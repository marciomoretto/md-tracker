#!/usr/bin/python3

import os
import re
import sys
import urllib.parse
import subprocess
from pathlib import Path


# --- Funções de Ajuda ---
def print_help():
    """
    Exibe o manual de uso do script.
    """
    help_text = """
Uso: python3 sync_and_cleanup_with_help.py CAMINHO_DO_DIRETORIO [OPÇÕES]

Sincroniza links de arquivos Markdown com o Tracker3, limpa links obsoletos e oferece opções de reindexação.

ARGUMENTOS:
  CAMINHO_DO_DIRETORIO        Caminho do diretório contendo arquivos .md.

OPÇÕES:
  --remove-all                Remove todas os links do Tracker3.
  --reindex                   Remove todas os links e reprocessa o diretório.
  --help, -h                  Exibe este manual de uso.

EXEMPLOS:
  1. Sincronizar e limpar links obsoletos:
     sync_tracker_logseq.py ~/Documentos/Vault/pages

  2. Remover todas os links:
     sync_tracker_logseq.py ~/Documentos/Vault/pages --remove-all

  3. Reindexar: remover todas os links e reprocessar o diretório:
     sync_tracker_logseq.py ~/Documentos/Vault/pages --reindex
"""
    print(help_text)


# --- Funções Principais ---
def get_links_and_files():
    """
    Recupera todos os links RDF e os arquivos associados do Tracker3.
    :return: Lista de tuplas (arquivo, link).
    """
    query = f"""
    SELECT ?file ?link WHERE {{
        ?file nie:relatedTo ?link .
    }}
    """
    try:
        result = subprocess.run(
            ["tracker3", "sparql", "--dbus-service=org.freedesktop.Tracker3.Miner.Files", "--query", query],
            stdout=subprocess.PIPE,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar consulta SPARQL: {e.stderr}")
        sys.exit(1)

    links_files = []
    for line in result.stdout.splitlines():
        if line.strip().startswith("file://"):
            parts = line.split(" ", 1)                   
            if len(parts) == 2:  # Garante que há exatamente dois elementos
                file_uri, link_uri = parts[1].split(",", 1)
                
                file_path = Path(urllib.parse.unquote(file_uri.replace("file://", "")))
                link_path = Path(urllib.parse.unquote(link_uri.replace("file://", "")))
                links_files.append((file_path, link_path))
    return links_files


def process_directory(directory):
    """
    Varre um diretório e executa o tracker_logseq.py para cada arquivo .md encontrado.

    :param directory: Caminho do diretório a ser processado.
    """
    directory_path = Path(directory)
    if not directory_path.is_dir():
        print(f"Erro: O caminho fornecido '{directory}' não é um diretório.")
        sys.exit(1)

    for file in directory_path.iterdir():
        if file.is_file() and file.suffix == ".md":
            print(f"Processando arquivo: {file}")
            try:
                subprocess.run(
                    ["tracker_logseq.py", str(file), "CREATE"],
                    check=True
                )
            except subprocess.CalledProcessError as e:
                print(f"Erro ao processar o arquivo {file}: {e}")


def cleanup_links(directory):
    """
    Remove links associadas a arquivos que não existem mais.

    :param directory: Caminho do diretório base para verificar os arquivos.
    """
    directory_path = Path(directory)
    if not directory_path.is_dir():
        print(f"Erro: O caminho fornecido '{directory}' não é um diretório.")
        sys.exit(1)

    links_files = get_links_and_files()
    for file_path, link_path in links_files:
#        decoded_keyword = urllib.parse.unquote(keyword)
        if not file_path.exists() or not str(file_path).startswith(str(directory_path)):
            print(f"Removendo link associado ao arquivo inexistente: {file_path} ↔ {link_path}")
            try:
                subprocess.run(
                    ["tracker_logseq.py", str(file_path), "DELETE"],
                    check=True
                )
            except subprocess.CalledProcessError as e:
                print(f"Erro ao processar DELETE para {file_path}: {e}")


def remove_all_links(directory):
    """
    Remove todos os links associados a arquivos no Tracker3.

    :param directory: Caminho base dos arquivos.
    """
    links_files = get_links_and_files()
    for file_path, _ in links_files:
        if file_path.suffix == ".md":
            try:
                print(file_path)
                subprocess.run(
                    ["tracker_logseq.py", str(file_path), "DELETE"],
                    check=True
                )
            except subprocess.CalledProcessError as e:
                print(f"Erro ao processar DELETE para {file_path}: {e}")


def sync_and_cleanup(directory, remove_all, reindex):
    """
    Combina as funções de sincronização e limpeza:
    - Remove todas os links (se remove_all for True).
    - Reindexa (se reindex for True).
    - Processa todos os arquivos .md no diretório (CREATE).
    - Remove links associadas a arquivos inexistentes (DELETE).
    """
    if remove_all:
        print("=== Removendo todos os links ===")
        remove_all_links(directory)
        print("=== Todas os links foram removidas ===")
        return

    if reindex:
        print("=== Reindexando: removendo todas os links e processando o diretório ===")
        remove_all_links(directory)
        process_directory(directory)
        print("=== Reindexação concluída ===")
        return

    print(f"=== Iniciando sincronização de arquivos ===")
    process_directory(directory)
    print("=== Sincronização concluída ===\n")

    print(f"=== Iniciando limpeza de links obsoletos ===")
    cleanup_links(directory)
    print("=== Limpeza concluída ===")


# --- Execução Principal ---
if __name__ == "__main__":
    if "--help" in sys.argv or "-h" in sys.argv:
        print_help()
        sys.exit(0)

    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)

    directory = sys.argv[1]
    remove_all = "--remove-all" in sys.argv
    reindex = "--reindex" in sys.argv

    sync_and_cleanup(directory, remove_all, reindex)
