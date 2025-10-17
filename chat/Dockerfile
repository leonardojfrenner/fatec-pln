# Imagem base com Python 3.11
FROM python:3.11-slim

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema necessárias
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivo de requisitos primeiro (para cache de layers)
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar apenas os arquivos necessários do backend
COPY application/ ./application/
COPY service/ ./service/
COPY run_api.py .

# Criar diretório para cache do Hugging Face
RUN mkdir -p /root/.cache/huggingface

# Expor porta da API
EXPOSE 8000

# Variável de ambiente para o token do Hugging Face (opcional)
ENV HF_TOKEN=""

# Variável de ambiente para usar CPU
ENV CUDA_VISIBLE_DEVICES=""

# Comando para iniciar a API
CMD ["python", "run_api.py"]

