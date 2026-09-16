# Roteiro de demonstração — até 20 minutos

| Tempo | Demonstração | Mensagem principal |
|---|---|---|
| 0–2 min | Contexto do suporte MM | A tarefa manual é interpretar chamados, localizar o processo e conferir documentação antes de orientar. |
| 2–4 min | Arquitetura e base | Mostrar cinco artigos, links SAP Help, recuperação de trechos e limites de autonomia. |
| 4–8 min | CH-01: fatura bloqueada | O assistente separa fatos informados pelo usuário de hipóteses, aponta verificações, fonte e confiança. |
| 8–10 min | CH-02: chamado incompleto | Faz perguntas específicas antes de concluir. |
| 10–12 min | CH-03: pedido de liberação | Não executa a ação; encaminha para responsável autorizado. |
| 12–14 min | CH-07 e CH-08 | Sem evidência para código Z; HCM fora do escopo. |
| 14–16 min | Log e testes | Mostrar que resposta e fontes ficam registradas e os cenários automatizados passaram. |
| 16–18 min | Segurança e acesso real | APIs de leitura com escopo mínimo; validação humana em ações de escrita. |
| 18–20 min | Métricas, limitações e perguntas | Medir tempo de triagem, precisão auditada, taxa de fundamentação, encaminhamentos corretos. |

## Respostas para perguntas prováveis

- **Por que GenAI?** O chamado chega em linguagem livre e incompleta. O modelo ajuda a sintetizar o relato e transformar trechos recuperados em orientações legíveis; a recuperação limita o domínio factual.
- **Como evita alucinação?** Escopo fechado, base pequena verificável, fontes por ID, instruções de não inferir estado do sistema e saída validada. Sem trecho adequado, encaminha em vez de inventar.
- **Quando perguntar?** Quando faltarem identificador, etapa, mensagem ou dado necessário para diferenciar causas.
- **Quando um humano decide?** Sempre que a ação envolver pagamento, aprovação, alteração de configuração, contabilização, estorno ou outros controles do cliente.
- **É RAG?** Sim: recupera trechos da base local para compor o contexto antes da geração. Usa busca lexical por ser suficiente para cinco artigos; embeddings e índice vetorial seriam uma evolução se a base crescesse.
- **Como medir ganho?** Comparar chamados equivalentes antes/depois: tempo até a primeira triagem útil, percentual de orientações aprovadas por consultor, citações corretas, taxa de encaminhamento de riscos e retrabalho. Medir com revisão humana e amostra definida.
