# Arquivo: pessoas/forms.py

from django import forms
from .models import Pessoa

class PessoaForm(forms.ModelForm):
    class Meta:
        model = Pessoa
        # ATUALIZE ESTA LINHA para incluir todos os campos do seu modelo:
        fields = ['nome', 'email', 'senha']