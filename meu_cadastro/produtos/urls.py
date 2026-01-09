from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'produtos'

urlpatterns = [
    path('', views.home_conveniencia, name='home'),
    path('adicionar/<int:produto_id>/', views.adicionar_carrinho, name='adicionar_carrinho'),
    path('remover/<int:produto_id>/', views.remover_unidade_carrinho, name='remover_unidade_carrinho'),
    path('finalizar/', views.finalizar_pedido, name='finalizar_pedido'),

    # NOVAS ROTAS PARA O PAINEL DO DONO
    path('painel/', views.painel_dono, name='painel_dono'),
    path('status/<int:pedido_id>/<str:novo_status>/', views.mudar_status_pedido, name='mudar_status'),
    path('imprimir/<int:pedido_id>/', views.imprimir_pedido, name='imprimir_pedido'),
    path('caderno/', views.caderno_gestao, name='caderno'),

    path('carrinho/ajax/<str:produto_id>/<str:acao>/', views.gerenciar_carrinho_ajax, name='carrinho_ajax'),



    path('pedido/recusar/<int:pedido_id>/', views.recusar_pedido, name='recusar_pedido'),
    path('pedido/<int:pedido_id>/mudar-status/<str:novo_status>/', views.mudar_status, name='mudar_status'),
    path('pedido/<int:pedido_id>/registrar/', views.registrar_caderno, name='registrar_caderno'),
    path('pedido/<int:pedido_id>/recusar/', views.recusar_pedido, name='recusar_pedido'),
    path('pedido/<int:pedido_id>/imprimir/', views.imprimir_pedido, name='imprimir_pedido'),
    path('login/', auth_views.LoginView.as_view(
        template_name='produtos/login.html',
        redirect_authenticated_user=True
    ), name='login'),

    path('logout/', auth_views.LogoutView.as_view(), name='logout'),




]