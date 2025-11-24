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

        user = authenticate(request, username=username, password=password)

        if user:
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
                print(f"Pedido {pedido_id} marcado como 'entregue' automaticamente.")
        except Pedido.DoesNotExist:
            print(f"Timer: Pedido {pedido_id} não encontrado.")
        except Exception as e:
            print(f"Timer: Erro ao atualizar pedido {pedido_id}: {e}")

    def update(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response(status=status.HTTP_403_FORBIDDEN)
            
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        novo_status = request.data.get('status')

        if novo_status == 'enviado' and instance.status != 'enviado':
            print(f"Iniciando timer de 2 minutos para Pedido {instance.id}")
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