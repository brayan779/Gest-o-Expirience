from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    # 1. Rota do Painel Administrativo
    path('admin/', admin.site.urls),

    # 2. Rota Raiz (/) - Agora aponta para o App de Produtos (Conveniência)
    # Isso fará com que o site abra direto na página das fotos que você mandou
    path('', include('produtos.urls')),

    # 3. Rota de Contas (Login/Cadastro se ainda for usar algum dia)
    path('contas/', include('pessoas.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),


]
# 4. CONFIGURAÇÃO DE IMAGENS (Essencial para as fotos dos produtos aparecerem)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)