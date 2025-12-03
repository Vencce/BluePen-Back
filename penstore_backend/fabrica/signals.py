from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import (
    ControleQualidade, MovimentoProdutoAcabado, OrdemProducao,
    PedidoCompra, ItemPedidoCompra, MovimentoInsumo, FluxoCaixa, Insumo,
    ComposicaoProduto
)
from loja.models import Produto, Pedido

@receiver(post_save, sender=ControleQualidade)
def criar_entrada_estoque_apos_aprovacao_cq(sender, instance, created, **kwargs):
    
    # 1. ENTRADA de Produto Acabado (Apenas APROVADO)
    if instance.status == 'APROVADO':
        movimento_existente = MovimentoProdutoAcabado.objects.filter(
            referencia_tabela='ControleQualidade',
            referencia_id=instance.id,
            tipo='ENTRADA'
        ).exists()
        
        if not movimento_existente:
            try:
                ordem_producao = instance.ordem_producao
                produto_final = ordem_producao.produto_acabado
                quantidade_aprovada = instance.quantidade_aprovada
                if quantidade_aprovada > 0:
                    custo = produto_final.custo_base_producao_unitario
                    MovimentoProdutoAcabado.objects.create(
                        produto=produto_final,
                        tipo='ENTRADA',
                        quantidade=quantidade_aprovada,
                        custo_producao_unitario=custo,
                        referencia_tabela='ControleQualidade',
                        referencia_id=instance.id
                    )
                    print(f"Signal (CQ ID: {instance.id}): ENTRADA de {quantidade_aprovada} {produto_final.nome}.")

                if ordem_producao.status != 'CONCLUIDA':
                    ordem_producao.status = 'CONCLUIDA'
                    ordem_producao.save(update_fields=['status'])
                
            except Exception as e:
                print(f"Signal (CQ ID: {instance.id}): ERRO ao criar movimento de produto: {e}")

    # 2. SAIDA de Insumos (Deve ocorrer se APROVADO OU REPROVADO, e apenas uma vez)
    if instance.status in ['APROVADO', 'REPROVADO']:
        insumos_descontados = MovimentoInsumo.objects.filter(
            referencia_tabela='ControleQualidade',
            referencia_id=instance.id,
            tipo='SAIDA'
        ).exists()

        if not insumos_descontados:
            try:
                ordem_producao = instance.ordem_producao
                produto_final = ordem_producao.produto_acabado
                # Consumo total (Aprovado + Rejeitado)
                quantidade_total_produzida = instance.quantidade_aprovada + instance.quantidade_rejeitada
                
                if quantidade_total_produzida > 0:
                    composicao_itens = ComposicaoProduto.objects.filter(produto=produto_final)
                    
                    if not composicao_itens.exists():
                         print(f"Signal (CQ ID: {instance.id}): Aviso - Produto '{produto_final.nome}' não tem Ficha Técnica.")
                    
                    for item in composicao_itens:
                        insumo = item.insumo
                        qtd_consumo = item.quantidade_necessaria * quantidade_total_produzida
                        
                        MovimentoInsumo.objects.create(
                            insumo=insumo,
                            tipo='SAIDA',
                            quantidade=qtd_consumo,
                            custo_unitario_movimento=insumo.custo_unitario,
                            referencia_tabela='ControleQualidade',
                            referencia_id=instance.id
                        )
                        print(f"Signal (CQ ID: {instance.id}): SAIDA de {qtd_consumo} {insumo.nome} (Matéria-Prima).")

            except Exception as e:
                print(f"Signal (CQ ID: {instance.id}): ERRO ao descontar insumos: {e}")


@receiver(post_save, sender=PedidoCompra)
def registrar_compra_insumos_e_fluxo_caixa(sender, instance, created, **kwargs):
    
    if instance.status == 'RECEBIDO_TOTAL': 
        
        financeiro_existente = FluxoCaixa.objects.filter(
            referencia_tabela='PedidoCompra',
            referencia_id=instance.id,
            tipo='SAIDA'
        ).exists()
        
        if not financeiro_existente:
            try:
                FluxoCaixa.objects.create(
                    tipo='SAIDA', 
                    categoria='INSUMO', 
                    descricao=f'Pagamento Pedido de Compra #{instance.id} - {instance.fornecedor.nome}',
                    valor=instance.valor_total_pedido, 
                    data_lancamento=instance.data_pedido,
                    referencia_tabela='PedidoCompra',
                    referencia_id=instance.id
                )
                print(f"Signal (PedidoCompra ID: {instance.id}): Sucesso! Lançamento de SAIDA de R${instance.valor_total_pedido} no Fluxo de Caixa.")
            except Exception as e:
                print(f"Signal (PedidoCompra ID: {instance.id}): ERRO ao lançar no Fluxo de Caixa: {e}")

        itens_do_pedido = instance.itens_pedido_compra.all()
        
        for item in itens_do_pedido:
            movimento_existente = MovimentoInsumo.objects.filter(
                referencia_tabela='ItemPedidoCompra',
                referencia_id=item.id,
                tipo='ENTRADA'
            ).exists()
            
            if not movimento_existente:
                try:
                    MovimentoInsumo.objects.create(
                        insumo=item.insumo,
                        tipo='ENTRADA',
                        quantidade=item.quantidade,
                        custo_unitario_movimento=item.custo_unitario_compra,
                        referencia_tabela='ItemPedidoCompra',
                        referencia_id=item.id
                    )
                    print(f"Signal (ItemPedidoCompra ID: {item.id}): Sucesso! ENTRADA de {item.quantidade} de {item.insumo.nome} no estoque.")
                except Exception as e:
                    print(f"Signal (ItemPedidoCompra ID: {item.id}): ERRO ao dar entrada no insumo: {e}")

@receiver(post_save, sender=MovimentoInsumo)
def atualizar_estoque_insumo(sender, instance, created, **kwargs):
    if created:
        try:
            insumo = instance.insumo
            
            estoque_atual = insumo.quantidade_estoque or 0
            
            if instance.tipo == 'ENTRADA':
                insumo.quantidade_estoque = estoque_atual + instance.quantidade
                print(f"Signal (MovimentoInsumo ID: {instance.id}): Atualizando estoque de {insumo.nome}: +{instance.quantidade}. Novo total: {insumo.quantidade_estoque}")
            elif instance.tipo == 'SAIDA':
                insumo.quantidade_estoque = estoque_atual - instance.quantidade
                print(f"Signal (MovimentoInsumo ID: {instance.id}): Atualizando estoque de {insumo.nome}: -{instance.quantidade}. Novo total: {insumo.quantidade_estoque}")
            
            insumo.save(update_fields=['quantidade_estoque'])
            
        except Exception as e:
            print(f"Signal (MovimentoInsumo ID: {instance.id}): ERRO ao atualizar Insumo.quantidade_estoque: {e}")

@receiver(post_save, sender=Pedido)
def registrar_venda_no_fluxo_caixa(sender, instance, **kwargs):
    if instance.status == 'entregue':
        try:
            lancamento, created = FluxoCaixa.objects.get_or_create(
                referencia_tabela='Pedido',
                referencia_id=instance.id,
                tipo='ENTRADA',
                defaults={
                    'categoria': 'VENDA',
                    'descricao': f'Recebimento referente ao Pedido #{instance.id}',
                    'valor': instance.total_pedido,
                    'data_lancamento': instance.created_at.date(), 
                }
            )
            if created:
                print(f"Signal (Pedido ID: {instance.id}): Venda registrada no caixa.")
        except Exception as e:
            print(f"Signal (Pedido ID: {instance.id}): ERRO ao lançar Venda: {e}")