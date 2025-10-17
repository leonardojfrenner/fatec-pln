"""
Script para iniciar a API do Chat com LLM
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "application.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

