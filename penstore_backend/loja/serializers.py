from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Produto, Profile, Pedido, ItemPedido, Endereco
from django.db import transaction

class RegisterSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True, 'allow_blank': False} 
        }
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "As senhas não conferem."})
        return data
    def create(self, validated_data):
        validated_data.pop('password_confirm') 
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''), 
            password=validated_data['password']
        )
        Profile.objects.create(user=user)
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_superuser']
        read_only_fields = ['id', 'username', 'is_superuser']

class ProdutoSerializer(serializers.ModelSerializer):
    estoque = serializers.IntegerField(source='estoque_atual', read_only=True) 

    class Meta:
        model = Produto
        fields = ['id', 'nome', 'preco', 'estoque', 
                  'custo_base_producao_unitario', 'preco_venda_unitario_fabrica']
        read_only_fields = ['id', 'estoque'] 

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True) 
    
    class Meta:
        model = Profile
        fields = ['id', 'user', 'telefone', 'data_nascimento']
        read_only_fields = ['id', 'user']

class ItemPedidoSerializer(serializers.ModelSerializer):
    produto_id = serializers.PrimaryKeyRelatedField(
        queryset=Produto.objects.all(), source='produto', write_only=True
    )
    produto = ProdutoSerializer(read_only=True) 
    class Meta:
        model = ItemPedido
        fields = ['id', 'produto', 'produto_id', 'quantidade', 'preco_unitario']
        read_only_fields = ['id', 'produto', 'preco_unitario']

class PedidoSerializer(serializers.ModelSerializer):
    itens = ItemPedidoSerializer(many=True) 
    user = UserSerializer(read_only=True) 
    class Meta:
        model = Pedido
        fields = [
            'id', 'user', 'total_pedido', 'metodo_pagamento', 'status', 
            'endereco_cep', 'endereco_rua', 'endereco_numero', 'endereco_complemento', 
            'endereco_bairro', 'endereco_cidade', 'endereco_estado', 
            'created_at', 'itens'
        ]
        read_only_fields = ['id', 'user', 'total_pedido', 'status', 'created_at']

    def create(self, validated_data):
        itens_data = validated_data.pop('itens') 
        with transaction.atomic():
            pedido = Pedido.objects.create(**validated_data) 
            total_calculado = 0
            try: 
                for item_data in itens_data:
                    produto = item_data['produto'] 
                    quantidade = item_data['quantidade']
                    if quantidade <= 0:
                         raise serializers.ValidationError(f'Quantidade inválida para {produto.nome}.')
                    if produto.estoque_atual < quantidade: 
                        raise serializers.ValidationError(
                            f'Estoque insuficiente para {produto.nome}. Disponível: {produto.estoque_atual}, Solicitado: {quantidade}'
                        )
                    from fabrica.models import MovimentoProdutoAcabado
                    MovimentoProdutoAcabado.objects.create(
                        produto=produto,
                        tipo='SAIDA',
                        quantidade=quantidade,
                        custo_producao_unitario=produto.custo_base_producao_unitario,
                        referencia_tabela='Pedido Loja',
                        referencia_id=pedido.id
                    )
                    
                    ItemPedido.objects.create(
                        pedido=pedido, 
                        produto=produto, 
                        quantidade=quantidade,
                        preco_unitario=produto.preco 
                    )
                    
                    total_calculado += (produto.preco * quantidade)
                pedido.total_pedido = total_calculado
                pedido.save(update_fields=['total_pedido']) 
            except serializers.ValidationError as e:
                raise e 
            except Exception as e:
                 pedido.delete()
                 print(f"Erro inesperado ao processar itens do pedido: {e}") 
                 raise serializers.ValidationError("Erro interno ao processar itens do pedido.")
        return pedido

class PedidoAdminSerializer(serializers.ModelSerializer):
    itens = ItemPedidoSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Pedido
        fields = [
            'id', 'user', 'total_pedido', 'metodo_pagamento', 'status', 
            'endereco_cep', 'endereco_rua', 'endereco_numero', 'endereco_complemento', 
            'endereco_bairro', 'endereco_cidade', 'endereco_estado', 
            'created_at', 'itens'
        ]
        read_only_fields = [
            'id', 'user', 'total_pedido', 'created_at', 'itens', 
            'metodo_pagamento', 'endereco_cep', 'endereco_rua', 
            'endereco_numero', 'endereco_complemento', 'endereco_bairro', 
            'cidade', 'estado'
        ]
    
class EnderecoSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Endereco
        fields = [
            'id', 'user', 'apelido', 'cep', 'rua', 'numero', 
            'complemento', 'bairro', 'cidade', 'estado', 'is_principal'
        ]
        read_only_fields = ['id', 'user']
    
    def validate(self, data):
        user = self.context['request'].user
        if self.instance:
            if Endereco.objects.filter(user=user, apelido=data['apelido']).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError({'apelido': 'Você já tem um endereço com este apelido.'})
        else:
            if Endereco.objects.filter(user=user, apelido=data['apelido']).exists():
                raise serializers.ValidationError({'apelido': 'Você já tem um endereço com este apelido.'})
        return data

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)