from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import csv
from .models import ChatManager
import io
# Create your views here.
def index(request):
    return render(request, 'index.html')

@csrf_exempt
@require_http_methods(["POST"])
def pergunta(request):
    """
    Endpoint para processar perguntas do usuário
    Recebe: { "question": "...", "chat_id": "...", "max_tokens": 256 }
    """
    try:
        print(f"[DEBUG] Recebida requisição: {request.body}")
        data = json.loads(request.body)
        pergunta_usuario = data.get('question', '')
        chat_id = data.get('chat_id')
        
        print(f"[DEBUG] Pergunta: {pergunta_usuario}")
        print(f"[DEBUG] Chat ID: {chat_id}")
        
        if not pergunta_usuario:
            return JsonResponse({'error': 'Pergunta não fornecida'}, status=400)
        
        # Integração com API FastAPI do modelo
        try:
            import requests
            print(f"[DEBUG] Chamando API do modelo: http://localhost:8000/pergunta")
            
            api_response = requests.post(
                "http://localhost:8000/pergunta",
                json={"question": pergunta_usuario},
                timeout=120
            )
            
            print(f"[DEBUG] Status da API: {api_response.status_code}")
            print(f"[DEBUG] Resposta da API: {api_response.text}")
            
            if api_response.status_code == 200:
                api_data = api_response.json()
                resposta_modelo = api_data.get('response', 'Desculpe, não consegui processar sua pergunta.')
            else:
                resposta_modelo = f"Erro na API do modelo: {api_response.status_code} - {api_response.text}"
                
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Erro ao conectar com API do modelo: {e}")
            resposta_modelo = "Erro ao conectar com o modelo de IA. Tente novamente."
        
        # Gerenciador de chat
        chat_manager = ChatManager()
        
        # Se não existe chat_id, cria um novo chat
        if not chat_id:
            print("[DEBUG] Criando novo chat...")
            chat_id = chat_manager.criar_chat(titulo=f"Chat - {pergunta_usuario[:30]}")
            print(f"[DEBUG] Novo chat criado: {chat_id}")
        
        # Adiciona a mensagem ao chat
        print(f"[DEBUG] Adicionando mensagem ao chat {chat_id}...")
        chat_manager.adicionar_mensagem(chat_id, pergunta_usuario, resposta_modelo)
        print("[DEBUG] Mensagem adicionada com sucesso!")
        
        return JsonResponse({
            'response': resposta_modelo,
            'chat_id': chat_id
        })
    
    except Exception as e:
        print(f"[ERROR] Erro na view pergunta: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def criar_chat(request):
    """Cria um novo chat"""
    try:
        data = json.loads(request.body)
        titulo = data.get('titulo', 'Novo Chat')
        
        chat_manager = ChatManager()
        chat_id = chat_manager.criar_chat(titulo)
        
        return JsonResponse({
            'chat_id': chat_id,
            'titulo': titulo,
            'mensagem': 'Chat criado com sucesso'
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def listar_chats(request):
    """Lista todos os chats"""
    try:
        chat_manager = ChatManager()
        chats = chat_manager.listar_chats()
        
        # Converte datetime para string
        for chat in chats:
            chat['criado_em'] = chat['criado_em'].isoformat()
            chat['atualizado_em'] = chat['atualizado_em'].isoformat()
            for msg in chat['mensagens']:
                msg['timestamp'] = msg['timestamp'].isoformat()
        
        return JsonResponse({'chats': chats})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def obter_chat(request, chat_id):
    """Obtém um chat específico"""
    try:
        chat_manager = ChatManager()
        chat = chat_manager.obter_chat(chat_id)
        
        if not chat:
            return JsonResponse({'error': 'Chat não encontrado'}, status=404)
        
        # Converte datetime para string
        chat['criado_em'] = chat['criado_em'].isoformat()
        chat['atualizado_em'] = chat['atualizado_em'].isoformat()
        for msg in chat['mensagens']:
            msg['timestamp'] = msg['timestamp'].isoformat()
        
        return JsonResponse({'chat': chat})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["DELETE"])
def deletar_chat(request, chat_id):
    """Deleta um chat"""
    try:
        chat_manager = ChatManager()
        sucesso = chat_manager.deletar_chat(chat_id)
        
        if sucesso:
            return JsonResponse({'mensagem': 'Chat deletado com sucesso'})
        else:
            return JsonResponse({'error': 'Chat não encontrado'}, status=404)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["PUT"])
def atualizar_titulo_chat(request, chat_id):
    """Atualiza o título de um chat"""
    try:
        data = json.loads(request.body)
        novo_titulo = data.get('titulo')
        
        if not novo_titulo:
            return JsonResponse({'error': 'Título não fornecido'}, status=400)
        
        chat_manager = ChatManager()
        chat_manager.atualizar_titulo(chat_id, novo_titulo)
        
        return JsonResponse({'mensagem': 'Título atualizado com sucesso'})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



@require_http_methods(["GET"])
def download_chat_json(request, chat_id):
    """Download do chat em formato JSON"""
    try:
        chat_manager = ChatManager()
        chat = chat_manager.obter_chat(chat_id)

        if not chat:
            return JsonResponse({'error': 'Chat não encontrado'}, status=404)

        # Converte o chat em JSON serializável
        def serialize_mongo(obj):
            """Converte tipos do MongoDB (ObjectId, datetime, etc.)"""
            from bson import ObjectId
            from datetime import datetime
            if isinstance(obj, ObjectId):
                return str(obj)
            if isinstance(obj, datetime):
                return obj.isoformat()
            return obj

        json_data = json.dumps(chat, default=serialize_mongo, indent=2, ensure_ascii=False)

        # Cria resposta HTTP para download
        response = HttpResponse(json_data, content_type='application/json; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="chat_{chat_id}.json"'
        response['Content-Length'] = len(json_data.encode("utf-8"))

        print(f"[DEBUG] JSON gerado com sucesso ({len(json_data.encode('utf-8'))} bytes)")
        return response

    except Exception as e:
        print(f"[ERRO] {e}")
        return JsonResponse({'error': str(e)}, status=500)
    
@require_http_methods(["GET"])
def download_chat_csv(request, chat_id):
    # Busca os dados do chat (exemplo)
    chat_data = [
        {"pergunta": "2+2?", "resposta": "2 + 2 é 4.", "timestamp": "23/10/2025 09:44"},
        {"pergunta": "4*4?", "resposta": "4 multiplicado por 4 é 16.", "timestamp": "23/10/2025 15:11"},
    ]

    # Cria um buffer com codificação UTF-8 com BOM
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=',')
    writer.writerow(["Pergunta", "Resposta", "Timestamp"])

    for item in chat_data:
        writer.writerow([item["pergunta"], item["resposta"], item["timestamp"]])

    response = HttpResponse(buffer.getvalue().encode('utf-8-sig'), content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="chat-{chat_id}.csv"'
    return response