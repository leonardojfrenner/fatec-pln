# 🎨 Frontend - Chat com LLM

Interface web simples e moderna para interagir com o modelo Qwen 3, inspirada no ChatGPT.

## 🚀 Como Usar

### 1. Iniciar a API (Backend)

Primeiro, certifique-se de que a API está rodando:

```powershell
# Na pasta raiz do projeto
python run_api.py
```

A API deve estar disponível em `http://localhost:8000`

### 2. Abrir o Frontend

Simplesmente abra o arquivo `index.html` no seu navegador:

- **Opção 1**: Clique duplo em `index.html`
- **Opção 2**: Arraste `index.html` para o navegador
- **Opção 3**: Abra via navegador (Ctrl+O)

## ✨ Funcionalidades

### 💬 Chat Interativo com Streaming
- Interface limpa similar ao ChatGPT
- Digite sua pergunta e pressione Enter (ou clique no botão)
- **⚡ Streaming em tempo real** - Veja o texto sendo gerado palavra por palavra!
- Cursor piscando mostra onde o modelo está gerando

### 🧠 Modo Pensamento em Tempo Real
- Checkbox "Mostrar pensamento do modelo"
- **Veja o raciocínio sendo gerado em tempo real**
- Acompanhe como o modelo pensa antes de responder
- Ative/desative a qualquer momento

### ⚙️ Configurações
- **Max Tokens**: Controle o tamanho da resposta (50-2048)
- Ajuste conforme necessário para respostas mais curtas ou longas

### 🎨 Interface
- Design moderno e responsivo
- Gradiente roxo elegante
- Animações suaves
- Loading indicator enquanto processa
- Scroll automático para últimas mensagens

## 🖼️ Preview

```
┌────────────────────────────────────┐
│     🤖 Chat com LLM                │
│     Powered by Qwen 3              │
├────────────────────────────────────┤
│                                    │
│  Você: Quem foi a primeira         │
│        pessoa no espaço?           │
│                                    │
│  🧠 Pensamento: Analisando...      │
│                                    │
│  🤖 Yuri Gagarin foi a primeira    │
│     pessoa no espaço em 1961...    │
│                                    │
├────────────────────────────────────┤
│ Digite sua pergunta aqui...    [↑] │
│ ☑ Mostrar pensamento  Tokens: 512 │
└────────────────────────────────────┘
```

## 🔧 Tecnologias

- **HTML5**: Estrutura
- **CSS3**: Estilização moderna com gradientes e animações
- **JavaScript Vanilla**: Sem frameworks, puro e simples
- **Fetch API**: Comunicação com backend

## 📁 Arquivos

```
front/
├── index.html    # Estrutura HTML
├── style.css     # Estilos e animações
├── script.js     # Lógica e comunicação com API
└── README.md     # Este arquivo
```

## 🎯 Atalhos de Teclado

- **Enter**: Enviar mensagem
- **Shift + Enter**: Nova linha no input

## ⚠️ Resolução de Problemas

### Erro: "Não foi possível conectar à API"

**Solução**: Verifique se a API está rodando:
```powershell
python run_api.py
```

### Erro de CORS

Se você ver erros de CORS no console do navegador, a API já está configurada com CORS habilitado. Certifique-se de que está acessando de:
- `file://` (abrindo arquivo local)
- `http://localhost`

### Respostas muito lentas

O modelo roda em CPU, então pode demorar alguns segundos. Considere:
- Reduzir o `max_tokens`
- Fazer perguntas mais diretas

## 💡 Dicas de Uso

1. **Perguntas Claras**: Seja específico para respostas melhores
2. **Max Tokens**: 
   - 100-200: Respostas curtas
   - 512: Respostas médias (padrão)
   - 1024-2048: Respostas longas
3. **Pensamento do Modelo**: Útil para entender o raciocínio
4. **Histórico**: Todas as mensagens ficam visíveis até você recarregar a página

## 🎨 Personalização

### Mudar Cores

Edite `style.css`:

```css
/* Gradiente principal */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Mude para suas cores favoritas */
background: linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 100%);
```

### Mudar URL da API

Edite `script.js`:

```javascript
const API_URL = 'http://localhost:8000';

// Para usar outra URL:
const API_URL = 'http://seu-servidor:porta';
```

## 📱 Responsivo

O frontend é totalmente responsivo e funciona em:
- 💻 Desktop
- 📱 Tablet
- 📱 Mobile

---

Desenvolvido com 💜 para interagir com LLMs

