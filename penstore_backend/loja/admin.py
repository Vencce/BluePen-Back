from django.contrib import admin
from .models import Produto, Profile, Pedido, ItemPedido, Endereco

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = (
        'nome', 
        'preco', 
        'estoque_atual_admin',
        'custo_base_producao_unitario', 
        'preco_venda_unitario_fabrica'
    )
    search_fields = ('nome',)
    readonly_fields = ('estoque_atual_admin',)
    
    fieldsets = (
        (None, {
            'fields': ('nome', 'preco')
        }),
        ('Informações de Produção/Fábrica', {
            'fields': ('custo_base_producao_unitario', 'preco_venda_unitario_fabrica')
        }),
        ('Estoque (Calculado)', {
            'fields': ('estoque_atual_admin',)
        }),
    )

    def estoque_atual_admin(self, obj):
        return obj.estoque_atual
    
    estoque_atual_admin.short_description = 'Estoque Atual'

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'telefone')
    search_fields = ('user__username',)

class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    raw_id_fields = ('produto',)
    fields = ('produto', 'quantidade', 'preco_unitario') 
    readonly_fields = ('preco_unitario',) 

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_pedido', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'id')
    inlines = [ItemPedidoInline]
    readonly_fields = ('user', 'created_at', 'total_pedido')

@admin.register(Endereco)
class EnderecoAdmin(admin.ModelAdmin):
    list_display = ('user', 'apelido', 'cep', 'cidade', 'estado', 'is_principal')
    list_filter = ('estado', 'is_principal')
    search_fields = ('user__username', 'cep', 'rua', 'cidade')