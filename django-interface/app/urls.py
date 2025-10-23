from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    path('', views.index, name='index'),
    path('pergunta', views.pergunta, name='pergunta'),
    path('chats/', views.listar_chats, name='listar_chats'),
    path('chats/criar', views.criar_chat, name='criar_chat'),
    path('chats/<str:chat_id>', views.obter_chat, name='obter_chat'),
    path('chats/<str:chat_id>/deletar', views.deletar_chat, name='deletar_chat'),
    path('chats/<str:chat_id>/titulo', views.atualizar_titulo_chat, name='atualizar_titulo_chat'),
    path('download-json/<str:chat_id>/', views.download_chat_json, name='download-json'),
]