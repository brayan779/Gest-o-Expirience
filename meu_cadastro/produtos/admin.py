from django.contrib import admin
from .models import Produto, Categoria, Pedido, ItemPedido


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'get_pai', 'ordem')
    list_editable = ('ordem',)
    search_fields = ('nome',)

    def get_pai(self, obj):
        return obj.pai.nome if obj.pai else "---"

    get_pai.short_description = "Categoria Pai"


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'get_categoria', 'preco', 'disponivel', 'ordem')
    list_editable = ('preco', 'disponivel', 'ordem')
    list_filter = ('categoria', 'disponivel')
    search_fields = ('nome', 'descricao')

    def get_categoria(self, obj):
        return f"{obj.categoria_pai.nome} > {obj.categoria.nome}"

    get_categoria.short_description = "Categoria"


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome_cliente', 'telefone', 'total', 'status', 'data_pedido')
    list_filter = ('status', 'data_pedido')
    inlines = [ItemPedidoInline]