# DLI Chat - Interface Django com MongoDB

Sistema de chat com múltiplas conversas usando Django e MongoDB.

## 📋 Estrutura do Banco de Dados

### MongoDB - Collection: `chats`

Cada documento na collection `chats` representa uma conversa completa:

```json
{
  "_id": "ObjectId",
  "titulo": "Chat - Primeira pergunta...",
  "criado_em": "2025-10-22T10:30:00",
  "atualizado_em": "2025-10-22T10:35:00",
  "mensagens": [
    {
      "pergunta": "Qual é a capital do Brasil?",
      "resposta": "A capital do Brasil é Brasília.",
      "timestamp": "2025-10-22T10:30:00"
    },
    {
      "pergunta": "E do Japão?",
      "resposta": "A capital do Japão é Tóquio.",
      "timestamp": "2025-10-22T10:35:00"
    }
  ]
}
```

## 📋 Pré-requisitos

- **Python 3.8+**
- **Docker** (para MongoDB)
- **Git**

## 🚀 Como Usar

### 1. Configure o MongoDB

#### Instalar o MongoDB via Docker:
```bash
# Baixar a imagem oficial do MongoDB
docker pull mongodb/mongodb-community-server:7.0-ubi8

# Executar o container MongoDB
docker run -d \
  --name meu-mongodb \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=admin \
  mongodb/mongodb-community-server:7.0-ubi8
```

#### Verificar se o MongoDB está rodando:
```bash
docker exec -it meu-mongodb mongosh -u admin -p admin --authenticationDatabase admin
```

### 2. Ative o ambiente virtual

```bash
# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instale as dependências

```bash
# IMPORTANTE: Use o -r para instalar do arquivo requirements.txt
pip install -r requirements.txt

# Ou se preferir, instale individualmente:
# pip install Django==5.2.7
# pip install pymongo==4.15.3
# pip install dnspython==2.8.0
# pip install django-cors-headers==4.9.0
# pip install requests==2.32.5
```

### 4. Execute o servidor

```bash
# IMPORTANTE: Use a porta 8001 pois a porta 8000 é usada pela API FastAPI
python manage.py runserver 8001
```

> **⚠️ ATENÇÃO:** Se você tem uma API FastAPI rodando na porta 8000, o Django **DEVE** rodar na porta 8001 para evitar conflitos!

### 5. Acesse o sistema

Abra seu navegador em: `http://localhost:8001`

> **Nota:** Se sua API FastAPI não estiver rodando, você pode usar a porta 8000. Mas o recomendado é sempre usar 8001 para o Django.

## 🌐 Arquitetura de Portas

O projeto utiliza 3 portas diferentes:

| Serviço | Porta | URL | Descrição |
|---------|-------|-----|-----------|
| **API FastAPI (Modelo LLM)** | 8000 | `http://localhost:8000` | API do modelo de IA (Docker) |
| **Django Interface** | 8001 | `http://localhost:8001` | Interface web do chat |
| **MongoDB** | 27017 | `localhost:27017` | Banco de dados (Docker) |

### Fluxo de Comunicação:
```
Navegador (8001) → Django (8001) → API FastAPI (8000) → Modelo LLM
                       ↓
                  MongoDB (27017)
```

## 📡 API Endpoints

### Perguntas

- **POST** `/pergunta`
  - Envia uma pergunta e recebe resposta do modelo
  - Body: `{ "question": "...", "chat_id": "..." (opcional), "max_tokens": 256 }`
  - Retorna: `{ "response": "...", "chat_id": "..." }`

### Gerenciamento de Chats

- **GET** `/chats/` - Lista todos os chats
- **POST** `/chats/criar` - Cria um novo chat
  - Body: `{ "titulo": "Novo Chat" }`
- **GET** `/chats/<chat_id>` - Obtém um chat específico
- **DELETE** `/chats/<chat_id>/deletar` - Deleta um chat
- **PUT** `/chats/<chat_id>/titulo` - Atualiza título do chat
  - Body: `{ "titulo": "Novo título" }`

## 🔧 Configuração do MongoDB

### Container MongoDB
- **Imagem:** `mongodb/mongodb-community-server:7.0-ubi8`
- **Usuário:** `admin`
- **Senha:** `admin` (definida para facilitar desenvolvimento)
- **Porta:** `27017`
- **Nome do container:** `meu-mongodb`

### Configuração no código
As configurações do MongoDB estão em `app/models.py`:

```python
def get_db():
    client = MongoClient(
        host='localhost',
        port=27017,
        username='admin',
        password='admin',
        authSource='admin'
    )
    return client['chat_database']
```

### Comandos úteis do MongoDB
```bash
# Conectar ao MongoDB
docker exec -it meu-mongodb mongosh -u admin -p admin --authenticationDatabase admin

# Ver bancos de dados
show dbs

# Usar o banco do projeto
use chat_database

# Ver coleções
show collections

# Ver todos os chats
db.chats.find().pretty()

# Contar chats
db.chats.countDocuments()
```

## 💡 Próximos Passos

Você precisará integrar seu modelo de IA no arquivo `app/views.py`, na função `pergunta()`:

```python
# TODO: Aqui você vai integrar com seu modelo de IA
# Por enquanto, vou simular uma resposta
resposta_modelo = f"Resposta simulada para: {pergunta_usuario}"
```

Substitua essa linha pela chamada ao seu modelo de IA real.

## 🎨 Funcionalidades do Frontend

- ✅ Sidebar com lista de todos os chats
- ✅ Criar novo chat
- ✅ Carregar chat existente
- ✅ Deletar chat
- ✅ Visualizar histórico completo de mensagens
- ✅ Interface moderna e responsiva
- ✅ Suporte a Markdown nas respostas do bot

## 📂 Estrutura do Projeto

```
django-interface/
├── app/
│   ├── models.py          # ChatManager com funções MongoDB
│   ├── views.py           # Views da API
│   ├── urls.py            # Rotas da aplicação
│   └── templates/
│       └── index.html     # Interface do chat
├── chat/
│   └── settings.py        # Configurações do Django
├── manage.py
├── requirements.txt
└── README.md
```

## 🛠️ Tecnologias

- **Backend**: Django 5.2.7
- **Banco de Dados**: MongoDB 7.0 (via PyMongo)
- **Container**: Docker (mongodb/mongodb-community-server:7.0-ubi8)
- **Frontend**: HTML, CSS, JavaScript vanilla
- **Markdown**: Marked.js
- **Ícones**: Font Awesome 6.0

## 🔧 Troubleshooting

### Problemas comuns:

#### MongoDB não conecta:
```bash
# Verificar se o container está rodando
docker ps | grep mongodb

# Reiniciar o container se necessário
docker restart meu-mongodb

# Verificar logs
docker logs meu-mongodb
```

#### Django não encontra o MongoDB:
- Verifique se o MongoDB está rodando na porta 27017
- Confirme as credenciais: usuário `admin`, senha `admin`
- Teste a conexão: `docker exec -it meu-mongodb mongosh -u admin -p admin --authenticationDatabase admin`

#### ⚠️ Erro de porta 8000 (MUITO IMPORTANTE):
Se você vê este erro ao iniciar o Django:
```
Error: That port is already in use.
```

**Solução:**
```bash
# PARE o servidor Django (Ctrl+C)
# Inicie novamente na porta 8001
python manage.py runserver 8001
```

**Por quê?** Sua API FastAPI (modelo LLM) já está usando a porta 8000. O Django **PRECISA** rodar na porta 8001.

**Acesse:** `http://localhost:8001` (não `http://localhost:8000`)

