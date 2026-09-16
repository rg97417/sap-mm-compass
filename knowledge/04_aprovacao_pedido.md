# KB-04 | Aprovação do pedido de compra (SAP S/4HANA MM)

Escopo: pedido com status de aprovação ou aguardando responsável.

## Fatos fundamentados

- O flexible workflow de pedidos pode usar condições de início e etapas com aprovadores definidos. A configuração do cliente determina qual fluxo é selecionado.
- A análise deve verificar status do pedido, detalhes do workflow, condições aplicáveis e responsável da etapa atual.
- Aprovar, rejeitar ou modificar regras de workflow são ações humanas autorizadas.

## Triagem recomendada

Peça número do pedido, sociedade, status, momento da última alteração e mensagem exibida. Verifique a etapa atual e a atribuição do aprovador no ambiente. Escalone para comprador ou administrador de workflow quando houver erro de determinação.

## Fontes SAP

- SAP Help, Manage Workflows for Purchase Orders: https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/af9ef57f504840d2b81be8667206d485/46c9e5b6ba7a4feeb920ca1cbad68c73.html
