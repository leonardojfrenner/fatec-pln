# Chat API com LLM

API REST para interagir com modelo de linguagem Qwen 3 usando FastAPI.

## Estrutura do Projeto

```
chat/
├── application/
│   └── app.py          # Rotas da API FastAPI
├── service/
│   └── llm.py          # Serviço do modelo LLM
├── run_api.py          # Script para iniciar a API
├── test_api.py         # Script para testar a API
└── README.md           # Este arquivo
```

## Como Executar

### 🐳 Opção 1: Com Docker (Recomendado)

**Simples e sem configuração:**

```powershell
# Construir e iniciar
docker-compose up -d

# Ver logs
docker-compose logs -f
```

A API estará disponível em: `http://localhost:8000`

📖 **Documentação completa:** [DOCKER.md](DOCKER.md)

### 🐍 Opção 2: Direto com Python

**1. Ativar o ambiente virtual:**
```powershell
.\venv\Scripts\activate
```

**2. Instalar dependências:**
```powershell
pip install -r requirements.txt
```

**3. Iniciar a API:**
```powershell
python run_api.py
```

A API estará disponível em: `http://localhost:8000`

### 📚 Acessar a documentação

Abra no navegador:
- **Documentação interativa (Swagger)**: http://localhost:8000/docs
- **Documentação alternativa (ReDoc)**: http://localhost:8000/redoc

## Endpoints da API

### GET `/`
Informações básicas da API

**Exemplo:**
```bash
curl http://localhost:8000/
```

### GET `/saude`
Verifica o status da API e do modelo

**Exemplo:**
```bash
curl http://localhost:8000/saude
```

**Response:**
```json
{
  "status": "saudavel",
  "modelo_carregado": true,
  "nome_modelo": "Qwen/Qwen3-0.6B"
}
```

### POST `/pergunta` 💬 (modo síncrono)

**Request Body:**
```json
{
  "question": "Quem foi a primeira pessoa no espaço?",
  "max_tokens": 256
}
```

**Response:**
```json
{
  "question": "Quem foi a primeira pessoa no espaço?",
  "thinking": "Analisando a história da exploração espacial...",
  "response": "Yuri Gagarin foi a primeira pessoa no espaço..."
}
```

### POST `/pergunta-stream` ⚡ (modo streaming)

**Request Body:** (igual ao síncrono)
```json
{
  "question": "Quem foi a primeira pessoa no espaço?",
  "max_tokens": 512
}
```

**Response:** Server-Sent Events (SSE)
```
data: {'type': 'thinking_chunk', 'content': 'Analisando'}
data: {'type': 'thinking_chunk', 'content': ' a'}
data: {'type': 'thinking_chunk', 'content': ' história...'}
data: {'type': 'thinking', 'content': 'Analisando a história...'}
data: {'type': 'response_chunk', 'content': 'Yuri'}
data: {'type': 'response_chunk', 'content': ' Gagarin'}
data: {'type': 'response_chunk', 'content': '...'}
data: {'type': 'done'}
```

**Tipos de eventos:**
- `thinking_chunk`: Pedaços do pensamento em tempo real
- `thinking`: Pensamento completo
- `response_chunk`: Pedaços da resposta em tempo real
- `response`: Resposta completa (opcional)
- `done`: Streaming finalizado

**Exemplo com curl:**
```bash
curl -X POST http://localhost:8000/pergunta \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"Quem foi a primeira pessoa no espaço?\"}"
```

**Exemplo com PowerShell:**
```powershell
$body = @{
    question = "Quem foi a primeira pessoa no espaço?"
    max_tokens = 512
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/pergunta" -Method Post -Body $body -ContentType "application/json"
```

**Exemplo com Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/pergunta",
    json={
        "question": "Quem foi a primeira pessoa no espaço?",
        "max_tokens": 512
    }
)

result = response.json()
print("🧠 Pensamento:", result["thinking"])
print("💬 Resposta:", result["response"])
```

### GET `/modelo`
Retorna informações sobre o modelo carregado

**Exemplo:**
```bash
curl http://localhost:8000/modelo
```

**Response:**
```json
{
  "nome_modelo": "Qwen/Qwen3-0.6B",
  "dispositivo": "cpu",
  "tipo_modelo": "Qwen2ForCausalLM"
}
```

## Tecnologias

- **FastAPI**: Framework web moderno e rápido
- **Transformers**: Biblioteca da Hugging Face para modelos de linguagem
- **Qwen 3 0.6B**: Modelo de linguagem compacto com modo de pensamento
- **Uvicorn**: Servidor ASGI de alta performance

## Recursos

- ✅ Modelo muito leve (~600MB) que roda em CPU
- ✅ Modo "thinking" mostra o raciocínio do modelo
- ✅ Documentação automática com Swagger
- ✅ Validação de dados com Pydantic
- ✅ API REST simples e rápida

## Notas

- O modelo é carregado na inicialização da API (pode demorar alguns segundos)
- O modelo usa CPU (pode levar alguns segundos para perguntas complexas)
- O modo "thinking" mostra o raciocínio interno do modelo antes da resposta

## 📊 Sobre o Modelo Qwen3-0.6B

O **Qwen/Qwen3-0.6B** é um modelo muito compacto de 600MB:

**Vantagens:**
- ✅ Muito rápido - gera respostas em segundos
- ✅ Roda em CPU com pouca RAM (4GB suficiente)
- ✅ Pequeno e fácil de baixar
- ✅ Tem modo "thinking" integrado

**Limitações:**
- ⚠️ Conhecimento limitado (modelo muito pequeno)
- ⚠️ Pode dar respostas imprecisas ou confusas em português
- ⚠️ Melhor em inglês que em português
- ⚠️ Não é adequado para perguntas complexas

**Para melhores resultados:**

1. **Faça perguntas simples e diretas**
   - ✅ "Quem foi Yuri Gagarin?"
   - ❌ "Explique detalhadamente a história da exploração espacial"

2. **Use perguntas em inglês quando possível**
   - O modelo foi treinado principalmente em inglês

3. **Considere usar modelos maiores:**
   - Qwen/Qwen2.5-7B (melhor qualidade, precisa de mais RAM)
   - Modelos da família Llama
   - APIs comerciais (OpenAI, Anthropic, Groq)

### Como trocar o modelo

Para usar um modelo diferente, edite `service/llm.py`:

```python
# Linha 9 - Trocar o modelo
def __init__(self, model_name: str = "Qwen/Qwen3-0.6B"):  # ← Atual (0.6B)
    
# Opções de modelos:
# Modelo pequeno (mais rápido, menos preciso) - ATUAL
def __init__(self, model_name: str = "Qwen/Qwen3-0.6B"):  # 0.6B - muito rápido ✅
# Modelo médio (balanceado, mais preciso)
def __init__(self, model_name: str = "microsoft/phi-2"):  # 2.7B - melhor qualidade
# Modelo médio-grande
def __init__(self, model_name: str = "Qwen/Qwen2.5-1.5B"):  # 1.5B
# Modelo grande (melhor qualidade, precisa GPU ou muita RAM)
def __init__(self, model_name: str = "Qwen/Qwen2.5-7B"):  # 7B - melhor qualidade
```

**Nota:** Modelos maiores precisam de mais RAM e são mais lentos na CPU.

**Recomendações por RAM:**
- 4-8GB RAM: `Qwen/Qwen3-0.6B` (atual ✅ - mais rápido)
- 8-16GB RAM: `microsoft/phi-2` (mais preciso)
- 16GB+ RAM: `Qwen/Qwen2.5-7B` (melhor qualidade)
