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


st.set_page_config(page_title="MM Compass | Triagem SAP", page_icon="◈", layout="wide")
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');
    :root { --ink:#18352e; --muted:#62766c; --line:#d8e0d8; --paper:#f4f4ef; --accent:#dc8f32; }
    html, body, [class*="css"], [data-testid="stApp"] {font-family:'DM Sans',sans-serif;color:var(--ink)}
    [data-testid="stApp"] {background: radial-gradient(circle at 92% 0%, #e5efdf 0%, transparent 30%), var(--paper)}
    [data-testid="stSidebar"] {background:#17352d;color:#eef1e7}
    [data-testid="stSidebar"] * {color:#eef1e7}
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] [role="combobox"],
    [data-testid="stSidebar"] [data-baseweb="select"] * {color:#18352e !important}
    [data-testid="stSidebar"] .stCaption {color:#b8c8bd}
    .block-container {max-width:1320px;padding-top:4.5rem;padding-bottom:3rem}
    h1,h2,h3 {color:var(--ink);letter-spacing:-.045em}
    h1 {font-family:Georgia,serif;font-size:3.2rem !important;line-height:1.02 !important;font-weight:400 !important}
    h2 {font-family:Georgia,serif;font-weight:400 !important}
    .eyebrow {font-family:'IBM Plex Mono',monospace;font-size:.75rem;letter-spacing:.12em;text-transform:uppercase;color:#547165;margin-bottom:.65rem}
    .hero-sub {color:var(--muted);font-size:1.08rem;max-width:720px;line-height:1.55;margin:.9rem 0 2rem}
    .section-kicker {font-family:'IBM Plex Mono',monospace;font-size:.73rem;letter-spacing:.1em;color:#6b7d6f;text-transform:uppercase;margin-bottom:.35rem}
    .status {display:inline-block;border:1px solid #d9a14e;background:#fff6e8;color:#79510f;border-radius:100px;padding:.38rem .82rem;font-family:'IBM Plex Mono',monospace;font-size:.8rem}
    .status.ok {border-color:#8cbaa1;background:#e8f4eb;color:#2a6146}
    .status.pending {border-color:#b8c2ca;background:#eef1f2;color:#36515b}
    .status.review {border-color:#d68b59;background:#fff0e7;color:#8a3f21}
    .status.neutral {border-color:#ccc;background:#eee;color:#555}
    div[data-testid="stVerticalBlockBorderWrapper"] > div {border-color:var(--line) !important;background:#fffefa;border-radius:12px}
    div.stButton > button {border-radius:7px;font-weight:700;min-height:2.8rem}
    div.stButton > button[kind="primary"] {background:#1e5441;border-color:#1e5441;color:white}
    .subtle {font-size:.84rem;color:#6b7b70}
    code {font-family:'IBM Plex Mono',monospace}
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("<div class='eyebrow' style='color:#d7aa63'>MM / COMPASS</div>", unsafe_allow_html=True)
    st.header("Painel de casos")
    st.caption("SAP S/4HANA · Materials Management · Procure to Pay")
    labels = {case["id"]: f'{case["id"]} · {case["titulo"]}' for case in CASES}
    selection = st.selectbox("Chamado fictício", options=["personalizado"] + list(labels), index=1, format_func=lambda x: "Escrever meu chamado" if x == "personalizado" else labels[x])
    selected = next((case for case in CASES if case["id"] == selection), None)
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

left, right = st.columns([1.45, 1], gap="large")
with left:
    st.markdown("<div class='section-kicker'>01 / Entrada</div>", unsafe_allow_html=True)
    default = selected["texto"] if selected else ""
    ticket = st.text_area("Descreva o chamado", value=default, height=190, placeholder="Ex.: A fatura 510... está bloqueada para pagamento. Pedido 450..., item 10, sociedade 1000...")
    go = st.button("Analisar chamado  →", type="primary", use_container_width=True)
    if selected:
        st.caption(f'Cenário de demonstração: {selected["cenario"].replace("_", " ")} · documentos fictícios')
with right:
    st.markdown("<div class='section-kicker'>02 / Regras de operação</div>", unsafe_allow_html=True)
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
    st.markdown("<div class='section-kicker'>03 / Resultado da triagem</div>", unsafe_allow_html=True)
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
