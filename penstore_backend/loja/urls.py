from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView,
    CustomLoginView,
    CustomLogoutView,
    GenerateTOTPView,
    VerifyTOTPSetupView,
    DisableTOTPView,
    ProdutoViewSet,
    ProfileViewSet,
    PedidoViewSet,
    EnderecoViewSet,
    UserListView
)

router = DefaultRouter()
router.register(r'produtos', ProdutoViewSet, basename='produto')
router.register(r'perfis', ProfileViewSet, basename='profile')
router.register(r'pedidos', PedidoViewSet, basename='pedido')
router.register(r'enderecos', EnderecoViewSet, basename='endereco')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('2fa/generate/', GenerateTOTPView.as_view(), name='generate-totp'),
    path('2fa/verify/', VerifyTOTPSetupView.as_view(), name='verify-totp'),
    path('2fa/disable/', DisableTOTPView.as_view(), name='disable-totp'),
]