from django.db import models
from django.utils import timezone


class Categoria(models.Model):
    nome = models.CharField(max_length=50)

    # Ex: 'Bebidas', 'Salgadinhos', 'Doces'

    def __str__(self):
        return self.nome


class Produto(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='produtos')
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, help_text="Ex: Refrigerante 2L")
    preco = models.DecimalField(max_digits=7, decimal_places=2)
    imagem = models.ImageField(upload_to='produtos/', null=True, blank=True)
    disponivel = models.BooleanField(default=True)

    def __str__(self):
        return self.nome


class Pedido(models.Model):
    # Campos que aparecem no seu formulário "FINALIZAR PEDIDO" da imagem
    STATUS_CHOICES = [
        ('novo', 'Em Negociação'),
        ('confirmado', 'Confirmado/Preparação'),
        ('finalizado', 'Registrado no Caderno'),
    ]
    # ... seus campos de nome, telefone, endereco ...
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='novo')

    nome_cliente = models.CharField(max_length=150)
    telefone = models.CharField(max_length=20)
    endereco = models.TextField()
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    data_pedido = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido {self.id} - {self.nome_cliente}"

    def itens_resumo_whats(self):
        itens = self.itens.all()
        # O %0A faz o WhatsApp pular uma linha para cada produto
        return "%0A".join([f"• {item.quantidade}x {item.produto.nome}" for item in itens])

    def itens_resumo(self):
        itens = self.itens.all()
        return ", ".join([f"{item.quantidade}x {item.produto.nome}" for item in itens])


class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)
    preco_unitario = models.DecimalField(max_digits=7, decimal_places=2)

    def total_item(self):
        return self.quantidade * self.preco_unitario