# Script de deploy para Docker Hub
# Usuário: leonardorennerdev

Write-Host "🚀 Deploy da imagem para Docker Hub" -ForegroundColor Cyan
Write-Host ""

# Variáveis
$DOCKER_USER = "leonardorennerdev"
$IMAGE_NAME = "chat-llm-api"
$VERSION = "1.0.0"

# Verificar se está logado
Write-Host "Verificando login no Docker Hub..." -ForegroundColor Yellow
docker info | Select-String -Pattern "Username"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Fazendo login no Docker Hub..." -ForegroundColor Yellow
    docker login
}

# Construir a imagem
Write-Host ""
Write-Host "📦 Construindo imagem..." -ForegroundColor Yellow
docker-compose build

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao construir imagem!" -ForegroundColor Red
    exit 1
}

# Criar tags
Write-Host ""
Write-Host "🏷️  Criando tags..." -ForegroundColor Yellow
docker tag chat-llm-api "${DOCKER_USER}/${IMAGE_NAME}:latest"
docker tag chat-llm-api "${DOCKER_USER}/${IMAGE_NAME}:${VERSION}"

# Fazer push
Write-Host ""
Write-Host "⬆️  Fazendo push para Docker Hub..." -ForegroundColor Yellow
docker push "${DOCKER_USER}/${IMAGE_NAME}:latest"
docker push "${DOCKER_USER}/${IMAGE_NAME}:${VERSION}"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Deploy concluído com sucesso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📦 Imagem publicada em:" -ForegroundColor Cyan
    Write-Host "   https://hub.docker.com/r/${DOCKER_USER}/${IMAGE_NAME}" -ForegroundColor White
    Write-Host ""
    Write-Host "🚀 Para usar em outra máquina:" -ForegroundColor Cyan
    Write-Host "   docker pull ${DOCKER_USER}/${IMAGE_NAME}:latest" -ForegroundColor White
    Write-Host "   docker run -d -p 8000:8000 ${DOCKER_USER}/${IMAGE_NAME}:latest" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "❌ Erro ao fazer push!" -ForegroundColor Red
}


