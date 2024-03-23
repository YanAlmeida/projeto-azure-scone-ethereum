# Usar uma imagem base oficial do Python
FROM python:3.8-slim

# Instalar sshpass
RUN apt-get update && \
    apt-get install -y openssh-client bc && \
    rm -rf /var/lib/apt/lists/*

# Configurar o diretório de trabalho
WORKDIR /app

# Copiar as chaves SSH para o diretório .ssh do usuário root no contêiner
# Substitua `id_rsa` e `id_rsa.pub` pelos caminhos para suas chaves SSH
COPY id_rsa /root/.ssh/id_rsa
COPY id_rsa.pub /root/.ssh/id_rsa.pub

# Garantir permissões adequadas para as chaves
RUN chmod 600 /root/.ssh/id_rsa && \
    chmod 644 /root/.ssh/id_rsa.pub

# Copiar o script shell para o diretório de trabalho
COPY requirements.txt /app/requirements.txt

RUN pip3 install -r requirements.txt

RUN pip3 install locust

COPY automacao.sh /app/automacao.sh
COPY coletar_dados.py /app/coletar_dados.py
COPY main.py /app/main.py
COPY smart_contract.py /app/smart_contract.py

# Dar permissão de execução ao script
RUN chmod +x /app/automacao.sh

# Comando para executar o script quando o contêiner iniciar
CMD ["/app/automacao.sh"]
