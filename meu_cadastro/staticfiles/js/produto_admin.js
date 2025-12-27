// produtos/static/js/produto_admin.js
(function($) {
    $(document).ready(function() {
        console.log('Script produto_admin.js carregado!');

        // Quando a categoria muda, atualiza as subcategorias
        $('#id_categoria').change(function() {
            var categoriaId = $(this).val();
            console.log('Categoria selecionada:', categoriaId);

            var subcategoriaSelect = $('#id_subcategoria');
            subcategoriaSelect.empty();

            if (categoriaId) {
                subcategoriaSelect.append($('<option>').val('').text('Carregando...'));

                $.ajax({
                    url: '/produtos/admin/get_subcategorias/',
                    data: {'categoria_id': categoriaId},
                    success: function(data) {
                        console.log('Subcategorias:', data);
                        subcategoriaSelect.empty();
                        subcategoriaSelect.append($('<option>').val('').text('---------'));

                        if (data.length > 0) {
                            $.each(data, function(index, item) {
                                subcategoriaSelect.append(
                                    $('<option>').val(item.id).text(item.nome)
                                );
                            });
                        } else {
                            subcategoriaSelect.append(
                                $('<option>').val('').text('Nenhuma subcategoria')
                            );
                        }
                    },
                    error: function() {
                        subcategoriaSelect.empty();
                        subcategoriaSelect.append($('<option>').val('').text('Erro ao carregar'));
                    }
                });
            } else {
                subcategoriaSelect.append($('<option>').val('').text('---------'));
            }
        });

        // Executa ao carregar se já tiver categoria
        if ($('#id_categoria').val()) {
            $('#id_categoria').trigger('change');
        }
    });
})(django.jQuery);