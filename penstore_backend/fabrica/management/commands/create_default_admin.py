from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import os

class Command(BaseCommand):
    help = 'Cria o superusuário admin de forma não interativa se ele não existir.'

    def handle(self, *args, **options):
        username = os.environ.get('admin')
        email = os.environ.get('admin@gmail.com', '')
        password = os.environ.get('Palmito0072005@')

        if not username or not password:
            self.stdout.write(self.style.WARNING('AVISO: Variáveis de ambiente de superusuário ausentes. Pulando criação automática.'))
            return

        if not User.objects.filter(username=username).exists():
            try:
                User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                self.stdout.write(self.style.SUCCESS(f'Sucesso! Superusuário "{username}" criado automaticamente.'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Erro ao criar superusuário: {e}'))
        else:
            self.stdout.write(self.style.WARNING(f'Superusuário "{username}" já existe. Pulando criação.'))