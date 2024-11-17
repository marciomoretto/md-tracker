# MD Tracker
O MD Tracker é uma ferramenta para monitorar alterações em arquivos Markdown (.md) em tempo real e integrá-las ao Tracker3, gerando relações semânticas automáticas. Ele utiliza inotify para detecção de eventos e o Tracker3 para gerenciar metadados RDF.
## Recursos
* **Monitoramento Contínuo:** Detecta criação, modificação e exclusão de arquivos .md.
* **Integração com Tracker3:** Atualiza automaticamente relações RDF entre arquivos Markdown e assets relacionados.
* **Configuração Personalizável:** Escolha os diretórios monitorados e personalize o comportamento do programa.
* **Execução em Segundo Plano:** Funciona como um serviço systemd para monitoramento contínuo.
## Licença
Este projeto é licenciado sob a GPL 3.0. Leia o arquivo LICENSE para mais detalhes.
---
## Instalação

### 1. Instalar com .deb
Se você deseja uma instalação rápida e simples:
  1. Baixe o pacote .deb a partir da página de lançamentos.
  2. Instale o pacote:
  ```bash
  sudo dpkg -i md-tracker.deb
  ```
  3. Edite o arquivo de configuração:
  ```bash
  sudo nano /etc/md-tracker/config
  ```
    * Exemplo:
    ```bash
    PYTHON_SCRIPT=/usr/local/bin/md-tracker.py
    MONITORED_DIRS="/home/user/Documentos/Vault/pages /home/user/Documentos/Vault/journals"
    ```
  4. Inicie o serviço:
  ```bash
  sudo systemctl daemon-reload
  sudo systemctl enable md-tracker.service
  sudo systemctl start md-tracker.service
  ```
### 2. Clonar o Repositório
Se você prefere personalizar ou entender os detalhes do programa:
1. Clone este repositório:
```bash
git clone https://github.com/seu-usuario/md-tracker.git
cd md-tracker
```
2. Use o Makefile para configurar os arquivos e instalar as dependências:
```bash
make install
`` 
3. Edite o arquivo de configuração:
```bash
sudo nano /etc/md-tracker/config
```
  * Exemplo:
  ```bash
  PYTHON_SCRIPT=/usr/local/bin/md-tracker.py
  MONITORED_DIRS="/home/user/Documentos/Vault/pages /home/user/Documentos/Vault/journals"
  ```
4. Inicie o serviço:
```bash
sudo systemctl daemon-reload
sudo systemctl enable md-tracker.service
sudo systemctl start md-tracker.service
```
---
## Uso
### Verificar o Status do Serviço
* Verifique se o serviço está rodando:
```bash
sudo systemctl status md-tracker.service
```
### Visualizar Logs
* Verifique os eventos capturados:
```bash
sudo journalctl -u md-tracker.service
```
### Configuração Personalizada
Para alterar os diretórios monitorados ou o script Python utilizado, edite `/etc/md-tracker/config` e reinicie o serviço:
```bash
sudo systemctl restart md-tracker.service
```
---
### Como Funciona
1. Monitoramento de Eventos:
  * Detecta eventos de criação, modificação e exclusão em arquivos .md nos diretórios especificados.
2. Integração com Tracker3:
  * O script Python processa eventos para criar, atualizar ou remover relações RDF.
3. Serviço Systemd:
  * Executa o programa em segundo plano, reiniciando automaticamente em caso de falhas.
---
### Desinstalação
1. Parar e Desabilitar o Serviço:
```bash
sudo systemctl stop md-tracker.service
sudo systemctl disable md-tracker.service
```
2. Remover o Pacote:
```bash
sudo apt remove md-tracker
```
3. Remover Diretórios e Configurações:
```bash
sudo rm -rf /etc/md-tracker /usr/local/bin/md-tracker*
```
---
### Contribuições
Contribuições são bem-vindas! Siga as etapas abaixo para colaborar:
1. Faça um Fork deste repositório.
2. Crie uma branch para sua funcionalidade:
```bash
git checkout -b minha-nova-funcionalidade
```
3. Envie um pull request com as alterações propostas.
---
### Contato
Se você tiver dúvidas ou encontrar problemas, sinta-se à vontade para abrir uma Issue no GitHub.
