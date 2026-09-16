# KB-02 | Fatura bloqueada para pagamento (SAP S/4HANA MM)

Escopo: verificação de fatura com referência ao pedido ou entrada de mercadorias.

## Fatos fundamentados

- O SAP compara dados da fatura com valores esperados do pedido ou da entrada. Divergências de preço, quantidade, valor do item ou outras condições podem levar a bloqueio, conforme configuração.
- Uma fatura com divergência acima da tolerância pode ser contabilizada e ficar bloqueada para pagamento. Não confundir bloqueio de pagamento com falha de contabilização.
- O motivo de bloqueio pode ser automático, manual ou estocástico. O código de motivo e os documentos devem ser verificados antes de atribuir uma causa.
- A liberação de uma fatura bloqueada é uma decisão financeira controlada. O assistente apenas orienta a análise; não executa liberação.

## Triagem recomendada

Peça número da fatura, pedido e item, sociedade, motivo de bloqueio, valores e quantidades de pedido, recebimento e fatura. Verifique se a divergência corresponde ao documento do fornecedor ou a erro de lançamento. Encaminhe correção, liberação e alteração de tolerâncias para responsáveis autorizados.

## Fontes SAP

- SAP Help, Blocking Invoices: https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/af9ef57f504840d2b81be8667206d485/7870b6531de6b64ce10000000a174cb4.html
- SAP Help, Variance in an Invoice Item: https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/af9ef57f504840d2b81be8667206d485/7b70b6531de6b64ce10000000a174cb4.html
