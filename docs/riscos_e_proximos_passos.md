# Riscos, limitações e próximos passos

| Risco ou limite | Tratamento na prova de conceito | Próximo passo para produção |
|---|---|---|
| Documentação local incompleta/desatualizada | Apenas cinco artigos e recusa quando não houver evidência | Curadoria, versionamento, validade por cliente e edição SAP |
| Resposta plausível porém incorreta | Citações, validação de fontes e revisão humana para risco | Avaliação com chamados reais anonimizados e especialistas MM |
| Confiança interpretada como probabilidade | Rótulo qualitativo associado à evidência disponível | Calibração com conjunto rotulado e métricas de erro |
| Variações de configuração entre clientes | Não presume percentual de tolerância nem estado de documento | Consultas autorizadas a customizing e dados transacionais |
| Prompt injection no chamado ou documento | Tratar conteúdo recuperado e entrada como dados; validar saída | Filtros adicionais, testes adversariais e monitoramento |
| Dados sensíveis em chamados e logs | Exemplos fictícios; sem chaves no log | Mascaramento, criptografia, retenção e acesso por papel |
| Custo, latência ou falha do provedor LLM | Erro explícito e nenhum lançamento automático | Timeout, retry controlado, observabilidade e plano de contingência |
| Ausência de integração SAP | Apenas recomenda verificações, sem afirmar consultas reais | API de leitura com permissões mínimas, aprovação e trilha para escrita |

## Limite explícito

Esta é uma prova de conceito de apoio ao consultor. O assistente não substitui análise funcional, configurações locais, segregação de funções nem aprovação financeira.
