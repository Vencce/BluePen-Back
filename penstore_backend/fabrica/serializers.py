# fabrica/serializers.py
from rest_framework import serializers
from django.conf import settings
from django.contrib.auth import get_user_model # Importa get_user_model
from .models import (
    # Funcionario foi removido daqui
    Maquina, Fornecedor, Insumo,
    MovimentoInsumo, MovimentoProdutoAcabado,
    PedidoCompra, ItemPedidoCompra, OrdemProducao,
    ControleQualidade, Venda, FluxoCaixa, LogEstoqueDiario
)
from loja.models import Produto 
from loja.serializers import UserSerializer # Importa UserSerializer da 'loja'

User = get_user_model() # Pega o modelo User

# --- DEFINIÇÃO FALTANDO (A CAUSA DO ERRO) ---
# Serializer de Produto (Leitura)
class ProdutoReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produto
        fields = ['id', 'nome', 'preco']
# ----------------------------------------------

class MaquinaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maquina
        fields = '__all__'

class FornecedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fornecedor
        fields = '__all__'

class InsumoSerializer(serializers.ModelSerializer):
    fornecedor_nome = serializers.SerializerMethodField()
    fornecedor = serializers.PrimaryKeyRelatedField(
        queryset=Fornecedor.objects.all(), write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Insumo
        fields = [
            'id', 'nome', 'codigo', 'fornecedor', 'fornecedor_nome', 
            'unidade_medida', 'quantidade_estoque', 'estoque_minimo', 
            'custo_unitario'
        ]

    def get_fornecedor_nome(self, obj):
        if obj.fornecedor:
            return obj.fornecedor.nome
        return None

class MovimentoInsumoSerializer(serializers.ModelSerializer):
    insumo = InsumoSerializer(read_only=True)
    insumo_id = serializers.PrimaryKeyRelatedField(
        queryset=Insumo.objects.all(), source='insumo', write_only=True
    )
    class Meta:
        model = MovimentoInsumo
        fields = '__all__'

class MovimentoProdutoAcabadoSerializer(serializers.ModelSerializer):
    produto = ProdutoReadSerializer(read_only=True) # Agora 'ProdutoReadSerializer' existe
    produto_id = serializers.PrimaryKeyRelatedField(
        queryset=Produto.objects.all(), source='produto', write_only=True
    )
    class Meta:
        model = MovimentoProdutoAcabado
        fields = ['id', 'produto', 'produto_id', 'data_hora', 'tipo', 'quantidade', 'custo_producao_unitario', 'referencia_tabela', 'referencia_id']
        read_only_fields = ['id', 'produto', 'data_hora']

class ItemPedidoCompraSerializer(serializers.ModelSerializer):
    insumo = InsumoSerializer(read_only=True)
    insumo_id = serializers.PrimaryKeyRelatedField(
        queryset=Insumo.objects.all(), source='insumo', write_only=True
    )
    class Meta:
        model = ItemPedidoCompra
        fields = '__all__'

class PedidoCompraSerializer(serializers.ModelSerializer):
    fornecedor = FornecedorSerializer(read_only=True)
    fornecedor_id = serializers.PrimaryKeyRelatedField(
        queryset=Fornecedor.objects.all(), source='fornecedor', write_only=True
    )
    itens_pedido_compra = ItemPedidoCompraSerializer(many=True, read_only=True) # Corrigido
    class Meta:
        model = PedidoCompra
        fields = '__all__'

class OrdemProducaoSerializer(serializers.ModelSerializer):
    maquina = MaquinaSerializer(read_only=True)
    maquina_id = serializers.PrimaryKeyRelatedField(
        queryset=Maquina.objects.all(), source='maquina', write_only=True, required=False, allow_null=True
    )
    funcionario = UserSerializer(read_only=True) # Usa UserSerializer
    funcionario_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        source='funcionario', 
        write_only=True,
        required=False,
        allow_null=True
    )
    class Meta:
        model = OrdemProducao
        fields = '__all__'

class ControleQualidadeSerializer(serializers.ModelSerializer):
    ordem_producao = OrdemProducaoSerializer(read_only=True)
    ordem_producao_id = serializers.PrimaryKeyRelatedField(
        queryset=OrdemProducao.objects.all(), source='ordem_producao', write_only=True
    )
    inspetor = UserSerializer(read_only=True) # Usa UserSerializer
    inspetor_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        source='inspetor',
        write_only=True,
        required=False,
        allow_null=True
    )
    class Meta:
        model = ControleQualidade
        fields = '__all__'

class VendaSerializer(serializers.ModelSerializer):
    produto = ProdutoReadSerializer(read_only=True) # Agora 'ProdutoReadSerializer' existe
    produto_id = serializers.PrimaryKeyRelatedField(
        queryset=Produto.objects.all(), source='produto', write_only=True
    )
    class Meta:
        model = Venda
        fields = ['id', 'produto', 'produto_id', 'data_venda', 'quantidade', 'valor_unitario_praticado', 'valor_total_venda']
        read_only_fields = ['id', 'produto']

class FluxoCaixaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FluxoCaixa
        fields = '__all__'

class LogEstoqueDiarioSerializer(serializers.ModelSerializer):
    insumo = InsumoSerializer(read_only=True) 
    insumo_id = serializers.PrimaryKeyRelatedField(
        queryset=Insumo.objects.all(), source='insumo', write_only=True
    )
    class Meta:
        model = LogEstoqueDiario
        fields = ['id', 'insumo', 'insumo_id', 'data', 'quantidade_inicial', 'quantidade_final', 'custo_estocagem_dia', 'lancado_financeiro', 'movimentos']
        read_only_fields = ['id', 'insumo']