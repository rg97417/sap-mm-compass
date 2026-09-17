"""Interface de demonstração do assistente de chamados SAP S/4HANA MM."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

import streamlit as st

from src.assistant import OpenAICompatibleClient, SAPTicketAssistant


ROOT = Path(__file__).resolve().parent
CASES = json.loads((ROOT / "data/chamados.json").read_text(encoding="utf-8"))
STATUS = {
    "answered": ("Orientação fundamentada", "ok"),
    "needs_info": ("Aguardando informações", "pending"),
    "human_review": ("Validação humana necessária", "review"),
    "out_of_scope": ("Fora do escopo", "neutral"),
    "insufficient_evidence": ("Evidência insuficiente", "review"),
    "error": ("Geração indisponível", "review"),
}
PROCESS = {
    "purchase_order": "Pedido de compra",
    "goods_receipt": "Entrada de mercadorias",
    "invoice_verification": "Verificação de fatura",
    "out_of_scope": "Fora do escopo",
}
SCENARIO = {
    "sucesso": "Sucesso",
    "triagem_adicional": "Triagem adicional",
    "excecao_incompleto": "Exceção · dados incompletos",
    "excecao_risco": "Exceção · ação de risco",
    "excecao_sem_evidencia": "Exceção · sem evidência",
    "excecao_fora_escopo": "Exceção · fora do escopo",
}


def local_model_ready() -> bool:
    try:
        with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=0.35) as response:
            models = json.load(response).get("models", [])
        return any(item.get("name", "").startswith("qwen3.5:4b") for item in models)
    except (urllib.error.URLError, TimeoutError, ValueError, OSError):
        return False


def safe_md(value: str) -> str:
    """Keep currency symbols from becoming Markdown math delimiters."""
    return value.replace("$", r"\$")


def load_case() -> None:
    """Keep the editor and result synchronized with the selected demo case."""
    selection = st.session_state.get("case_selection", "CH-01")
    selected_case = next((case for case in CASES if case["id"] == selection), None)
    st.session_state["ticket_text"] = selected_case["texto"] if selected_case else ""
    st.session_state.pop("result", None)


st.set_page_config(page_title="MM Compass | Triagem SAP", page_icon="◈", layout="wide")
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');
    :root { --ink:#12372d; --muted:#62766c; --line:#d7dfd8; --paper:#f5f5ef; --accent:#d7933d; --white:#fffefa; }
    html, body, [class*="css"], [data-testid="stApp"] {font-family:'DM Sans',sans-serif;color:var(--ink)}
    [data-testid="stApp"] {background:radial-gradient(circle at 88% -5%, #dcebdd 0%, transparent 27%),linear-gradient(180deg,#f8f8f3 0%,var(--paper) 100%)}
    [data-testid="stSidebar"] {background:linear-gradient(180deg,#143a30 0%,#102f27 100%);color:#eef1e7;border-right:1px solid #284c42}
    [data-testid="stSidebar"] * {color:#eef1e7}
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] [role="combobox"],
    [data-testid="stSidebar"] [data-baseweb="select"] * {color:#18352e !important}
    [data-testid="stSidebar"] .stCaption {color:#b8c8bd}
    .block-container {max-width:1180px;padding-top:3.4rem;padding-bottom:3rem}
    h1,h2,h3 {color:var(--ink);letter-spacing:-.045em}
    h1 {font-family:Georgia,serif;font-size:3rem !important;line-height:1.03 !important;font-weight:400 !important;max-width:850px}
    h2 {font-family:Georgia,serif;font-weight:400 !important}
    .eyebrow {font-family:'IBM Plex Mono',monospace;font-size:.75rem;letter-spacing:.12em;text-transform:uppercase;color:#547165;margin-bottom:.65rem}
    .hero-sub {color:var(--muted);font-size:1.04rem;max-width:760px;line-height:1.55;margin:.8rem 0 1.5rem}
    .section-kicker {font-family:'IBM Plex Mono',monospace;font-size:.73rem;letter-spacing:.1em;color:#6b7d6f;text-transform:uppercase;margin-bottom:.35rem}
    .status {display:inline-block;border:1px solid #d9a14e;background:#fff6e8;color:#79510f;border-radius:100px;padding:.38rem .82rem;font-family:'IBM Plex Mono',monospace;font-size:.8rem}
    .status.ok {border-color:#8cbaa1;background:#e8f4eb;color:#2a6146}
    .status.pending {border-color:#b8c2ca;background:#eef1f2;color:#36515b}
    .status.review {border-color:#d68b59;background:#fff0e7;color:#8a3f21}
    .status.neutral {border-color:#ccc;background:#eee;color:#555}
    .statline {display:flex;gap:1.8rem;flex-wrap:wrap;margin:0 0 1.8rem;padding:.8rem 1rem;border:1px solid var(--line);border-radius:10px;background:rgba(255,254,250,.72);box-shadow:0 10px 30px rgba(27,55,46,.035)}
    .statline span {font-family:'IBM Plex Mono',monospace;font-size:.75rem;letter-spacing:.035em;color:#5c7167}
    .statline strong {color:var(--ink);font-weight:600}
    div[data-testid="stVerticalBlockBorderWrapper"] > div {border-color:var(--line) !important;background:var(--white);border-radius:12px;box-shadow:0 12px 35px rgba(29,61,50,.045)}
    div.stButton > button {border-radius:8px;font-weight:700;min-height:2.9rem;transition:transform .16s ease,box-shadow .16s ease}
    div.stButton > button[kind="primary"] {background:#1e5441;border-color:#1e5441;color:white}
    div.stButton > button[kind="primary"]:hover {background:#174635;border-color:#174635;transform:translateY(-1px);box-shadow:0 8px 18px rgba(23,70,53,.18)}
    [data-testid="stMetric"] {background:var(--white);border:1px solid var(--line);border-radius:10px;padding:.8rem 1rem;min-height:92px}
    [data-testid="stMetricLabel"] {color:#6a7b72;font-family:'IBM Plex Mono',monospace;font-size:.75rem}
    [data-testid="stMetricValue"] {font-size:1.35rem !important;line-height:1.25 !important;white-space:normal;overflow:visible;text-overflow:clip}
    [data-testid="stExpander"] {background:var(--white);border-color:var(--line) !important;border-radius:10px !important}
    [data-testid="stTextArea"] textarea {background:#fff;border-color:#cad5cd;border-radius:8px;line-height:1.5}
    [data-testid="stSelectbox"] > div > div {border-radius:8px}
    .subtle {font-size:.84rem;color:#6b7b70}
    code {font-family:'IBM Plex Mono',monospace}
    @media (max-width:800px) {.block-container{padding-top:2rem} h1{font-size:2.35rem !important}.statline{gap:.8rem}}
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("<div class='eyebrow' style='color:#d7aa63'>MM / COMPASS</div>", unsafe_allow_html=True)
    st.header("Configuração")
    st.caption("SAP S/4HANA · Materials Management · Procure to Pay")
    st.divider()
    st.markdown("**Configuração do modelo**")
    provider = st.radio("Provedor", ["OpenAI API", "Ollama local"], index=1 if local_model_ready() else 0, horizontal=True)
    env_key = os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY") or ""
    if provider == "OpenAI API":
        typed_key = st.text_input("Chave da API", type="password", help="Usada somente nesta sessão. Nunca entra no log.")
        api_key = typed_key or env_key
        model = st.text_input("Modelo", value=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), key="openai_model")
        base_url = "https://api.openai.com/v1"
        if not api_key:
            st.caption("Informe uma chave para gerar respostas com o LLM. Os casos e a base podem ser inspecionados sem ela.")
    else:
        api_key = "ollama"
        model = st.text_input("Modelo local", value="qwen3.5:4b", key="ollama_model")
        base_url = "http://127.0.0.1:11434/v1"
        st.caption("Requer Ollama em execução e o modelo instalado. O chamado fica nesta máquina.")
    st.divider()
    st.caption("Leitura e orientação apenas. Nenhuma operação é enviada ao SAP.")

st.markdown("<div class='eyebrow'>CENTRAL DE TRIAGEM · PROVA DE CONCEITO</div>", unsafe_allow_html=True)
st.title("Cada orientação, uma evidência.")
st.markdown("<div class='hero-sub'>Um assistente para transformar chamados de compras em uma triagem verificável, com fontes, perguntas úteis e uma parada obrigatória antes de decisões críticas.</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='statline'><span><strong>8</strong> cenários de demonstração</span><span><strong>5</strong> artigos na base</span><span><strong>0</strong> ações executadas no SAP</span></div>",
    unsafe_allow_html=True,
)

labels = {case["id"]: f'{case["id"]}  ·  {case["titulo"]}' for case in CASES}
if "case_selection" not in st.session_state:
    st.session_state["case_selection"] = "CH-01"
if "ticket_text" not in st.session_state:
    load_case()

st.markdown("<div class='section-kicker'>01 / Escolha do cenário</div>", unsafe_allow_html=True)
selection = st.selectbox(
    "8 chamados fictícios disponíveis",
    options=list(labels) + ["personalizado"],
    format_func=lambda value: "Meu próprio chamado" if value == "personalizado" else labels[value],
    key="case_selection",
    on_change=load_case,
    help="Selecione um dos oito casos preparados para a demonstração ou escreva um relato próprio.",
)
selected = next((case for case in CASES if case["id"] == selection), None)
if selected:
    st.caption(f'{SCENARIO.get(selected["cenario"], selected["cenario"])} · {selected["titulo"]} · documentos fictícios')
else:
    st.caption("Entrada livre · descreva um chamado relacionado a pedido, recebimento ou fatura.")

left, right = st.columns([1.45, 1], gap="large")
with left:
    st.markdown("<div class='section-kicker'>02 / Relato para análise</div>", unsafe_allow_html=True)
    ticket = st.text_area("Descreva ou ajuste o chamado", key="ticket_text", height=190, placeholder="Ex.: A fatura 510... está bloqueada para pagamento. Pedido 450..., item 10, sociedade 1000...")
    go = st.button("Analisar chamado  →", type="primary", use_container_width=True)
with right:
    st.markdown("<div class='section-kicker'>03 / Limites de autonomia</div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("**O assistente pode**")
        st.write("Interpretar o relato, consultar a base local, listar hipóteses e verificações, pedir dados e encaminhar o caso.")
        st.markdown("**Uma pessoa autorizada decide**")
        st.write("Aprovação de pedido, lançamento ou estorno, liberação de pagamento e mudança de tolerâncias ou dados mestres.")
        st.markdown("<div class='subtle'>As fontes oficiais apoiam o diagnóstico; os números dos chamados são simulados.</div>", unsafe_allow_html=True)

if go:
    llm = OpenAICompatibleClient(api_key, model, base_url, timeout=120 if provider == "Ollama local" else 35) if api_key else None
    assistant = SAPTicketAssistant(ROOT / "knowledge", ROOT / "logs/requests.jsonl", llm=llm)
    with st.spinner("Consultando a base e validando a resposta..."):
        st.session_state["result"] = assistant.answer(ticket)

if "result" in st.session_state:
    result = st.session_state["result"]
    st.divider()
    label, tone = STATUS.get(result["status"], (result["status"], "neutral"))
    st.markdown("<div class='section-kicker'>04 / Resultado da triagem</div>", unsafe_allow_html=True)
    st.markdown(f"<span class='status {tone}'>{label}</span>", unsafe_allow_html=True)
    st.subheader(safe_md(result["summary"]))
    if "[DOC_" in json.dumps(result, ensure_ascii=False):
        st.caption("DOC_1, DOC_2... são identificadores mascarados antes do envio ao modelo; os documentos originais constam apenas no chamado local.")
    meta1, meta2, meta3 = st.columns(3)
    meta1.metric("Processo", PROCESS.get(result["process"], result["process"]))
    meta2.metric("Confiança", {"low": "Baixa", "medium": "Média", "high": "Alta"}.get(result["confidence"], "Baixa"))
    meta3.metric("Validação humana", "Obrigatória" if result["human_review_required"] else "Conforme análise")

    col_a, col_b = st.columns(2, gap="large")
    with col_a:
        if result["probable_causes"]:
            st.markdown("#### Causas possíveis")
            for item in result["probable_causes"]:
                st.markdown(f"- {safe_md(item)}")
        if result["questions"]:
            st.markdown("#### Informações necessárias")
            for item in result["questions"]:
                st.markdown(f"- {safe_md(item)}")
    with col_b:
        if result["checks"]:
            st.markdown("#### Verificações recomendadas")
            for item in result["checks"]:
                st.markdown(f"- {safe_md(item)}")
        if result["risks"]:
            st.markdown("#### Limites e riscos")
            for item in result["risks"]:
                st.markdown(f"- {safe_md(item)}")

    with st.expander(f'Fontes recuperadas ({len(result["sources"])})', expanded=True):
        if result["sources"]:
            for source in result["sources"]:
                st.markdown(f'**{source["id"]} · {source["title"]}**  \n`knowledge/{source["path"]}`')
                st.caption(source["excerpt"][:400] + ("…" if len(source["excerpt"]) > 400 else ""))
                for url in source.get("urls", []):
                    if url.startswith("https://help.sap.com/"):
                        st.markdown(f"[Abrir documentação SAP]({url})")
        else:
            st.write("Nenhuma fonte aplicável para este caso.")
    st.caption(f'Registro de auditoria: {result["request_id"]} · logs/requests.jsonl')

st.divider()
st.markdown("<div class='subtle'>MM Compass · Protótipo para avaliação técnica · SAP S/4HANA MM · Base local e documentos fictícios</div>", unsafe_allow_html=True)
