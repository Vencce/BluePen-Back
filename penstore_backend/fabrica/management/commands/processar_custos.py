from django.core.management.base import BaseCommand
from django.utils import timezone
from fabrica.models import FluxoCaixa
from loja.models import Produto

class Command(BaseCommand):
    help = 'Calcula e registra o custo de estocagem diário automaticamente. Ideal para rodar via Cron/Agendador.'

    def handle(self, *args, **options):
        hoje = timezone.now().date()
        
        self.stdout.write(f"--- Iniciando rotina de custos para: {hoje} ---")

        if FluxoCaixa.objects.filter(
            categoria='DEPRECIACAO', 
            data_lancamento=hoje, 
            descricao__startswith="Custo Diário"
        ).exists():
            self.stdout.write(self.style.WARNING(f"AVISO: Custos de {hoje} já foram processados. Abortando para evitar duplicidade."))
            return

        produtos = Produto.objects.all()
        total_custo = 0
        itens_com_estoque = 0

        for produto in produtos:
            estoque = produto.estoque_atual
            if estoque > 0:
                custo_item = estoque * 0.02
                total_custo += float(custo_item)
                itens_com_estoque += 1
                self.stdout.write(f" - {produto.nome}: {estoque} un -> R$ {custo_item:.2f}")

        if total_custo > 0:
            FluxoCaixa.objects.create(
                tipo='SAIDA',
                categoria='DEPRECIACAO',
                descricao=f"Custo Diário de Estocagem ({hoje})",
                valor=total_custo,
                data_lancamento=hoje,
                referencia_tabela='RotinaAutomatica'
            )
            self.stdout.write(self.style.SUCCESS(f"SUCESSO: Lançamento de R$ {total_custo:.2f} criado."))
        else:
            self.stdout.write(self.style.SUCCESS("Estoque zerado. Nenhum custo gerado hoje."))