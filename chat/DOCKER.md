# 🐳 Docker - Chat API com LLM

Instruções para rodar a API usando Docker.

## 📋 Pré-requisitos

- Docker instalado ([Download](https://www.docker.com/get-started))
- Docker Compose instalado (já vem com Docker Desktop)
- Pelo menos 8GB de RAM disponível

## 🚀 Como Usar

### Opção 1: Docker Compose (Recomendado)

**1. Construir e iniciar:**
```powershell
docker-compose up -d
```

**2. Ver logs:**
```powershell
docker-compose logs -f
```

**3. Parar:**
```powershell
docker-compose down
```

**4. Parar e remover volumes:**
```powershell
docker-compose down -v
```

### Opção 2: Docker Manual

**1. Construir a imagem:**
```powershell
docker build -t chat-llm-api .
```

**2. Executar o container:**
```powershell
docker run -d \
  --name chat-llm-api \
  -p 8000:8000 \
  -v huggingface-cache:/root/.cache/huggingface \
  chat-llm-api
```

**3. Ver logs:**
```powershell
docker logs -f chat-llm-api
```

**4. Parar e remover:**
```powershell
docker stop chat-llm-api
docker rm chat-llm-api
```

## 🔧 Configurações

### Token do Hugging Face

Se o modelo precisar de autenticação, crie um arquivo `.env`:

```env
HF_TOKEN=seu_token_aqui
```

Depois execute:
```powershell
docker-compose up -d
```

### Ajustar Recursos

Edite `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '4'      # Número de CPUs
      memory: 8G     # RAM máxima
```

## 📊 Verificar Status

### API está rodando?
```powershell
curl http://localhost:8000/saude
```

Ou abra no navegador: http://localhost:8000/docs

### Ver uso de recursos:
```powershell
docker stats chat-llm-api
```

## 🎯 Usar com Frontend

O frontend (`front/index.html`) já está configurado para conectar em `http://localhost:8000`.

Basta:
1. Iniciar a API com Docker: `docker-compose up -d`
2. Abrir `front/index.html` no navegador

## 🔄 Atualizar

Após fazer mudanças no código ou requirements.txt:

```powershell
# Parar containers
docker-compose down

# Reconstruir a imagem (sem cache)
docker-compose build --no-cache

# Reiniciar
docker-compose up -d
```

**Atualização rápida (sem rebuild):**
```powershell
docker-compose restart
```

## 🗑️ Limpar Tudo

```powershell
# Parar e remover containers, volumes e imagens
docker-compose down -v
docker rmi chat-llm-api
```

## 📝 Estrutura do Container

```
/app/
├── application/
│   └── app.py
├── service/
│   └── llm.py
└── run_api.py
```

## ⚠️ Notas Importantes

1. **Primeira execução demora**: O modelo precisa ser baixado (~600MB)
2. **Cache persistente**: O modelo fica salvo em um volume Docker
3. **Somente CPU**: O container usa apenas CPU, não GPU
4. **Memória**: Recomendado 8GB RAM mínimo
5. **Porta 8000**: Certifique-se que está livre

## 🐛 Troubleshooting

### Erro: "data did not match any variant of untagged enum ModelWrapper"

**Causa:** Incompatibilidade entre versão do transformers e o modelo.

**Solução:**
```powershell
# 1. Parar e remover tudo
docker-compose down -v

# 2. Reconstruir SEM cache
docker-compose build --no-cache

# 3. Iniciar novamente
docker-compose up -d
```

### Porta 8000 já em uso
```powershell
# Verificar o que está usando a porta
netstat -ano | findstr :8000

# Mudar a porta no docker-compose.yml
ports:
  - "8080:8000"  # Usa 8080 ao invés de 8000
```

### Container para imediatamente
```powershell
# Ver logs completos
docker-compose logs

# Ver logs em tempo real
docker-compose logs -f
```

### Modelo não baixa
```powershell
# Verificar internet e espaço em disco
docker exec -it chat-llm-api df -h

# Verificar se o container está rodando
docker ps -a
```

### Erro de memória / Container travando
```powershell
# Aumentar limites no docker-compose.yml
deploy:
  resources:
    limits:
      memory: 12G  # Aumentar de 8G para 12G
```

### Limpar cache e recomeçar
```powershell
docker-compose down -v
docker system prune -a --volumes
docker-compose up -d
```

## 🎨 Customizar Modelo

Para trocar o modelo, edite `service/llm.py` antes de construir a imagem:

```python
def __init__(self, model_name: str = "Qwen/Qwen3-0.6B"):  # Mudar aqui
```

Depois reconstrua:
```powershell
docker-compose build --no-cache
docker-compose up -d
```

## 📦 Publicar Imagem no Docker Hub

### Método 1: Script Automático (Fácil)

```powershell
# Executar script de deploy
.\deploy.ps1
```

O script faz automaticamente:
- Login no Docker Hub
- Build da imagem
- Tag com versão
- Push para Docker Hub

### Método 2: Manual

```powershell
# 1. Login no Docker Hub
docker login
# Usuário: leonardorennerdev
# Senha: [sua senha]

# 2. Tag da imagem
docker tag chat-llm-api leonardorennerdev/chat-llm-api:latest
docker tag chat-llm-api leonardorennerdev/chat-llm-api:1.0.0

# 3. Publicar
docker push leonardorennerdev/chat-llm-api:latest
docker push leonardorennerdev/chat-llm-api:1.0.0
```

### Usar a imagem publicada

Em qualquer máquina com Docker:

```powershell
# Baixar e executar
docker run -d -p 8000:8000 leonardorennerdev/chat-llm-api:latest

# Ou com docker-compose, crie um arquivo:
```

**docker-compose.yml:**
```yaml
services:
  api:
    image: leonardorennerdev/chat-llm-api:latest
    ports:
      - "8000:8000"
    volumes:
      - huggingface-cache:/root/.cache/huggingface

volumes:
  huggingface-cache:
```

Depois execute:
```powershell
docker-compose up -d
```

---

**Pronto!** Sua API está rodando em container e publicada no Docker Hub! 🎉

**Link da sua imagem:** https://hub.docker.com/r/leonardorennerdev/chat-llm-api

