from django.contrib import admin
from .models import (
    Fornecedor, 
    Insumo, 
    LogEstoqueDiario, 
    Maquina,
    MovimentoInsumo, 
    MovimentoProdutoAcabado,
    PedidoCompra, 
    ItemPedidoCompra,
    OrdemProducao, 
    ControleQualidade,
    Venda, 
    FluxoCaixa,
    ComposicaoProduto
)

@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cnpj', 'telefone', 'email', 'contato', 'lead_time_medio_dias') 
    search_fields = ('nome', 'cnpj')

@admin.register(Insumo)
class InsumoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'codigo', 'fornecedor', 'estoque_minimo', 'quantidade_estoque', 'unidade_medida') 
    list_filter = ('fornecedor', 'unidade_medida')
    search_fields = ('nome', 'codigo')
    
@admin.register(LogEstoqueDiario)
class LogEstoqueDiarioAdmin(admin.ModelAdmin):
    list_display = ('insumo', 'data', 'quantidade_inicial', 'quantidade_final', 'movimentos')
    list_filter = ('insumo', 'data')
    
@admin.register(Maquina)
class MaquinaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'modelo', 'status_operacional', 'capacidade_producao_hora', 'data_aquisicao')
    list_filter = ('status_operacional', 'data_aquisicao')
    search_fields = ('nome', 'modelo')

@admin.register(MovimentoInsumo)
class MovimentoInsumoAdmin(admin.ModelAdmin):
    list_display = ('insumo', 'tipo', 'quantidade', 'data_hora', 'referencia_tabela', 'referencia_id')
    list_filter = ('tipo', 'insumo', 'data_hora')
    search_fields = ('insumo__nome', 'referencia_tabela')

@admin.register(MovimentoProdutoAcabado)
class MovimentoProdutoAcabadoAdmin(admin.ModelAdmin):
    list_display = ('produto', 'tipo', 'quantidade', 'custo_producao_unitario', 'data_hora', 'referencia_tabela', 'referencia_id')
    list_filter = ('tipo', 'produto', 'data_hora')
    search_fields = ('produto__nome', 'referencia_tabela')
    raw_id_fields = ('produto',)

class ItemPedidoCompraInline(admin.TabularInline):
    model = ItemPedidoCompra
    extra = 1 
    fields = ('insumo', 'quantidade', 'custo_unitario_compra')

@admin.register(PedidoCompra)
class PedidoCompraAdmin(admin.ModelAdmin):
    list_display = ('id', 'fornecedor', 'status', 'valor_total_pedido', 'data_pedido')
    list_filter = ('status', 'data_pedido', 'fornecedor')
    search_fields = ('fornecedor__nome',)
    inlines = [ItemPedidoCompraInline]
    
@admin.register(OrdemProducao)
class OrdemProducaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'produto_acabado', 'quantidade_produzir', 'status', 'data_inicio_prevista', 'data_conclusao_real')
    list_filter = ('status', 'data_inicio_prevista', 'maquina', 'funcionario')
    search_fields = ('produto_acabado__nome',) 
    raw_id_fields = ('produto_acabado', 'maquina', 'funcionario',) 

    fields = (
        'produto_acabado', 
        'quantidade_produzir',
        'status',
        'data_inicio_prevista',
        'maquina',
        'funcionario',
        'data_conclusao_real',
        'observacoes'
    )
    
@admin.register(ControleQualidade)
class ControleQualidadeAdmin(admin.ModelAdmin):
    list_display = ('ordem_producao', 'inspetor', 'data_inspecao', 'status', 'observacoes')
    list_filter = ('status', 'inspetor', 'data_inspecao') 
    search_fields = ('ordem_producao__produto_acabado__nome', 'inspetor__username', 'status')
    raw_id_fields = ('ordem_producao', 'inspetor',)

@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ('id', 'produto', 'data_venda', 'quantidade', 'valor_total_venda')
    list_filter = ('produto', 'data_venda')
    search_fields = ('produto__nome',)
    raw_id_fields = ('produto',)

@admin.register(FluxoCaixa)
class FluxoCaixaAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo', 'categoria', 'valor', 'data_lancamento')
    list_filter = ('tipo', 'categoria', 'data_lancamento')
    search_fields = ('descricao',)

@admin.register(ComposicaoProduto)
class ComposicaoProdutoAdmin(admin.ModelAdmin):
    list_display = ('produto', 'insumo', 'quantidade_necessaria')
    list_filter = ('produto',)
    search_fields = ('produto__nome', 'insumo__nome')
    raw_id_fields = ('produto', 'insumo')