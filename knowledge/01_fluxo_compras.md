# KB-01 | Fluxo de compras e histórico do pedido (SAP S/4HANA MM)

Escopo: pedido de compra (PO), entrada de mercadorias (GR) e verificação de fatura logística. Este protótipo usa dados fictícios; não consulta um SAP real.

## Fatos fundamentados

- Uma entrada de mercadorias com referência ao pedido registra a entrega no histórico do pedido. O histórico permite conferir o que foi pedido, recebido e faturado.
- Em cenário de verificação de fatura baseada na entrada, a referência da fatura é a entrada de mercadorias correspondente.
- A fatura pode ser registrada antes da entrada em alguns cenários. Portanto, ausência de GR não prova sozinha um erro: é preciso verificar o indicador de verificação baseada em GR e as regras do ambiente.
- O processo pode usar a conta transitória GR/IR para conciliar entrada e fatura.

## Triagem recomendada

Peça número do pedido, item, sociedade, número da fatura, mensagem exata e, quando houver, documento da entrada. Compare histórico do pedido, quantidades e valores por item. Não afirme o estado real dos documentos sem consulta ao sistema.

## Fontes SAP

- SAP Help, Goods Receipt with Reference to a Purchase Order: https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/91b21005dded4984bcccf4a69ae1300c/a363bd534f22b44ce10000000a174cb4.html
- SAP Help, Invoices for Purchase Orders: https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/af9ef57f504840d2b81be8667206d485/be5eb6531de6b64ce10000000a174cb4.html
