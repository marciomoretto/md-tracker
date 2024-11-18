# ======================= INSTRUÇÕES ==========================
# Este Makefile instala, configura e gerencia o Simple Search Provider
# sem exigir alterações na estrutura de diretórios existente.
#
# COMANDOS DISPONÍVEIS:
# 1. Instalar o script e serviços:
#    make all
#
# 2. Apenas instalar o script Python:
#    make install
#
# 3. Configurar o D-Bus:
#    make config
#
# 4. Configurar e iniciar o serviço Systemd:
#    make service
#
# 5. Desinstalar tudo:
#    make uninstall
#
# 6. Limpar arquivos temporários (se aplicável):
#    make clean
# ============================================================

# Variáveis de Configuração
INSTALL_DIR = /usr/local/bin
DBUS_DIR = /etc/dbus-1/services
SYSTEMD_USER_DIR = /lib/systemd/user
SERVICE_NAME = simple-search-provider
DBUS_SERVICE = org.example.SimpleSearch.service

# Alvos principais
.PHONY: all install config service clean uninstall

# Alvo principal
all: install config service

# Instalar o script Python
install:
	@echo "Instalando o script Python..."
	install -m 0755 simple_search_provider.py $(INSTALL_DIR)/$(SERVICE_NAME).py
	@echo "Script Python instalado com sucesso em $(INSTALL_DIR)/$(SERVICE_NAME).py"

# Configurar D-Bus
config:
	@echo "Configurando o serviço D-Bus..."
	install -m 0644 org.example.SimpleSearch.service $(DBUS_DIR)/$(DBUS_SERVICE)
	@echo "Serviço D-Bus configurado em $(DBUS_DIR)/$(DBUS_SERVICE)"

# Configurar e iniciar o serviço Systemd
service:
	@echo "Instalando e configurando o serviço Systemd..."
	install -m 0644 simple-search-provider.service $(SYSTEMD_USER_DIR)/$(SERVICE_NAME).service
	@echo "Recarregando configurações do systemd..."
	systemctl --user daemon-reload
	@echo "Habilitando e iniciando o serviço..."
	systemctl --user enable $(SERVICE_NAME).service
	systemctl --user start $(SERVICE_NAME).service
	@echo "Serviço Systemd configurado com sucesso!"

# Remover os arquivos instalados
uninstall:
	@echo "Parando e desabilitando o serviço Systemd..."
	systemctl --user stop $(SERVICE_NAME).service || true
	systemctl --user disable $(SERVICE_NAME).service || true
	@echo "Removendo arquivos instalados..."
	rm -f $(INSTALL_DIR)/$(SERVICE_NAME).py
	rm -f $(DBUS_DIR)/$(DBUS_SERVICE)
	rm -f $(SYSTEMD_USER_DIR)/$(SERVICE_NAME).service
	@echo "Recarregando configurações do systemd..."
	systemctl --user daemon-reload
	@echo "Desinstalação concluída!"

# Limpar arquivos temporários
clean:
	@echo "Limpando arquivos temporários..."
	@echo "Não há arquivos temporários para limpar neste projeto."
	@echo "Limpeza concluída!"
