from django.contrib import admin
from .models import Produto, Categoria, Pedido, ItemPedido

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome',)

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    # Exibe essas colunas na listagem do Admin
    list_display = ('nome', 'categoria', 'preco', 'disponivel')
    # Permite editar a disponibilidade e o preço direto na lista
    list_editable = ('preco', 'disponivel')
    # Cria um filtro lateral por categoria
    list_filter = ('categoria', 'disponivel')
    # Campo de busca por nome
    search_fields = ('nome',)

# Para você conseguir ver os pedidos que chegam pelo site
class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome_cliente', 'telefone', 'total', 'data_pedido')
    inlines = [ItemPedidoInline]