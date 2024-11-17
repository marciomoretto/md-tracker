#!/usr/bin/python3

import os
import re
import sys
import urllib.parse
import subprocess
import unicodedata
from pathlib import Path
import argparse

# Caminho para a pasta de assets
ASSETS_PATH = os.path.expanduser("~/Documentos/Vault/assets")

def show_help():
    print("Uso: python script.py CAMINHO_DO_ARQUIVO EVENTO")
    print("\nSincroniza tags para assets mencionados em arquivos .md no LogSeq.")
    print("\nArgumentos:")
    print("  CAMINHO_DO_ARQUIVO   Caminho para o arquivo .md da página do LogSeq.")
    print("  EVENTO               Tipo de evento (CREATE, MODIFY, DELETE).")
    print("\nExemplos de uso:")
    print("  tracker_logseq.py ~/Documentos/LogSeqVault/minha_pagina.md MODIFY")
    sys.exit()

def urlencode(text):
    return urllib.parse.quote(text, safe='')

def ensure_information_element(file_path):
    """
    Garante que o arquivo seja registrado como nie:InformationElement.
    """
    file_uri = "file://" + urlencode(str(file_path))

    # Verifica e define o tipo como nie:InformationElement, se necessário
    subprocess.run([
        "tracker3", "sparql", "--update", "--dbus-service=org.freedesktop.Tracker3.Miner.Files",
        "--query", f"""
        INSERT {{
            <{file_uri}> a nie:InformationElement
        }} WHERE {{
            FILTER NOT EXISTS {{
                <{file_uri}> a nie:InformationElement
            }}
        }}
        """
    ], check=True, encoding="utf-8")

def add_link(file_path, asset_path):
    file_uri = "file://" + urlencode(str(file_path))
    asset_uri = "file://" + urlencode(str(asset_path))

    print(f"DEBUG: Criando link simétrico RDF -> {file_uri} ↔ {asset_uri}")

    # Garante que o arquivo Markdown é identificado como nie:InformationElement
    ensure_information_element(file_path)

    # Garante que o asset é identificado como nie:InformationElement
    ensure_information_element(asset_path)

    # Adiciona link do Markdown para o Asset
    subprocess.run([
        "tracker3", "sparql", "--update", "--dbus-service=org.freedesktop.Tracker3.Miner.Files",
        "--query", f"""
        INSERT {{
            <{file_uri}> nie:relatedTo <{asset_uri}>
        }} WHERE {{
            FILTER NOT EXISTS {{
                <{file_uri}> nie:relatedTo <{asset_uri}>
            }}
        }}
        """
    ], check=True, encoding="utf-8")

    # Adiciona link do Asset para o Markdown
    subprocess.run([
        "tracker3", "sparql", "--update", "--dbus-service=org.freedesktop.Tracker3.Miner.Files",
        "--query", f"""
        INSERT {{
            <{asset_uri}> nie:relatedTo <{file_uri}>
        }} WHERE {{
            FILTER NOT EXISTS {{
                <{asset_uri}> nie:relatedTo <{file_uri}>
            }}
        }}
        """
    ], check=True, encoding="utf-8")

def remove_link(file_path, asset_path):
    file_uri = "file://" + urlencode(str(file_path))
    asset_uri = "file://" + urlencode(str(asset_path))

    print(f"DEBUG: Removendo link simétrico RDF -> {file_uri} ↔ {asset_uri}")

    try:
        # Remove link do Markdown para o Asset
        subprocess.run([
            "tracker3", "sparql", "--update", "--dbus-service=org.freedesktop.Tracker3.Miner.Files",
            "--query", f"""
            DELETE {{
                <{file_uri}> nie:relatedTo <{asset_uri}>
            }} WHERE {{
                <{file_uri}> nie:relatedTo <{asset_uri}>
            }}
            """
        ], check=True, encoding="utf-8")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao remover link de {file_uri} para {asset_uri}: {e}")

    try:
        # Remove link do Asset para o Markdown
        subprocess.run([
            "tracker3", "sparql", "--update", "--dbus-service=org.freedesktop.Tracker3.Miner.Files",
            "--query", f"""
            DELETE {{
                <{asset_uri}> nie:relatedTo <{file_uri}>
            }} WHERE {{
                <{asset_uri}> nie:relatedTo <{file_uri}>
            }}
            """
        ], check=True, encoding="utf-8")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao remover link de {asset_uri} para {file_uri}: {e}")

def search_by_links(page_file):
    page_uri = "file://" + urlencode(str(page_file))
    result = subprocess.run([
        "tracker3", "sparql", "--dbus-service=org.freedesktop.Tracker3.Miner.Files",
        "--query", f"""
        SELECT ?asset WHERE {{
            <{page_uri}> nie:relatedTo ?asset
        }}
        """
    ], stdout=subprocess.PIPE, text=True, check=True)
    links = re.findall(r'file://[^\s]+', result.stdout)
    return [Path(urllib.parse.unquote(link.replace("file://", ""))) for link in links]

def sync_links(page_file, event):
    page_name = Path(page_file).stem

    # Se o evento for "DELETE", removemos todos os links associados
    if event == "DELETE":
        for file_path in search_by_links(page_file):
            remove_link(page_file, file_path)
            print(f"Removido link entre {page_file} e {file_path} (arquivo {page_file} foi removido)")
        return

    # Se o evento for "MODIFY" ou "CREATE", sincronizar links
    assets_mencionados = {}
    md_referenciados = {}

    with open(page_file, 'r', encoding='utf-8') as f:
        for line in f:
            # Captura assets mencionados no formato ../assets/arquivo.ext
            match_asset = re.search(r'\.\./assets/(.*?)\)(?=\s|$)', line)
            if match_asset:
                asset_file = match_asset.group(1)
                asset_path = Path(ASSETS_PATH) / asset_file
                assets_mencionados[asset_path] = 1

            # Captura referências a outros arquivos Markdown no formato [[nome_da_pagina]]
            match_md_brackets = re.findall(r'\[\[(.*?)\]\]', line)
            if match_md_brackets:
                for ref in match_md_brackets:
                    referenced_file = Path(page_file).parent / f"{ref}.md"
                    if referenced_file.exists():
                        md_referenciados[referenced_file] = 1

            # Captura referências a outros arquivos Markdown no formato #nome_da_pagina
            match_md_hash = re.findall(r'#([a-zA-Z0-9_]+)', line)
            if match_md_hash:
                for ref in match_md_hash:
                    referenced_file = Path(page_file).parent / f"{ref}.md"
                    if referenced_file.exists():
                        md_referenciados[referenced_file] = 1

    # Recupera os links RDF já existentes
    links_existentes = {Path(file_path): 1 for file_path in search_by_links(page_file)}

    # Função para adicionar links de uma lista ao arquivo principal
    def add_missing_links(referenced_items):
        for file_path in referenced_items.keys():
            if file_path not in links_existentes:
                add_link(page_file, file_path)
                print(f"Criado link simétrico RDF entre {page_file} e {file_path}")

    # Adiciona links para assets e arquivos Markdown referenciados
    add_missing_links(assets_mencionados)
    add_missing_links(md_referenciados)

    # Remove links que estão registrados, mas não são mais referenciados
    for file_path in links_existentes.keys():
        if file_path not in assets_mencionados and file_path not in md_referenciados:
            # Verifica se o arquivo ainda aponta para a página atual
            backlinks = search_by_links(file_path)
            if Path(page_file) not in backlinks:
                remove_link(page_file, file_path)
                print(f"Removido link simétrico RDF entre {page_file} e {file_path}")
            else:
                print(f"Link de {file_path} para {page_file} ainda existe; não será removido.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sincroniza tags para assets mencionados em arquivos .md no LogSeq.")
    parser.add_argument("page_file", help="Caminho para o arquivo .md da página do LogSeq.")
    parser.add_argument("event", choices=["CREATE", "MODIFY", "DELETE"], help="Tipo de evento.")

    args = parser.parse_args()
    page_file = args.page_file
    event = args.event

    sync_links(page_file, event)   
