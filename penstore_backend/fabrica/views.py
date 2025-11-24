from rest_framework import generics, permissions, status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import (
    Fornecedor, Insumo, LogEstoqueDiario, Maquina,
    MovimentoInsumo, MovimentoProdutoAcabado, PedidoCompra,
    ItemPedidoCompra, OrdemProducao, ControleQualidade,
    Venda, FluxoCaixa
)
from loja.models import Produto
from .serializers import (
    FornecedorSerializer, InsumoSerializer, LogEstoqueDiarioSerializer,
    MaquinaSerializer, MovimentoInsumoSerializer, MovimentoProdutoAcabadoSerializer,
    PedidoCompraSerializer, ItemPedidoCompraSerializer, OrdemProducaoSerializer,
    ControleQualidadeSerializer, VendaSerializer, FluxoCaixaSerializer
)

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

class ProcessarCustosEstoqueView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        hoje = timezone.now().date()
        
        # Verifica se já rodou hoje para evitar duplicidade (opcional, mas recomendado)
        ja_processado = FluxoCaixa.objects.filter(
            categoria='DEPRECIACAO', # Ou ESTOCAGEM
            data_lancamento=hoje,
            descricao__startswith="Custo Diário de Estocagem"
        ).exists()

        if ja_processado:
            return Response({"message": "Custos de hoje já foram processados."}, status=status.HTTP_400_BAD_REQUEST)

        produtos = Produto.objects.all()
        total_custo = 0
        detalhes = []

        for produto in produtos:
            estoque = produto.estoque_atual
            if estoque > 0:
                custo_produto = estoque * 0.02 # R$ 0,02 por caneta
                total_custo += float(custo_produto)
                detalhes.append(f"{produto.nome}: {estoque} un x 0.02")

        if total_custo > 0:
            FluxoCaixa.objects.create(
                tipo='SAIDA',
                categoria='DEPRECIACAO', # Pode criar essa categoria no model se não existir, ou usar OUTROS
                descricao=f"Custo Diário de Estocagem ({hoje})",
                valor=total_custo,
                data_lancamento=hoje
            )
            return Response({
                "message": "Custos processados com sucesso.",
                "total": total_custo,
                "detalhes": detalhes
            }, status=status.HTTP_200_OK)
        
        return Response({"message": "Estoque zerado, nenhum custo gerado."}, status=status.HTTP_200_OK)