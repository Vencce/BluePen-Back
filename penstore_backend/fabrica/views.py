# fabrica/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models import (
    Fornecedor, Insumo, LogEstoqueDiario, Maquina,
    MovimentoInsumo, MovimentoProdutoAcabado, PedidoCompra,
    ItemPedidoCompra, OrdemProducao, ControleQualidade,
    Venda, FluxoCaixa
)
from .serializers import (
    FornecedorSerializer, InsumoSerializer, LogEstoqueDiarioSerializer,
    MaquinaSerializer, MovimentoInsumoSerializer, MovimentoProdutoAcabadoSerializer,
    PedidoCompraSerializer, ItemPedidoCompraSerializer, OrdemProducaoSerializer,
    ControleQualidadeSerializer, VendaSerializer, FluxoCaixaSerializer
)

# Views para API REST

class FornecedorViewSet(viewsets.ModelViewSet):
    queryset = Fornecedor.objects.all()
    serializer_class = FornecedorSerializer
    permission_classes = [IsAuthenticated]

class InsumoViewSet(viewsets.ModelViewSet):
    queryset = Insumo.objects.all()
    serializer_class = InsumoSerializer
    permission_classes = [IsAuthenticated]

class LogEstoqueDiarioViewSet(viewsets.ModelViewSet):
    queryset = LogEstoqueDiario.objects.all()
    serializer_class = LogEstoqueDiarioSerializer
    permission_classes = [IsAuthenticated]

class MaquinaViewSet(viewsets.ModelViewSet):
    queryset = Maquina.objects.all()
    serializer_class = MaquinaSerializer
    permission_classes = [IsAuthenticated]

class MovimentoInsumoViewSet(viewsets.ModelViewSet):
    queryset = MovimentoInsumo.objects.all()
    serializer_class = MovimentoInsumoSerializer
    permission_classes = [IsAuthenticated]

class MovimentoProdutoAcabadoViewSet(viewsets.ModelViewSet):
    queryset = MovimentoProdutoAcabado.objects.all()
    serializer_class = MovimentoProdutoAcabadoSerializer
    permission_classes = [IsAuthenticated]

class PedidoCompraViewSet(viewsets.ModelViewSet):
    queryset = PedidoCompra.objects.all()
    serializer_class = PedidoCompraSerializer
    permission_classes = [IsAuthenticated]

class ItemPedidoCompraViewSet(viewsets.ModelViewSet):
    queryset = ItemPedidoCompra.objects.all()
    serializer_class = ItemPedidoCompraSerializer
    permission_classes = [IsAuthenticated]

class OrdemProducaoViewSet(viewsets.ModelViewSet):
    queryset = OrdemProducao.objects.all()
    serializer_class = OrdemProducaoSerializer
    permission_classes = [IsAuthenticated]

class ControleQualidadeViewSet(viewsets.ModelViewSet):
    queryset = ControleQualidade.objects.all()
    serializer_class = ControleQualidadeSerializer
    permission_classes = [IsAuthenticated]

class VendaViewSet(viewsets.ModelViewSet):
    queryset = Venda.objects.all()
    serializer_class = VendaSerializer
    permission_classes = [IsAuthenticated]

class FluxoCaixaViewSet(viewsets.ModelViewSet):
    queryset = FluxoCaixa.objects.all()
    serializer_class = FluxoCaixaSerializer
    permission_classes = [IsAuthenticated]