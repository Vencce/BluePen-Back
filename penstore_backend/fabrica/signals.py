from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import (
    ControleQualidade, MovimentoProdutoAcabado, OrdemProducao,
    PedidoCompra, ItemPedidoCompra, MovimentoInsumo, FluxoCaixa, Insumo
)
from loja.models import Produto 

@receiver(post_save, sender=ControleQualidade)
def criar_entrada_estoque_apos_aprovacao_cq(sender, instance, created, **kwargs):
    
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
                
                if not quantidade_aprovada or quantidade_aprovada <= 0:
                    print(f"Signal (CQ ID: {instance.id}): Falhou. Quantidade Aprovada é nula ou zero.")
                    return

                custo = produto_final.custo_base_producao_unitario
                
                MovimentoProdutoAcabado.objects.create(
                    produto=produto_final,
                    tipo='ENTRADA',
                    quantidade=quantidade_aprovada,
                    custo_producao_unitario=custo,
                    referencia_tabela='ControleQualidade',
                    referencia_id=instance.id
                )
                
                print(f"Signal (CQ ID: {instance.id}): Sucesso! Criado movimento de ENTRADA de {quantidade_aprovada} unidades de {produto_final.nome}.")

                if ordem_producao.status != 'CONCLUIDA':
                    ordem_producao.status = 'CONCLUIDA'
                    ordem_producao.save(update_fields=['status'])
                
            except Exception as e:
                print(f"Signal (CQ ID: {instance.id}): ERRO ao criar movimento de estoque: {e}")

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
    """
    Este signal escuta o MovimentoInsumo.
    Quando um movimento é CRIADO, ele atualiza o Insumo.quantidade_estoque.
    """
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