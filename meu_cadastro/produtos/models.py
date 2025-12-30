from django.db import models
from django.utils import timezone

class Categoria(models.Model):
    nome = models.CharField(max_length=50)
    pai = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategorias',
        verbose_name="Categoria Pai"
    )
    ordem = models.IntegerField(default=0, help_text="Ordem de exibição")

    def __str__(self):
        if self.pai:
            return f"{self.pai.nome} > {self.nome}"
        return self.nome

    @property
    def is_subcategoria(self):
        return self.pai is not None

    @property
    def is_categoria_pai(self):
        return self.pai is None

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['ordem', 'nome']

class Sabor(models.Model):
    nome = models.CharField(max_length=50)
    disponivel = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Sabor"
        verbose_name_plural = "Sabores"

class Produto(models.Model):
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        related_name='produtos'
    )
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, help_text="Ex: Refrigerante 2L")
    preco = models.DecimalField(max_digits=7, decimal_places=2)
    imagem = models.ImageField(upload_to='produtos/', null=True, blank=True)
    disponivel = models.BooleanField(default=True)
    ordem = models.IntegerField(default=0, help_text="Ordem de exibição")
    sabores = models.ManyToManyField(Sabor, blank=True, related_name='produtos')

    def __str__(self):
        return self.nome

    @property
    def categoria_pai(self):
        return self.categoria.pai if self.categoria.pai else self.categoria

    class Meta:
        ordering = ['ordem', 'nome']


# ... (mantenha Pedido e ItemPedido como estão) ...

class Pedido(models.Model):
    # Campos que aparecem no seu formulário "FINALIZAR PEDIDO" da imagem
    STATUS_CHOICES = [
        ('novo', 'Em Negociação'),
        ('confirmado', 'Confirmado/Preparação'),
        ('finalizado', 'Finalizado'),
        ('registrado', 'Registrado no Caderno'),  # Adicione este status
        ('cancelado', 'Cancelado'),
    ]
    # ... seus campos de nome, telefone, endereco ...
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='novo')

    nome_cliente = models.CharField(max_length=150)
    telefone = models.CharField(max_length=20)
    endereco = models.TextField(blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    data_pedido = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido {self.id} - {self.nome_cliente}"

    def itens_resumo_whats(self):
        itens = self.itens.all()
        # Esta função formata a lista para o link do WhatsApp
        return "%0A".join([
            f"• {item.quantidade}x {item.produto.nome} ({item.sabor_escolhido if item.sabor_escolhido else 'S/S'})"
            for item in itens
        ])

    def itens_resumo(self):
        itens = self.itens.all()
        # Esta função formata para exibição em texto no seu site/painel
        return "\n".join([
            f"• {item.quantidade}x {item.produto.nome} ({item.sabor_escolhido if item.sabor_escolhido else 'S/Sabor'})"
            for item in itens
        ])




class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)
    preco_unitario = models.DecimalField(max_digits=7, decimal_places=2)
    sabor_escolhido = models.CharField(max_length=50, null=True, blank=True)

    def total_item(self):
        return self.quantidade * self.preco_unitario

