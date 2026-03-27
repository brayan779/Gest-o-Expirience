# pessoas/models.py

from django.db import models


class Pessoa(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)  # Novo campo
    senha = models.CharField(max_length=100)  # Novo campo

    def __str__(self):
        return self.nome


class Produto(models.Model):
    nome = models.CharField(max_length=100)
    preco = models.FloatField()
    tipo_produto = models.CharField(max_length=50)
    quantidade = models.IntegerField()

    def __str__(self):
        return self.nome