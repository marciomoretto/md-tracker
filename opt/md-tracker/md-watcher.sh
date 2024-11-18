#!/bin/bash

# Configura as variáveis de ambiente necessárias para o Tracker3
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus
export TRACKER3_HOME=$HOME
export TRACKER_SPARQL_BACKEND=bus

# Local do arquivo de configuração do usuário
CONFIG_FILE="$HOME/.config/md-watcher/config"

# Verifica se o arquivo de configuração existe
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Erro: Arquivo de configuração não encontrado em $CONFIG_FILE"
    echo "Por favor, crie o arquivo com o seguinte conteúdo:"
    cat <<EOF
# Caminho para o script Python
PYTHON_SCRIPT=/opt/md-tracker/md-tracker.py

# Lista de diretórios monitorados
MONITORED_DIRS="\$HOME/Documentos/Vault/pages \$HOME/Documentos/Vault/journals"
EOF
    exit 1
fi

# Carrega o arquivo de configuração
source "$CONFIG_FILE"

# Verifica se o inotifywait está instalado
if ! command -v inotifywait &> /dev/null; then
    echo "Erro: 'inotifywait' não está instalado. Instale o pacote inotify-tools."
    exit 1
fi

# Verifica se os diretórios monitorados existem
for DIR in $MONITORED_DIRS; do
    if [ ! -d "$DIR" ]; then
        echo "Erro: O diretório '$DIR' não existe."
        exit 1
    fi
done

while true; do

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

            # Log do evento
            echo "[$(date)] Evento: $action no arquivo: $full_path" >> "$HOME/.config/md-watcher/events.log"
            
            # Executa o script Python com o evento e o arquivo
            /opt/md-tracker/env/bin/python3 /opt/md-tracker/md-tracker.py "$full_path" "$action"
        fi
    done
done