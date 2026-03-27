from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'produtos'

urlpatterns = [
    path('', views.home_conveniencia, name='home'),
    path('adicionar/<int:produto_id>/', views.adicionar_carrinho, name='adicionar_carrinho'),
    path('remover/<int:produto_id>/', views.remover_unidade_carrinho, name='remover_unidade_carrinho'),
    path('finalizar/', views.finalizar_pedido, name='finalizar_pedido'),

    # PAINEL DO DONO
    path('painel/', views.painel_dono, name='painel_dono'),
    path('carrinho/ajax/<str:produto_id>/<str:acao>/', views.gerenciar_carrinho_ajax, name='carrinho_ajax'),

    # CORRIJA AS ROTAS DUPLICADAS:
    # Mantenha apenas um conjunto de rotas para pedidos
    path('pedido/<int:pedido_id>/mudar-status/<str:novo_status>/', views.mudar_status_pedido, name='mudar_status'),
    path('pedido/<int:pedido_id>/recusar/', views.recusar_pedido, name='recusar_pedido'),
    path('pedido/<int:pedido_id>/imprimir/', views.imprimir_pedido, name='imprimir_pedido'),
    path('pedido/<int:pedido_id>/registrar/', views.registrar_caderno, name='registrar_caderno'),

    # Caderno
    path('caderno/', views.caderno_gestao, name='caderno'),

    # Autenticação
    path('login/', auth_views.LoginView.as_view(
        template_name='produtos/login.html',
        redirect_authenticated_user=True
    ), name='login'),

    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]

# IMPORTANTE: Para PythonAnywhere, você precisa configurar o servidor para servir arquivos de mídia
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Em produção no PythonAnywhere, você precisa configurar no painel web
    # Vá em: Web -> Static files
    # Adicione: URL: /media/, Directory: /home/BrayanMath/meu_cadastro/media
    pass