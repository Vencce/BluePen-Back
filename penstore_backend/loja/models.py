from django.db import models
from django.contrib.auth.models import User

class Produto(models.Model):
    nome = models.CharField(max_length=255)
    preco = models.DecimalField(max_digits=10, decimal_places=2) 
    imagem = models.ImageField(upload_to='produtos/', blank=True, null=True)
    
    custo_base_producao_unitario = models.DecimalField(max_digits=10, decimal_places=4, default=0.0000)
    preco_venda_unitario_fabrica = models.DecimalField(max_digits=10, decimal_places=4, default=0.0000)

    def __str__(self): return self.nome
    
    @property
    def estoque_atual(self):
        from fabrica.models import MovimentoProdutoAcabado 

        entradas = self.movimentos_produto_acabado.filter(tipo='ENTRADA').aggregate(
            total=models.Sum('quantidade')
        )['total'] or 0
        
        saidas = self.movimentos_produto_acabado.filter(tipo='SAIDA').aggregate(
            total=models.Sum('quantidade')
        )['total'] or 0
        
        return entradas - saidas


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) 
    telefone = models.CharField(max_length=20, blank=True)
    data_nascimento = models.DateField(null=True, blank=True)
    def __str__(self): return self.user.username

class Pedido(models.Model):
    STATUS_CHOICES = (
        ('pendente', 'Pendente'), 
        ('aprovado', 'Aprovado'), 
        ('enviado', 'Enviado'), 
        ('cancelado', 'Cancelado'),
        ('entregue', 'Entregue')
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    total_pedido = models.DecimalField(max_digits=10, decimal_places=2, default=0) 
    metodo_pagamento = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    endereco_cep = models.CharField(max_length=10)
    endereco_rua = models.CharField(max_length=255)
    endereco_numero = models.CharField(max_length=20)
    endereco_complemento = models.CharField(max_length=100, blank=True, null=True)
    endereco_bairro = models.CharField(max_length=100)
    endereco_cidade = models.CharField(max_length=100)
    endereco_estado = models.CharField(max_length=5)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f'Pedido {self.id} - {self.user.username if self.user else "Convidado"}'

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='itens', on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.SET_NULL, null=True)
    quantidade = models.IntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2) 
    def __str__(self): return f'{self.quantidade}x {self.produto.nome if self.produto else "Produto Removido"}'
    def get_total_item(self):
        if self.preco_unitario is not None and self.quantidade is not None:
            return self.preco_unitario * self.quantidade
        return 0
    
class Endereco(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enderecos')
    apelido = models.CharField(max_length=100, help_text="Ex: Casa, Trabalho")
    cep = models.CharField(max_length=10)
    rua = models.CharField(max_length=255)
    numero = models.CharField(max_length=20)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2, help_text="UF (ex: SC)")
    is_principal = models.BooleanField(default=False, help_text="Marcar como endereço principal")

    class Meta:
        verbose_name = "Endereço"
        verbose_name_plural = "Endereços"
        unique_together = ('user', 'apelido') 

    def __str__(self):
        return f"{self.apelido} ({self.user.username}) - {self.rua}, {self.numero}"