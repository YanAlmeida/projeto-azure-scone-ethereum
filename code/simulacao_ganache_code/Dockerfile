# Usa a imagem oficial do Python 3.8 como base
FROM python:3.8-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de dependências e instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto do seu código-fonte para o diretório de trabalho dentro do container
COPY . .

# Expõe a porta 8000 para permitir a comunicação com o aplicativo
EXPOSE 8000

# Comando para rodar a aplicação usando o Gunicorn com workers Uvicorn
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--workers", "4", "--bind", "0.0.0.0:8000"]
