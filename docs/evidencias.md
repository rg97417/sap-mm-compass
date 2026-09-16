# Evidências verificadas — 16/09/2026

## Testes automatizados

Comando: `python3 -m unittest discover -s tests -v`

Resultado: **12 testes passaram** (`Ran 12 tests ... OK`). Cobrem resposta com fonte válida, citação inventada, filtro de instrução insegura, limite de confiança, ausência de evidência, escopo, pedido incompleto, ação de risco sem chave e com LLM simulado, código Z não documentado, mascaramento no log e contrato HTTP compatível com OpenAI em servidor local de teste.

Comando: `python3 -m py_compile app.py cli.py src/assistant.py`

Resultado: **sem erros de sintaxe**.

## Execução dos chamados fictícios pela CLI

| Caso | Resultado observado neste ambiente | Observação |
|---|---|---|
| CH-02 | `needs_info` | Perguntou documento/etapa e mensagem exata. |
| CH-03 | `human_review` | Recusou liberação e mudança de tolerância sem pessoa autorizada. |
| CH-06 | `needs_info` | Não deduziu a causa sem número do documento. |
| CH-07 | `insufficient_evidence` | Não inventou causa para código Z não documentado. |
| CH-08 | `out_of_scope` | Identificou HCM como fora do recorte MM. |
| CH-01 | `error` | Não havia `OPENAI_API_KEY` no ambiente; nenhum resultado de LLM real foi fabricado. |

Os testes do núcleo injetam um cliente LLM falso para verificar o fluxo de CH-01 (`answered`) e CH-03 (`human_review`) com resposta JSON controlada. Isso testa orquestração e freios, **não a qualidade de um modelo real**.

## Interface

A aplicação Streamlit abriu em `http://127.0.0.1:8501`; o teste `AppTest` executou `app.py` sem exceções. A interface foi inspecionada no navegador, e o caso CH-02 exibiu o estado **Aguardando informações**, as duas perguntas de triagem e o ID de auditoria.

## Pendência para a demonstração final

Executar CH-01 e CH-03 com uma chave de API válida para demonstrar geração real do LLM e gravar um print ou vídeo da tela. Nenhuma chave foi encontrada neste ambiente no momento desta verificação.
