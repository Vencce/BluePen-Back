from django.db import models
from django.conf import settings 
from loja.models import Produto
from datetime import date

class Maquina(models.Model):
    STATUS_MAQUINA_CHOICES = [('OPERACIONAL', 'Operacional'), ('MANUTENCAO', 'Em Manutenção'), ('INOPERANTE', 'Inoperante')]
    nome = models.CharField(max_length=100, unique=True, default='Maquina Padrao')
    modelo = models.CharField(max_length=100)
    custo_aquisicao = models.DecimalField(max_digits=10, decimal_places=2)
    data_aquisicao = models.DateField(default=date.today)
    capacidade_dia = models.IntegerField(default=500)
    depreciacao_anual_percentual = models.DecimalField(max_digits=5, decimal_places=2, default=30.00)
    status_operacional = models.CharField(max_length=15, choices=STATUS_MAQUINA_CHOICES, default='OPERACIONAL')
    capacidade_producao_hora = models.IntegerField(default=500)
    def __str__(self): return self.nome

class Fornecedor(models.Model):
    nome = models.CharField(max_length=100)
    cnpj = models.CharField(max_length=18, unique=True, blank=True, null=True) 
    telefone = models.CharField(max_length=20, blank=True, null=True) 
    email = models.EmailField(blank=True, null=True) 
    contato = models.CharField(max_length=100, blank=True, null=True)
    lead_time_medio_dias = models.IntegerField(default=0)
    def __str__(self): return self.nome

class Insumo(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    codigo = models.CharField(max_length=50, unique=True, blank=True, null=True) 
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.SET_NULL, null=True, blank=True, related_name='insumos_fornecidos')
    custo_unitario = models.DecimalField(max_digits=10, decimal_places=4)
    estoque_minimo = models.IntegerField(default=5000)
    unidade_medida = models.CharField(max_length=10, default='un')
    quantidade_estoque = models.IntegerField(default=0) 
    def __str__(self): return f"{self.nome} ({self.quantidade_estoque} {self.unidade_medida})"

class MovimentoInsumo(models.Model):
    TIPO_CHOICES = [('ENTRADA', 'Entrada'), ('SAIDA', 'Saída')]
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE, related_name='movimentos_insumo') 
    data_hora = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=7, choices=TIPO_CHOICES)
    quantidade = models.IntegerField()
    custo_unitario_movimento = models.DecimalField(max_digits=10, decimal_places=4, default=0.0)
    referencia_tabela = models.CharField(max_length=50, blank=True, null=True)
    referencia_id = models.IntegerField(blank=True, null=True)
    def __str__(self): return f"{self.tipo} - {self.insumo.nome}"

class MovimentoProdutoAcabado(models.Model):
    TIPO_CHOICES = [('ENTRADA', 'Entrada'), ('SAIDA', 'Saída')]
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='movimentos_produto_acabado')
    data_hora = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=7, choices=TIPO_CHOICES)
    quantidade = models.IntegerField()
    custo_producao_unitario = models.DecimalField(max_digits=10, decimal_places=4)
    referencia_tabela = models.CharField(max_length=50, blank=True, null=True)
    referencia_id = models.IntegerField(blank=True, null=True)
    def __str__(self): return f"{self.tipo} - {self.produto.nome}"

class PedidoCompra(models.Model):
    STATUS_CHOICES = [('PENDENTE', 'Pendente'), ('RECEBIDO_TOTAL', 'Recebido Totalmente'), ('CANCELADO', 'Cancelado')]
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.CASCADE, related_name='pedidos')
    data_pedido = models.DateField(auto_now_add=True)
    valor_total_pedido = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDENTE')
    def __str__(self): return f"Pedido {self.id} - {self.fornecedor.nome}"

class ItemPedidoCompra(models.Model):
    pedido_compra = models.ForeignKey(PedidoCompra, on_delete=models.CASCADE, related_name='itens_pedido_compra')
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE, related_name='itens_pedido')
    quantidade = models.IntegerField()
    custo_unitario_compra = models.DecimalField(max_digits=10, decimal_places=4) 
    
    def save(self, *args, **kwargs):
        if not self.custo_unitario_compra or self.custo_unitario_compra == 0:
            if self.insumo and self.insumo.custo_unitario:
                self.custo_unitario_compra = self.insumo.custo_unitario
        super().save(*args, **kwargs)

    def __str__(self): return f"{self.insumo.nome} ({self.quantidade})"

class OrdemProducao(models.Model):
    STATUS_CHOICES = [('PLANEJADA', 'Planejada'), ('EM_ANDAMENTO', 'Em andamento'), ('CONCLUIDA', 'Concluída'), ('INSPECIONADA', 'Inspecionada')]
    produto_acabado = models.ForeignKey(Produto, on_delete=models.PROTECT, related_name='ordens_producao', verbose_name="Produto a Produzir")
    data_inicio_prevista = models.DateField()
    quantidade_produzir = models.IntegerField() 
    data_conclusao_real = models.DateTimeField(blank=True, null=True)
    maquina = models.ForeignKey(Maquina, on_delete=models.CASCADE, related_name='ordens')
    funcionario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='ordens_producao_responsavel')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANEJADA')
    observacoes = models.TextField(blank=True, null=True)
    def __str__(self): return f"Ordem {self.id} - {self.status}"

class ControleQualidade(models.Model):
    STATUS_CQ_CHOICES = [('PENDENTE', 'Pendente'), ('APROVADO', 'Aprovado'), ('REPROVADO', 'Reprovado')]

    ordem_producao = models.OneToOneField(OrdemProducao, on_delete=models.CASCADE, related_name='controle_qualidade')
    data_inspecao = models.DateTimeField(auto_now_add=True) 
    quantidade_aprovada = models.IntegerField(default=0)
    quantidade_rejeitada = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CQ_CHOICES, default='PENDENTE')
    inspetor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='inspecoes_realizadas')
    observacoes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Controle #{self.id} - Ordem {self.ordem_producao.id} ({self.status})"

class Venda(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='vendas_fabrica') 
    data_venda = models.DateTimeField(auto_now_add=True)
    quantidade = models.IntegerField()
    valor_unitario_praticado = models.DecimalField(max_digits=10, decimal_places=4)
    valor_total_venda = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self): return f"Venda {self.id} - {self.produto.nome}"

class FluxoCaixa(models.Model):
    TIPO_CHOICES = [('ENTRADA', 'Entrada'), ('SAIDA', 'Saída')]
    CATEGORIA_CHOICES = [('VENDA', 'Venda'), ('INSUMO', 'Insumo'), ('SALARIO', 'Salário'), ('CAPITAL_INICIAL', 'Capital Inicial'), ('OUTROS', 'Outros')]
    data_lancamento = models.DateField(default=date.today)
    descricao = models.TextField()
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    categoria = models.CharField(max_length=30, choices=CATEGORIA_CHOICES)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    referencia_id = models.IntegerField(blank=True, null=True)
    referencia_tabela = models.CharField(max_length=50, blank=True, null=True)
    def __str__(self): return f"{self.tipo} - {self.categoria} ({self.valor})"

class LogEstoqueDiario(models.Model):
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE, related_name='logs_estoque')
    data = models.DateField(default=date.today)
    quantidade_inicial = models.IntegerField(default=0) 
    quantidade_final = models.IntegerField(default=0)
    custo_estocagem_dia = models.DecimalField(max_digits=10, decimal_places=2)
    lancado_financeiro = models.BooleanField(default=False)
    movimentos = models.TextField(blank=True, null=True)
    def __str__(self): return f"{self.data} - {self.insumo.nome}"