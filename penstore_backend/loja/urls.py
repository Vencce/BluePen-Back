from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView,
    CustomLoginView,
    ProdutoViewSet,
    PedidoViewSet,
    EnderecoViewSet,
    ProfileViewSet,
    UserListView,
)

router = DefaultRouter()
router.register(r'produtos', ProdutoViewSet, basename='produto')
router.register(r'profile', ProfileViewSet, basename='profile')
router.register(r'pedidos', PedidoViewSet, basename='pedido')
router.register(r'enderecos', EnderecoViewSet, basename='endereco')

urlpatterns = [
    path('cadastro/', RegisterView.as_view(), name='cadastro'),
    path('login/', CustomLoginView.as_view(), name='api-login'),
    path('usuarios/', UserListView.as_view(), name='user-list'),
    path('', include(router.urls)),
]