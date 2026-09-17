# Evidências verificadas — 17/09/2026

## Testes automatizados

Comando: `python3 -m unittest discover -s tests -v`

Resultado: **18 testes passaram** (`Ran 18 tests ... OK`). Cobrem resposta com fonte válida, citação inventada, filtro de instrução insegura em todos os campos, limite de confiança, ausência de evidência, escopo, pedido incompleto, ação de risco sem chave e com LLM simulado, código Z não documentado, mascaramento antes do LLM e no log, contrato HTTP compatível com OpenAI em servidor local de teste, linguagem condicional sobre tolerância e distinção entre triagem de leitura e decisão humana.

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
| CH-01 | `answered` com Qwen3.5 4B local | Gerou orientação de leitura para divergência de preço com fontes e confiança média. A tolerância é apresentada como hipótese a conferir. Não há consulta ao SAP real. |
| CH-03 | `human_review` com Qwen3.5 4B local | Uma recomendação de ação controlada do modelo foi rejeitada integralmente. |

Os testes do núcleo também injetam um cliente LLM falso para verificar fluxos com resposta JSON controlada. A execução real acima usa [Qwen3.5 4B via Ollama](https://ollama.com/library/qwen3.5%3A4b). A qualidade de cada resposta ainda exige revisão funcional; houve uma tentativa anterior do modelo com afirmações excessivas, barrada pelo filtro.

## Interface

A aplicação Streamlit abriu em `http://127.0.0.1:8501`; o teste `AppTest` executou `app.py` sem exceções. A interface foi inspecionada no navegador: CH-01 exibiu **Orientação fundamentada**, fontes e confiança média; CH-02 exibiu **Aguardando informações**, perguntas de triagem e ID de auditoria.

## Demonstração ao avaliador

O README documenta as opções OpenAI e Ollama. Para comprovar o funcionamento visualmente, iniciar a interface, mostrar CH-01, CH-02 e CH-03 e gravar um print/vídeo ou apresentar ao vivo. Nenhuma chave externa foi necessária para a execução local descrita acima.
