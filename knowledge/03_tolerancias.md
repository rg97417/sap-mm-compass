# KB-03 | Divergências de preço e quantidade (SAP S/4HANA MM)

Escopo: comparação de pedido, entrada e fatura no processo de compras.

## Fatos fundamentados

- Limites de tolerância são configurados no sistema. Não existe um percentual universal seguro para todos os clientes.
- A verificação pode distinguir divergência de preço e de quantidade. O resultado depende dos limites configurados, da referência e da sequência dos documentos.
- A documentação SAP identifica o motivo **P** como divergência de preço e **Q** como divergência de quantidade em item de fatura.
- Quantidade faturada acima da quantidade recebida, em cenário relevante, pode gerar bloqueio por quantidade. Confirme o motivo no documento em vez de deduzir apenas pelos números.
- A decisão de alterar pedido, corrigir documento, aprovar exceção ou liberar pagamento pertence a usuários autorizados.

## Triagem recomendada

Compare preço unitário e quantidade por item, unidades de medida, moeda, impostos e recebimentos parciais. Confira tolerâncias configuradas com a equipe de configuração; não sugira alterá-las como atalho para um chamado.

## Fontes SAP

- SAP Help, Blocking Invoices: https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/af9ef57f504840d2b81be8667206d485/7870b6531de6b64ce10000000a174cb4.html
- SAP Help, Variance in an Invoice Item: https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/af9ef57f504840d2b81be8667206d485/7b70b6531de6b64ce10000000a174cb4.html
