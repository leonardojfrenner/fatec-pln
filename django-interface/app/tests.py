from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock, Mock
import json
from datetime import datetime
from bson import ObjectId
from .models import ChatManager


class ChatManagerTestCase(TestCase):
    """Testes para o gerenciador de chats no MongoDB"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.chat_manager = ChatManager()
        # Limpa a coleção antes de cada teste
        self.chat_manager.collection.delete_many({})
    
    def tearDown(self):
        """Limpeza após cada teste"""
        # Limpa a coleção após cada teste
        self.chat_manager.collection.delete_many({})
    
    def test_criar_chat_retorna_id_valido(self):
        """Testa se criar_chat retorna um ID válido"""
        chat_id = self.chat_manager.criar_chat(titulo="Teste Chat")
        
        # Verifica se o ID não é None
        self.assertIsNotNone(chat_id)
        # Verifica se é uma string
        self.assertTrue(isinstance(chat_id, str))
        # Verifica se tem o formato de ObjectId
        self.assertTrue(len(chat_id) == 24)
    
    def test_criar_chat_com_titulo_customizado(self):
        """Testa se o chat é criado com o título correto"""
        titulo = "Meu Chat Personalizado"
        chat_id = self.chat_manager.criar_chat(titulo=titulo)
        
        # Busca o chat criado
        chat = self.chat_manager.obter_chat(chat_id)
        
        # Verifica se o título está correto
        self.assertEqual(chat['titulo'], titulo)
        # Verifica se mensagens está vazio
        self.assertEqual(len(chat['mensagens']), 0)
    
    def test_criar_chat_com_titulo_padrao(self):
        """Testa se o chat usa título padrão quando não fornecido"""
        chat_id = self.chat_manager.criar_chat()
        chat = self.chat_manager.obter_chat(chat_id)
        
        self.assertEqual(chat['titulo'], "Novo Chat")
    
    def test_adicionar_mensagem_ao_chat(self):
        """Testa adicionar mensagem a um chat"""
        # Cria um chat
        chat_id = self.chat_manager.criar_chat(titulo="Chat Teste")
        
        # Adiciona mensagem
        pergunta = "Qual é a capital do Brasil?"
        resposta = "A capital do Brasil é Brasília."
        mensagem = self.chat_manager.adicionar_mensagem(chat_id, pergunta, resposta)
        
        # Verifica se a mensagem foi retornada
        self.assertIsNotNone(mensagem)
        self.assertEqual(mensagem['pergunta'], pergunta)
        self.assertEqual(mensagem['resposta'], resposta)
        self.assertIsNotNone(mensagem['timestamp'])
        
        # Busca o chat e verifica se a mensagem está lá
        chat = self.chat_manager.obter_chat(chat_id)
        self.assertEqual(len(chat['mensagens']), 1)
        self.assertEqual(chat['mensagens'][0]['pergunta'], pergunta)
    
    def test_adicionar_multiplas_mensagens(self):
        """Testa adicionar várias mensagens ao mesmo chat"""
        chat_id = self.chat_manager.criar_chat(titulo="Chat Múltiplas Mensagens")
        
        # Adiciona 5 mensagens
        for i in range(5):
            self.chat_manager.adicionar_mensagem(
                chat_id, 
                f"Pergunta {i+1}",
                f"Resposta {i+1}"
            )
        
        # Verifica se todas foram adicionadas
        chat = self.chat_manager.obter_chat(chat_id)
        self.assertEqual(len(chat['mensagens']), 5)
        
        # Verifica se estão na ordem correta
        for i, msg in enumerate(chat['mensagens']):
            self.assertEqual(msg['pergunta'], f"Pergunta {i+1}")
            self.assertEqual(msg['resposta'], f"Resposta {i+1}")
    
    def test_obter_chat_inexistente_retorna_none(self):
        """Testa buscar um chat que não existe"""
        # Cria um ObjectId falso
        chat_id_fake = str(ObjectId())
        
        chat = self.chat_manager.obter_chat(chat_id_fake)
        self.assertIsNone(chat)
    
    def test_listar_chats_vazio(self):
        """Testa listar chats quando não há nenhum"""
        chats = self.chat_manager.listar_chats()
        self.assertEqual(len(chats), 0)
        self.assertTrue(isinstance(chats, list))
    
    def test_listar_chats_com_multiplos_chats(self):
        """Testa listar vários chats"""
        # Cria 3 chats
        titulos = ["Chat 1", "Chat 2", "Chat 3"]
        for titulo in titulos:
            self.chat_manager.criar_chat(titulo=titulo)
        
        # Lista todos
        chats = self.chat_manager.listar_chats()
        
        self.assertEqual(len(chats), 3)
        # Verifica se todos têm _id convertido para string
        for chat in chats:
            self.assertTrue(isinstance(chat['_id'], str))
    
    def test_deletar_chat_existente(self):
        """Testa deletar um chat que existe"""
        # Cria um chat
        chat_id = self.chat_manager.criar_chat(titulo="Chat para Deletar")
        
        # Deleta o chat
        sucesso = self.chat_manager.deletar_chat(chat_id)
        
        self.assertTrue(sucesso)
        
        # Verifica se realmente foi deletado
        chat = self.chat_manager.obter_chat(chat_id)
        self.assertIsNone(chat)
    
    def test_deletar_chat_inexistente(self):
        """Testa deletar um chat que não existe"""
        chat_id_fake = str(ObjectId())
        
        sucesso = self.chat_manager.deletar_chat(chat_id_fake)
        self.assertFalse(sucesso)
    
    def test_atualizar_titulo_chat(self):
        """Testa atualizar o título de um chat"""
        # Cria um chat
        chat_id = self.chat_manager.criar_chat(titulo="Título Original")
        
        # Atualiza o título
        novo_titulo = "Título Atualizado"
        resultado = self.chat_manager.atualizar_titulo(chat_id, novo_titulo)
        
        self.assertTrue(resultado)
        
        # Verifica se foi atualizado
        chat = self.chat_manager.obter_chat(chat_id)
        self.assertEqual(chat['titulo'], novo_titulo)
    
    def test_chat_tem_timestamps_validos(self):
        """Testa se os timestamps são criados corretamente"""
        chat_id = self.chat_manager.criar_chat(titulo="Chat com Timestamps")
        chat = self.chat_manager.obter_chat(chat_id)
        
        # Verifica se criado_em existe e é datetime
        self.assertIsNotNone(chat['criado_em'])
        self.assertTrue(isinstance(chat['criado_em'], datetime))
        
        # Verifica se atualizado_em existe e é datetime
        self.assertIsNotNone(chat['atualizado_em'])
        self.assertTrue(isinstance(chat['atualizado_em'], datetime))


class ViewsTestCase(TestCase):
    """Testes para as views da aplicação"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.client = Client()
        self.chat_manager = ChatManager()
        # Limpa a coleção antes de cada teste
        self.chat_manager.collection.delete_many({})
    
    def tearDown(self):
        """Limpeza após cada teste"""
        self.chat_manager.collection.delete_many({})
    
    def test_index_retorna_200(self):
        """Testa se a página inicial carrega com sucesso"""
        response = self.client.get(reverse('app:index'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
    
    @patch('requests.post')
    def test_pergunta_endpoint_com_nova_pergunta(self, mock_post):
        """Testa o endpoint de pergunta criando novo chat"""
        # Mock da resposta da API externa
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'response': 'Esta é uma resposta de teste'
        }
        mock_post.return_value = mock_response
        
        # Faz a requisição
        response = self.client.post(
            reverse('app:pergunta'),
            data=json.dumps({
                'question': 'Qual é a capital da França?'
            }),
            content_type='application/json'
        )
        
        # Verifica resposta
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verifica se tem resposta e chat_id
        self.assertIn('response', data)
        self.assertIn('chat_id', data)
        self.assertIsNotNone(data['chat_id'])
        self.assertEqual(data['response'], 'Esta é uma resposta de teste')
    
    def test_pergunta_endpoint_sem_pergunta(self):
        """Testa o endpoint de pergunta sem enviar pergunta"""
        response = self.client.post(
            reverse('app:pergunta'),
            data=json.dumps({'question': ''}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Pergunta não fornecida')
    
    def test_criar_chat_endpoint(self):
        """Testa o endpoint de criar chat"""
        response = self.client.post(
            reverse('app:criar_chat'),
            data=json.dumps({'titulo': 'Novo Chat Teste'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('chat_id', data)
        self.assertEqual(data['titulo'], 'Novo Chat Teste')
        self.assertIn('mensagem', data)
    
    def test_listar_chats_endpoint_vazio(self):
        """Testa listar chats quando não há nenhum"""
        response = self.client.get(reverse('app:listar_chats'))
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('chats', data)
        self.assertEqual(len(data['chats']), 0)
        self.assertTrue(isinstance(data['chats'], list))
    
    def test_listar_chats_endpoint_com_chats(self):
        """Testa listar chats quando há chats criados"""
        # Cria alguns chats
        self.chat_manager.criar_chat(titulo="Chat 1")
        self.chat_manager.criar_chat(titulo="Chat 2")
        
        response = self.client.get(reverse('app:listar_chats'))
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(len(data['chats']), 2)
    
    def test_obter_chat_existente(self):
        """Testa obter um chat específico que existe"""
        # Cria um chat
        chat_id = self.chat_manager.criar_chat(titulo="Chat Específico")
        self.chat_manager.adicionar_mensagem(
            chat_id, 
            "Pergunta teste", 
            "Resposta teste"
        )
        
        # Busca o chat
        response = self.client.get(
            reverse('app:obter_chat', kwargs={'chat_id': chat_id})
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('chat', data)
        self.assertEqual(data['chat']['titulo'], "Chat Específico")
        self.assertEqual(len(data['chat']['mensagens']), 1)
    
    def test_obter_chat_inexistente(self):
        """Testa obter um chat que não existe"""
        chat_id_fake = str(ObjectId())
        
        response = self.client.get(
            reverse('app:obter_chat', kwargs={'chat_id': chat_id_fake})
        )
        
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn('error', data)
    
    def test_deletar_chat_endpoint(self):
        """Testa deletar um chat via endpoint"""
        # Cria um chat
        chat_id = self.chat_manager.criar_chat(titulo="Chat para Deletar")
        
        # Deleta via endpoint
        response = self.client.delete(
            reverse('app:deletar_chat', kwargs={'chat_id': chat_id})
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('mensagem', data)
        
        # Verifica se foi realmente deletado
        chat = self.chat_manager.obter_chat(chat_id)
        self.assertIsNone(chat)
    
    def test_deletar_chat_inexistente_endpoint(self):
        """Testa deletar um chat que não existe via endpoint"""
        chat_id_fake = str(ObjectId())
        
        response = self.client.delete(
            reverse('app:deletar_chat', kwargs={'chat_id': chat_id_fake})
        )
        
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn('error', data)
    
    def test_atualizar_titulo_endpoint(self):
        """Testa atualizar título via endpoint"""
        # Cria um chat
        chat_id = self.chat_manager.criar_chat(titulo="Título Original")
        
        # Atualiza o título
        response = self.client.put(
            reverse('app:atualizar_titulo_chat', kwargs={'chat_id': chat_id}),
            data=json.dumps({'titulo': 'Título Novo'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('mensagem', data)
        
        # Verifica se foi atualizado
        chat = self.chat_manager.obter_chat(chat_id)
        self.assertEqual(chat['titulo'], 'Título Novo')
    
    def test_atualizar_titulo_sem_titulo(self):
        """Testa atualizar título sem fornecer título"""
        chat_id = self.chat_manager.criar_chat(titulo="Chat Teste")
        
        response = self.client.put(
            reverse('app:atualizar_titulo_chat', kwargs={'chat_id': chat_id}),
            data=json.dumps({}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
    
    def test_download_json_endpoint(self):
        """Testa download de chat em formato JSON"""
        # Cria um chat com mensagens
        chat_id = self.chat_manager.criar_chat(titulo="Chat Download JSON")
        self.chat_manager.adicionar_mensagem(
            chat_id,
            "Pergunta 1",
            "Resposta 1"
        )
        
        # Faz o download
        response = self.client.get(
            reverse('app:download-json', kwargs={'chat_id': chat_id})
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json; charset=utf-8')
        self.assertIn('attachment', response['Content-Disposition'])
        
        # Verifica se o JSON é válido
        content = response.content.decode('utf-8')
        data = json.loads(content)
        self.assertEqual(data['titulo'], "Chat Download JSON")
        self.assertEqual(len(data['mensagens']), 1)
    
    def test_download_csv_endpoint(self):
        """Testa download de chat em formato CSV"""
        # Cria um chat com mensagens
        chat_id = self.chat_manager.criar_chat(titulo="Chat Download CSV")
        self.chat_manager.adicionar_mensagem(
            chat_id,
            "Pergunta CSV",
            "Resposta CSV"
        )
        
        # Faz o download
        response = self.client.get(
            reverse('app:download-csv', kwargs={'chat_id': chat_id})
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8')
        self.assertIn('attachment', response['Content-Disposition'])
        
        # Verifica se o CSV tem conteúdo
        content = response.content.decode('utf-8-sig')
        self.assertIn('Pergunta', content)
        self.assertIn('Resposta', content)
        self.assertIn('Pergunta CSV', content)
    
    def test_download_json_chat_inexistente(self):
        """Testa download JSON de chat que não existe"""
        chat_id_fake = str(ObjectId())
        
        response = self.client.get(
            reverse('app:download-json', kwargs={'chat_id': chat_id_fake})
        )
        
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn('error', data)


class IntegrationTestCase(TestCase):
    """Testes de integração completos"""
    
    def setUp(self):
        """Configuração inicial"""
        self.client = Client()
        self.chat_manager = ChatManager()
        self.chat_manager.collection.delete_many({})
    
    def tearDown(self):
        """Limpeza"""
        self.chat_manager.collection.delete_many({})
    
    def test_fluxo_completo_criar_chat_adicionar_mensagens_deletar(self):
        """Testa um fluxo completo de uso da aplicação"""
        # 1. Cria um chat
        response_criar = self.client.post(
            reverse('app:criar_chat'),
            data=json.dumps({'titulo': 'Chat Integração'}),
            content_type='application/json'
        )
        self.assertEqual(response_criar.status_code, 200)
        chat_id = response_criar.json()['chat_id']
        
        # 2. Adiciona mensagens
        for i in range(3):
            self.chat_manager.adicionar_mensagem(
                chat_id,
                f"Pergunta {i+1}",
                f"Resposta {i+1}"
            )
        
        # 3. Busca o chat e verifica
        response_obter = self.client.get(
            reverse('app:obter_chat', kwargs={'chat_id': chat_id})
        )
        self.assertEqual(response_obter.status_code, 200)
        chat_data = response_obter.json()['chat']
        self.assertEqual(len(chat_data['mensagens']), 3)
        
        # 4. Atualiza o título
        response_atualizar = self.client.put(
            reverse('app:atualizar_titulo_chat', kwargs={'chat_id': chat_id}),
            data=json.dumps({'titulo': 'Chat Atualizado'}),
            content_type='application/json'
        )
        self.assertEqual(response_atualizar.status_code, 200)
        
        # 5. Verifica atualização
        chat = self.chat_manager.obter_chat(chat_id)
        self.assertEqual(chat['titulo'], 'Chat Atualizado')
        
        # 6. Deleta o chat
        response_deletar = self.client.delete(
            reverse('app:deletar_chat', kwargs={'chat_id': chat_id})
        )
        self.assertEqual(response_deletar.status_code, 200)
        
        # 7. Verifica que foi deletado
        chat_deletado = self.chat_manager.obter_chat(chat_id)
        self.assertIsNone(chat_deletado)
        
        # 8. Lista chats e verifica que está vazio
        response_listar = self.client.get(reverse('app:listar_chats'))
        self.assertEqual(len(response_listar.json()['chats']), 0)
