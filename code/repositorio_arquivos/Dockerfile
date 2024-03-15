# Use a imagem oficial do Nginx
FROM nginx:latest

# Remova o arquivo de configuração padrão do Nginx
RUN rm /etc/nginx/conf.d/default.conf

# Adicione seu arquivo de configuração personalizado
COPY nginx.conf /etc/nginx/conf.d

# Copie os arquivos que você deseja disponibilizar para o diretório dentro do container
# Supondo que você tenha uma pasta 'files' no mesmo diretório do seu Dockerfile
COPY ./files /usr/share/nginx/html

# Exponha a porta 80
EXPOSE 80
