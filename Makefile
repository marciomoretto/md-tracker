# ================== Instruções ==================
# Este Makefile automatiza a criação, instalação e remoção do pacote md-tracker.
#
# Comandos disponíveis:
#
# 1. Construir o pacote .deb:
#    make build
#
# 2. Instalar o pacote:
#    make install
#
# 3. Desinstalar o pacote:
#    make uninstall
#
# 4. Limpar arquivos temporários:
#    make clean

# Variáveis de configuração
PACKAGE_NAME = md-tracker
BUILD_DIR = $(PACKAGE_NAME)
DEB_PACKAGE = $(PACKAGE_NAME).deb

# Caminhos no pacote
BIN_DIR = $(BUILD_DIR)/usr/local/bin
CONFIG_DIR = $(BUILD_DIR)/etc/md-tracker
SERVICE_DIR = $(BUILD_DIR)/lib/systemd/system

# Alvos principais
.PHONY: all build install clean uninstall

# Alvo principal
all: build

# Constrói o pacote .deb
build:
	@echo "Criando estrutura do pacote..."
	# Cria diretórios necessários
	mkdir -p $(BIN_DIR)
	mkdir -p $(CONFIG_DIR)
	mkdir -p $(SERVICE_DIR)
	mkdir -p $(BUILD_DIR)/DEBIAN

	# Copia os arquivos do projeto
	install -m 0755 md-watcher.sh $(BIN_DIR)/
	install -m 0755 md-tracker.py $(BIN_DIR)/
	install -m 0644 etc/md-tracker/config.example $(CONFIG_DIR)/config
	install -m 0644 lib/systemd/system/md-tracker.service $(SERVICE_DIR)/

	# Copia arquivos de controle do DEBIAN
	install -m 0644 DEBIAN/control $(BUILD_DIR)/DEBIAN/
	install -m 0755 DEBIAN/postinst $(BUILD_DIR)/DEBIAN/
	install -m 
