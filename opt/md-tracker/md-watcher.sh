#!/bin/bash

# Configura as variáveis de ambiente necessárias para o Tracker3
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus
export TRACKER3_HOME=$HOME
export TRACKER_SPARQL_BACKEND=bus

# Carrega o arquivo de configuração
CONFIG_FILE="/etc/md-watcher/config"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Erro: Arquivo de configuração não encontrado em $CONFIG_FILE"
    exit 1
fi
source "$CONFIG_FILE"

# Verifica se o script Python existe
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Erro: O script Python '$PYTHON_SCRIPT' não foi encontrado."
    exit 1
fi

# Verifica se os diretórios monitorados existem
for DIR in $MONITORED_DIRS; do
    if [ ! -d "$DIR" ]; then
        echo "Erro: O diretório '$DIR' não existe."
        exit 1
    fi
done

inotifywait -m -r -e create -e modify -e delete $MONITORED_DIRS |
while read -r path event file; do
    # Verifica se o arquivo tem extensão .md
    if [[ "$file" == *.md ]]; then
        # Determina o tipo de evento (converte para o formato do Python script)
        case $event in
            CREATE*) action="CREATE" ;;
            MODIFY*) action="MODIFY" ;;
            DELETE*) action="DELETE" ;;
            *) continue ;;
        esac

        # Caminho completo do arquivo
        full_path="$path$file"
        
        # Executa o script Python com o evento e o arquivo
        $PYTHON "$PYTHON_SCRIPT" "$full_path" "$action"
    fi
done
