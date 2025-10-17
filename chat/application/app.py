from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import sys
import os

# Adicionar o diretório raiz ao path para importar o serviço
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from service.llm import LLMService

# Criar a aplicação FastAPI
app = FastAPI(
    title="Chat API com LLM",
    description="API para interagir com modelo de linguagem Qwen",
    version="1.0.0"
)

# Configurar CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique os domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic para request/response
class QuestionRequest(BaseModel):
    question: str
    max_tokens: Optional[int] = 256
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "Quem foi a primeira pessoa no espaço?",
                "max_tokens": 256
            }
        }

class QuestionResponse(BaseModel):
    question: str
    thinking: str
    response: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "Quem foi a primeira pessoa no espaço?",
                "thinking": "Processo de raciocínio do modelo...",
                "response": "Yuri Gagarin foi a primeira pessoa no espaço..."
            }
        }

# Inicializar o serviço LLM (carrega o modelo na inicialização)
print("Inicializando serviço LLM...")
llm_service = LLMService()
print("Serviço LLM pronto!")

# Rotas da API

@app.get("/")
async def root():
    """Rota raiz - informações básicas da API"""
    return {
        "mensagem": "Chat API com LLM",
        "versao": "1.0.0",
        "modelo": llm_service.model_name,
        "endpoints": {
            "saude": "/saude (GET) - Verifica status da API",
            "pergunta": "/pergunta (POST) - Envia pergunta ao modelo",
            "modelo": "/modelo (GET) - Informações do modelo",
            "documentacao": "/docs - Documentação interativa"
        }
    }

@app.get("/saude")
async def verificar_saude():
    """Verifica se a API e o modelo estão funcionando"""
    try:
        is_loaded = llm_service.model is not None and llm_service.tokenizer is not None
        return {
            "status": "saudavel" if is_loaded else "indisponivel",
            "modelo_carregado": is_loaded,
            "nome_modelo": llm_service.model_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao verificar saúde: {str(e)}")

@app.post("/pergunta", response_model=QuestionResponse)
async def enviar_pergunta(request: QuestionRequest):
    """
    Envia uma pergunta ao modelo e retorna a resposta (modo síncrono)
    
    - **question**: A pergunta que você quer fazer ao modelo
    - **max_tokens**: Número máximo de tokens na resposta (opcional, padrão: 512)
    """
    try:
        # Validar entrada
        if not request.question or request.question.strip() == "":
            raise HTTPException(status_code=400, detail="A pergunta não pode estar vazia")
        
        if request.max_tokens < 1 or request.max_tokens > 1024:
            raise HTTPException(status_code=400, detail="max_tokens deve estar entre 1 e 1024")
        
        # Gerar resposta
        result = llm_service.generate_response(
            prompt=request.question,
            max_tokens=request.max_tokens
        )
        
        return QuestionResponse(
            question=request.question,
            thinking=result["thinking"],
            response=result["response"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar pergunta: {str(e)}")

@app.post("/pergunta-stream")
async def enviar_pergunta_stream(request: QuestionRequest):
    """
    Envia uma pergunta ao modelo e retorna a resposta com streaming em tempo real
    
    - **question**: A pergunta que você quer fazer ao modelo
    - **max_tokens**: Número máximo de tokens na resposta (opcional, padrão: 512)
    
    Retorna eventos SSE (Server-Sent Events) com:
    - thinking_chunk: Pedaços do pensamento do modelo
    - thinking: Pensamento completo
    - response_chunk: Pedaços da resposta
    - response: Resposta completa (opcional)
    - done: Indica que terminou
    """
    try:
        # Validar entrada
        if not request.question or request.question.strip() == "":
            raise HTTPException(status_code=400, detail="A pergunta não pode estar vazia")
        
        if request.max_tokens < 1 or request.max_tokens > 1024:
            raise HTTPException(status_code=400, detail="max_tokens deve estar entre 1 e 1024")
        
        # Retornar streaming response
        return StreamingResponse(
            llm_service.generate_response_stream(
                prompt=request.question,
                max_tokens=request.max_tokens
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar pergunta: {str(e)}")

@app.get("/modelo")
async def informacoes_modelo():
    """Retorna informações sobre o modelo carregado"""
    return {
        "nome_modelo": llm_service.model_name,
        "dispositivo": str(llm_service.model.device) if llm_service.model else None,
        "tipo_modelo": type(llm_service.model).__name__ if llm_service.model else None
    }