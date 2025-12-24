from django.shortcuts import render, redirect, get_object_or_404
from .models import Produto, Categoria, Pedido, ItemPedido
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.http import JsonResponse

def home_conveniencia(request):
    # 1. Busca todas as categorias e produtos para exibir na Landing Page
    categorias = Categoria.objects.all()
    categoria_id = request.GET.get('categoria')
    produtos = Produto.objects.filter(disponivel=True)

    if categoria_id:
        # Filtra os produtos pela categoria selecionada
        produtos = Produto.objects.filter(disponivel=True, categoria_id=categoria_id)
    else:
        # Se não tiver filtro, mostra tudo
        produtos = Produto.objects.filter(disponivel=True)

    # 2. Pega o carrinho da sessão para mostrar o "Resumo do Pedido" na mesma tela
    carrinho = request.session.get('carrinho', {})
    total_carrinho = 0
    itens_detalhados = []

    for item_id, dados in carrinho.items():
        # Verificação de segurança para evitar erro de dicionário/inteiro
        qtd = dados.get('quantidade', 0)
        preco = float(dados.get('preco', 0))

        subtotal = preco * qtd
        total_carrinho += subtotal

        itens_detalhados.append({
            'produto_id': item_id,
            'nome': dados.get('nome'),
            'quantidade': qtd,
            'preco': preco,
            'subtotal': subtotal
        })

    contexto = {
        'categorias': categorias,
        'produtos': produtos,
        'itens_carrinho': itens_detalhados,
        'total_carrinho': total_carrinho,
    }
    return render(request, 'produtos/cardapio.html', contexto)


def adicionar_carrinho(request, produto_id):
    carrinho = request.session.get('carrinho', {})
    id_str = str(produto_id)

    if id_str in carrinho:
        # Acessa a chave 'quantidade' corretamente para evitar o erro de dict + int
        carrinho[id_str]['quantidade'] += 1
    else:
        produto = get_object_or_404(Produto, id=produto_id)
        carrinho[id_str] = {
            'nome': produto.nome,
            'preco': str(produto.preco),
            'quantidade': 1
        }

    request.session['carrinho'] = carrinho
    request.session.modified = True
    return redirect('produtos:home')


def remover_unidade_carrinho(request, produto_id):
    carrinho = request.session.get('carrinho', {})
    id_str = str(produto_id)

    if id_str in carrinho:
        if carrinho[id_str]['quantidade'] > 1:
            carrinho[id_str]['quantidade'] -= 1
        else:
            del carrinho[id_str]

    request.session['carrinho'] = carrinho
    request.session.modified = True
    return redirect('produtos:home')


def finalizar_pedido(request):
    if request.method == 'POST':
        carrinho = request.session.get('carrinho', {})
        if not carrinho:
            return redirect('produtos:home')

        nome = request.POST.get('nome_completo')
        telefone = request.POST.get('telefone')
        endereco = request.POST.get('endereco')

        novo_pedido = Pedido.objects.create(
            nome_cliente=nome,
            telefone=telefone,
            endereco=endereco,
            total=0
        )

        total_geral = 0
        for item_id, dados in carrinho.items():
            produto = get_object_or_404(Produto, id=item_id)
            preco = float(dados['preco'])
            qtd = dados['quantidade']
            total_geral += preco * qtd

            ItemPedido.objects.create(
                pedido=novo_pedido,
                produto=produto,
                quantidade=qtd,
                preco_unitario=preco
            )

        novo_pedido.total = total_geral
        novo_pedido.save()

        request.session['carrinho'] = {}
        return render(request, 'produtos/sucesso.html', {'pedido': novo_pedido})

    return redirect('produtos:home')

@login_required
def painel_dono(request):
    # Coluna A: Apenas os novos
    novos = Pedido.objects.filter(status='novo').order_by('-data_pedido')
    # Coluna B: Apenas os confirmados
    confirmados = Pedido.objects.filter(status='confirmado').order_by('-data_pedido')

    return render(request, 'produtos/painel_dono.html', {
        'novos': novos,
        'confirmados': confirmados
    })


def mudar_status_pedido(request, pedido_id, novo_status):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    pedido.status = novo_status
    pedido.save()
    return redirect('produtos:painel_dono')

def imprimir_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    return render(request, 'produtos/imprimir_cupom.html', {'pedido': pedido})

@login_required
def caderno_gestao(request):
    # Captura o filtro da URL (o padrão será 'hoje' se nada for enviado)
    periodo = request.GET.get('periodo', 'hoje')
    agora = timezone.now()

    # Define a data de início com base no filtro selecionado
    if periodo == 'hoje':
        data_inicial = agora.replace(hour=0, minute=0, second=0, microsecond=0)
    elif periodo == 'semana':
        data_inicial = agora - timedelta(days=7)
    elif periodo == 'mes':
        data_inicial = agora - timedelta(days=30)
    elif periodo == 'ano':
        data_inicial = agora - timedelta(days=365)
    else:  # 'tudo'
        data_inicial = agora - timedelta(days=3650)

    # Filtra os pedidos finalizados a partir da data definida acima
    pedidos_base = Pedido.objects.filter(status='finalizado', data_pedido__gte=data_inicial)
    pedidos_finalizados = pedidos_base.order_by('-data_pedido')

    # Cálculos para o Placar (Bloco 1)
    faturamento_total = pedidos_finalizados.aggregate(Sum('total'))['total__sum'] or 0
    total_pedidos = pedidos_finalizados.count()
    ticket_medio = faturamento_total / total_pedidos if total_pedidos > 0 else 0

    # Rankings (Bloco 2) - Filtrando itens apenas dos pedidos selecionados
    top_produtos = ItemPedido.objects.filter(pedido__in=pedidos_finalizados) \
        .values('produto__nome') \
        .annotate(total_vendido=Sum('quantidade')) \
        .order_by('-total_vendido')[:3]

    top_categorias = ItemPedido.objects.filter(pedido__in=pedidos_finalizados) \
        .values('produto__categoria__nome') \
        .annotate(faturamento=Sum('preco_unitario')) \
        .order_by('-faturamento')[:3]

    contexto = {
        'pedidos': pedidos_finalizados,
        'faturamento_total': faturamento_total,
        'total_pedidos': total_pedidos,
        'ticket_medio': ticket_medio,
        'top_produtos': top_produtos,
        'top_categorias': top_categorias,
        'periodo_selecionado': periodo,
    }
    return render(request, 'produtos/caderno.html', contexto)


def gerenciar_carrinho_ajax(request, produto_id, acao):
    carrinho = request.session.get('carrinho', {})
    produto = get_object_or_404(Produto, id=produto_id)
    id_str = str(produto_id)

    # ADICIONA OU REMOVE
    if acao == 'adicionar':
        if id_str in carrinho:
            carrinho[id_str]['quantidade'] += 1
        else:
            carrinho[id_str] = {'nome': produto.nome, 'preco': str(produto.preco), 'quantidade': 1}
    elif acao == 'remover':
        if id_str in carrinho:
            if carrinho[id_str]['quantidade'] > 1:
                carrinho[id_str]['quantidade'] -= 1
            else:
                del carrinho[id_str]

    # SALVA NA SESSÃO (Essencial!)
    request.session['carrinho'] = carrinho
    request.session.modified = True

    # CALCULA TOTAIS E RENDERIZA O HTML
    itens_detalhados = [{'nome': d['nome'], 'quantidade': d['quantidade'], 'subtotal': float(d['preco']) * d['quantidade']} for id_i, d in carrinho.items()]
    total_carrinho = sum(item['subtotal'] for item in itens_detalhados)

    html_lista = render_to_string('produtos/includes/resumo_itens.html', {'itens_carrinho': itens_detalhados})

    return JsonResponse({
        'sucesso': True,
        'html': html_lista,
        'total': f"R$ {total_carrinho:.2f}"
    })