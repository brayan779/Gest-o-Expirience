from django.shortcuts import render, redirect
# IMPORTAÇÃO: Funções essenciais para renderizar templates e redirecionar URLs.
from .forms import PessoaForm
# IMPORTAÇÃO: Importa a classe de formulário para Pessoa (usada no cadastro).
from .models import Pessoa
# IMPORTAÇÃO: Importa a classe do modelo Pessoa (tabela do banco de dados).
from django.db.models import Q
# IMPORTAÇÃO: Importa Q, usado para consultas complexas (embora não usado diretamente abaixo).

from django.contrib.auth import logout




def home_view(request): # ESTA É A FUNÇÃO HOME
    # FUNÇÃO: Lida com a exibição da página inicial.
    if 'pessoa_id' in request.session:
        # CONDIÇÃO: Verifica se o usuário está logado.
        nome_usuario = request.session.get('pessoa_nome', 'Visitante')
        # SESSÃO: Pega o nome da sessão ou usa 'Visitante' como padrão.
    else:
        # SENÃO: Se não estiver logado.
        nome_usuario = 'Visitante'
        # VALOR PADRÃO: Define o nome como 'Visitante'.
    return render(request, 'pessoas/home.html', {'nome': nome_usuario})
    # RENDERIZAÇÃO: Exibe a página home, passando o nome para saudação.


# pessoas/views.py (Trecho da logout_view)
def sair_do_sistema(request):
    # 1. Limpa todos os dados da sessão (carrinho, id do usuário, etc)
    request.session.flush()

    # 2. (Opcional) Se usar o sistema padrão do Django também:
    logout(request)

    # 3. Redireciona para a home limpo
    return redirect('home')


