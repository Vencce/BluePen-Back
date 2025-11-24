# fabrica/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'maquinas', views.MaquinaViewSet)
router.register(r'fornecedores', views.FornecedorViewSet)
router.register(r'insumos', views.InsumoViewSet)
router.register(r'movimentos-insumo', views.MovimentoInsumoViewSet)
router.register(r'movimentos-produto', views.MovimentoProdutoAcabadoViewSet)
router.register(r'pedidos-compra', views.PedidoCompraViewSet)
router.register(r'itens-pedido', views.ItemPedidoCompraViewSet)
router.register(r'ordens-producao', views.OrdemProducaoViewSet)
router.register(r'controle-qualidade', views.ControleQualidadeViewSet)
router.register(r'vendas', views.VendaViewSet)
router.register(r'fluxo-caixa', views.FluxoCaixaViewSet)
router.register(r'logs-estoque', views.LogEstoqueDiarioViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('custos-diarios/processar/', views.ProcessarCustosEstoqueView.as_view(), name='processar-custos'),
]