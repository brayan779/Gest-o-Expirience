from django.shortcuts import render, redirect, get_object_or_404
from .models import Produto, Categoria, Pedido, ItemPedido
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.contrib import messages


def home_conveniencia(request):
    # 1. Busca categorias pai (sem pai) e produtos disponíveis
    categorias_pai = Categoria.objects.filter(pai__isnull=True).order_by('ordem', 'nome')

    # 2. Busca parâmetros da URL
    categoria_pai_id = request.GET.get('categoria_pai')
    subcategoria_id = request.GET.get('subcategoria')

    # 3. Inicializa variáveis
    produtos = Produto.objects.filter(disponivel=True)
    categoria_pai_selecionada = None
    subcategoria_selecionada = None

    # 4. Filtra por categoria pai (se especificada)
    if categoria_pai_id:
        try:
            categoria_pai_selecionada = Categoria.objects.get(id=categoria_pai_id, pai__isnull=True)

            # Se também tem subcategoria específica
            if subcategoria_id:
                subcategoria_selecionada = Categoria.objects.get(
                    id=subcategoria_id,
                    pai=categoria_pai_selecionada
                )
                produtos = produtos.filter(categoria=subcategoria_selecionada)
            else:
                # Filtra produtos das subcategorias desta categoria pai
                subcategorias_ids = categoria_pai_selecionada.subcategorias.values_list('id', flat=True)
                produtos = produtos.filter(categoria_id__in=subcategorias_ids)
        except Categoria.DoesNotExist:
            pass

    # 5. Busca subcategorias da categoria pai selecionada (se houver)
    subcategorias = []
    if categoria_pai_selecionada:
        subcategorias = categoria_pai_selecionada.subcategorias.all().order_by('ordem', 'nome')
    elif categorias_pai.exists():
        # Por padrão, pega a primeira categoria pai
        primeira_categoria = categorias_pai.first()
        subcategorias = primeira_categoria.subcategorias.all().order_by('ordem', 'nome')
        subcategorias_ids = subcategorias.values_list('id', flat=True)
        produtos = produtos.filter(categoria_id__in=subcategorias_ids)

    # 6. Organiza produtos por subcategoria para o template
    produtos_por_subcategoria = {}
    for subcat in subcategorias:
        produtos_subcat = produtos.filter(categoria=subcat).order_by('ordem', 'nome')
        if produtos_subcat.exists():
            produtos_por_subcategoria[subcat] = produtos_subcat

    # 7. Carrinho (mantido igual)
    carrinho = request.session.get('carrinho', {})
    total_carrinho = 0
    itens_detalhados = []

    for item_id, dados in carrinho.items():
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
        'categorias_pai': categorias_pai,
        'categoria_pai_selecionada': categoria_pai_selecionada,
        'subcategoria_selecionada': subcategoria_selecionada,
        'subcategorias': subcategorias,
        'produtos_por_subcategoria': produtos_por_subcategoria,
        'produtos': produtos,  # Mantém para compatibilidade
        'itens_carrinho': itens_detalhados,
        'total_carrinho': total_carrinho,
    }

    print("DEBUG VIEW:")  # Para ver no terminal
    print(f"- Categorias Pai: {categorias_pai.count()}")
    print(f"- Subcategorias: {len(subcategorias)}")
    print(f"- Produtos por Subcat: {len(produtos_por_subcategoria)}")

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

        # Criamos o pedido inicial
        novo_pedido = Pedido.objects.create(
            nome_cliente=nome,
            telefone=telefone,
            endereco=endereco,
            total=0
        )

        total_geral = 0
        for item_key, dados in carrinho.items():
            produto = get_object_or_404(Produto, id=dados['produto_id'])
            preco = float(dados['preco'])
            qtd = dados['quantidade']
            sabor = dados.get('sabor', '')

            # SOMA O TOTAL AQUI (Faltava isso!)
            total_geral += preco * qtd

            ItemPedido.objects.create(
                pedido=novo_pedido,
                produto=produto,
                quantidade=qtd,
                preco_unitario=preco,
                sabor_escolhido=sabor  # Salva o sabor no banco
            )

        # ATUALIZA O TOTAL NO PEDIDO
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

    finalizados = Pedido.objects.filter(status='finalizado').order_by('-data_pedido')

    return render(request, 'produtos/painel_dono.html', {
        'novos': novos,
        'confirmados': confirmados,
        'finalizados': finalizados
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

    # Filtra os pedidos REGISTRADOS a partir da data definida acima
    pedidos_base = Pedido.objects.filter(status='registrado', data_pedido__gte=data_inicial)
    pedidos_registrados = pedidos_base.order_by('-data_pedido')

    # Cálculos para o Placar (Bloco 1)
    faturamento_total = pedidos_registrados.aggregate(Sum('total'))['total__sum'] or 0
    total_pedidos = pedidos_registrados.count()
    ticket_medio = faturamento_total / total_pedidos if total_pedidos > 0 else 0

    # Rankings (Bloco 2) - Filtrando itens apenas dos pedidos selecionados
    top_produtos = ItemPedido.objects.filter(pedido__in=pedidos_registrados) \
        .values('produto__nome') \
        .annotate(total_vendido=Sum('quantidade')) \
        .order_by('-total_vendido')[:3]

    top_categorias = ItemPedido.objects.filter(pedido__in=pedidos_registrados) \
        .values('produto__categoria__nome') \
        .annotate(faturamento=Sum('preco_unitario')) \
        .order_by('-faturamento')[:3]

    contexto = {
        'pedidos': pedidos_registrados,
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
    # Buscamos o produto real pelo ID numérico
    produto = get_object_or_404(Produto, id=produto_id)
    sabor_escolhido = request.GET.get('sabor', '')

    # Chave única para diferenciar itens (Ex: "12-Framboesa")
    item_key = f"{produto_id}-{sabor_escolhido}" if sabor_escolhido else str(produto_id)

    if acao == 'adicionar':
        if item_key in carrinho:
            carrinho[item_key]['quantidade'] += 1
        else:
            carrinho[item_key] = {
                'produto_id': str(produto_id), # Guardamos o ID original
                'nome': produto.nome,
                'preco': str(produto.preco),
                'quantidade': 1,
                'sabor': sabor_escolhido
            }
    elif acao == 'remover':
        if item_key in carrinho:
            if carrinho[item_key]['quantidade'] > 1:
                carrinho[item_key]['quantidade'] -= 1
            else:
                del carrinho[item_key]

    request.session['carrinho'] = carrinho
    request.session.modified = True

    # Reconstrução da lista para o HTML
    itens_detalhados = []
    total_carrinho = 0
    for key, dados in carrinho.items():
        subtotal = float(dados['preco']) * dados['quantidade']
        total_carrinho += subtotal
        itens_detalhados.append({
            'produto_id': dados['produto_id'], # ID para o botão remover
            'nome': dados['nome'],
            'sabor': dados.get('sabor', ''),
            'quantidade': dados['quantidade'],
            'subtotal': subtotal
        })

    html_lista = render_to_string('produtos/includes/resumo_itens.html', {
        'itens_carrinho': itens_detalhados
    })

    return JsonResponse({
        'sucesso': True,
        'html': html_lista,
        'total': f"R$ {total_carrinho:.2f}"
    })

def recusar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    # Você pode optar por deletar ou apenas mudar o status para 'recusado'
    # Para limpar o painel totalmente, vamos deletar:
    pedido.delete()
    messages.success(request, f'Pedido #{pedido_id} recusado e removido.')
    return redirect('produtos:painel_dono')


def mudar_status(request, pedido_id, novo_status):
    """Muda o status do pedido sem registrar no caderno"""
    pedido = get_object_or_404(Pedido, id=pedido_id)

    # Status permitidos: 'confirmado', 'finalizado'
    if novo_status in ['confirmado', 'finalizado']:
        pedido.status = novo_status
        pedido.save()
        messages.success(request, f'Pedido #{pedido.id} movido para {novo_status}.')
    else:
        messages.error(request, 'Status inválido.')

    return redirect('produtos:painel_dono')


def registrar_caderno(request, pedido_id):
    """Registra o pedido finalizado no caderno de gestão"""
    pedido = get_object_or_404(Pedido, id=pedido_id, status='finalizado')

    # Muda o status para 'registrado' e NÃO deleta o pedido
    pedido.status = 'registrado'
    pedido.save()

    messages.success(request, f'Pedido #{pedido.id} registrado no caderno com sucesso!')
    return redirect('produtos:painel_dono')  # Redireciona para o caderno de gestão

