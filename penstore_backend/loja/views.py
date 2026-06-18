from rest_framework import generics, permissions, status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import get_object_or_404

import threading
import time
import pyotp

from .models import Produto, Profile, Pedido, ItemPedido, Endereco
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    ProdutoSerializer,
    ProfileSerializer,
    PedidoSerializer,
    PedidoAdminSerializer,
    ItemPedidoSerializer,
    EnderecoSerializer
)
from fabrica.models import MovimentoProdutoAcabado 

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class CustomLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        totp_code = request.data.get('totp_code')

        user = authenticate(request, username=username, password=password)

        if user:
            try:
                profile = user.profile
            except Profile.DoesNotExist:
                profile = Profile.objects.create(user=user)

            if profile.is_2fa_enabled:
                if not totp_code:
                    return Response({'requires_2fa': True}, status=status.HTTP_200_OK)
                
                totp = pyotp.TOTP(profile.totp_secret)
                if not totp.verify(totp_code):
                    return Response({'error': 'Código 2FA inválido'}, status=status.HTTP_400_BAD_REQUEST)

            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.pk,
                'username': user.username,
                'email': user.email,
                'is_superuser': user.is_superuser
            })
        return Response({'error': 'Credenciais inválidas'}, status=status.HTTP_400_BAD_REQUEST)

class CustomLogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            request.user.auth_token.delete()
            return Response({'message': 'Logout realizado com sucesso.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GenerateTOTPView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        profile, created = Profile.objects.get_or_create(user=request.user)
        
        if not profile.totp_secret:
            profile.totp_secret = pyotp.random_base32()
            profile.save()

        totp = pyotp.TOTP(profile.totp_secret)
        provisioning_uri = totp.provisioning_uri(name=request.user.email or request.user.username, issuer_name="BluePen")

        return Response({
            'secret': profile.totp_secret,
            'provisioning_uri': provisioning_uri
        })

class VerifyTOTPSetupView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        totp_code = request.data.get('totp_code')
        profile = get_object_or_404(Profile, user=request.user)

        if not profile.totp_secret:
            return Response({'error': 'Segredo TOTP não gerado'}, status=status.HTTP_400_BAD_REQUEST)

        totp = pyotp.TOTP(profile.totp_secret)
        if totp.verify(totp_code):
            profile.is_2fa_enabled = True
            profile.save()
            return Response({'message': '2FA ativado com sucesso'})
        
        return Response({'error': 'Código inválido'}, status=status.HTTP_400_BAD_REQUEST)

class DisableTOTPView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        profile.is_2fa_enabled = False
        profile.totp_secret = None
        profile.save()
        return Response({'message': '2FA desativado com sucesso'})

class ProdutoViewSet(viewsets.ModelViewSet):
    queryset = Produto.objects.all().order_by('nome')
    serializer_class = ProdutoSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [permissions.IsAdminUser]
        else: 
            self.permission_classes = [permissions.AllowAny]
        return super().get_permissions()

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Profile.objects.all()
        return Profile.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.is_superuser or instance.user == request.user:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        return Response(status=status.HTTP_403_FORBIDDEN)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.is_superuser or instance.user == request.user:
            return super().update(request, *args, **kwargs)
        return Response(status=status.HTTP_403_FORBIDDEN)
    
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.is_superuser or instance.user == request.user:
            return super().partial_update(request, *args, **kwargs)
        return Response(status=status.HTTP_403_FORBIDDEN)


class PedidoViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Pedido.objects.all().order_by('-created_at')
        return Pedido.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        with transaction.atomic():
            serializer.save(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PedidoSerializer
        
        if self.request and self.request.user.is_superuser:
            return PedidoAdminSerializer
            
        return PedidoSerializer

    def _marcar_como_entregue(self, pedido_id):
        try:
            time.sleep(60)
            pedido = Pedido.objects.get(id=pedido_id)
            if pedido.status == 'enviado':
                pedido.status = 'entregue'
                pedido.save(update_fields=['status'])
        except Pedido.DoesNotExist:
            pass
        except Exception as e:
            pass

    def update(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)
            
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        novo_status = request.data.get('status')

        if novo_status == 'enviado' and instance.status != 'enviado':
            timer = threading.Timer(120.0, self._marcar_como_entregue, [instance.id])
            timer.start()
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

class EnderecoViewSet(viewsets.ModelViewSet):
    serializer_class = EnderecoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Endereco.objects.filter(user=self.request.user).order_by('apelido')

    def perform_create(self, serializer):
        if not Endereco.objects.filter(user=self.request.user).exists():
            serializer.save(user=self.request.user, is_principal=True)
        else:
            serializer.save(user=self.request.user)
    
    def perform_update(self, serializer):
        if serializer.validated_data.get('is_principal') == True:
            Endereco.objects.filter(user=self.request.user).exclude(pk=self.get_object().pk).update(is_principal=False)
        serializer.save()

class UserListView(generics.ListAPIView):
    queryset = User.objects.all().order_by('username')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]