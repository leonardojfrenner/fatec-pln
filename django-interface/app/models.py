from django.db import models
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

# Conexão com MongoDB
def get_db():
    client = MongoClient(
        host='localhost',
        port=27017,
        username='admin',
        password='admin',
        authSource='admin'
    )
    return client['chat_database']

# Funções para gerenciar Chats
class ChatManager:
    def __init__(self):
        self.db = get_db()
        self.collection = self.db['chats']
    
    def criar_chat(self, titulo="Novo Chat"):
        """Cria um novo chat"""
        chat = {
            'titulo': titulo,
            'criado_em': datetime.now(),
            'atualizado_em': datetime.now(),
            'mensagens': []
        }
        resultado = self.collection.insert_one(chat)
        return str(resultado.inserted_id)
    
    def adicionar_mensagem(self, chat_id, pergunta, resposta):
        """Adiciona uma mensagem (pergunta e resposta) a um chat"""
        mensagem = {
            'pergunta': pergunta,
            'resposta': resposta,
            'timestamp': datetime.now()
        }
        
        self.collection.update_one(
            {'_id': ObjectId(chat_id)},
            {
                '$push': {'mensagens': mensagem},
                '$set': {'atualizado_em': datetime.now()}
            }
        )
        return mensagem
    
    def obter_chat(self, chat_id):
        """Obtém um chat específico"""
        chat = self.collection.find_one({'_id': ObjectId(chat_id)})
        if chat:
            chat['_id'] = str(chat['_id'])
        return chat
    
    def listar_chats(self):
        """Lista todos os chats"""
        chats = list(self.collection.find().sort('atualizado_em', -1))
        for chat in chats:
            chat['_id'] = str(chat['_id'])
        return chats
    
    def deletar_chat(self, chat_id):
        """Deleta um chat"""
        resultado = self.collection.delete_one({'_id': ObjectId(chat_id)})
        return resultado.deleted_count > 0
    
    def atualizar_titulo(self, chat_id, novo_titulo):
        """Atualiza o título de um chat"""
        self.collection.update_one(
            {'_id': ObjectId(chat_id)},
            {'$set': {'titulo': novo_titulo, 'atualizado_em': datetime.now()}}
        )
        return True
