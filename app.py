"""
Teoria das Filas — App principal
Navegação lateral entre os modelos implementados.
"""
import streamlit as st

st.set_page_config(
    page_title="Projeto | Teoria das Filas",
    page_icon="📊",
    layout="centered"
)

# ── menu lateral ──────────────────────────────────────────────────────────────
MODELOS = {
    "M/M/1":        "mm1",
    "M/M/s":        "mms",
    "M/M/1/K":      "mm1k",
    "M/M/s/K":      "mmsk",
    "M/M/1/N":      "mm1n",
    "M/M/s/N":      "mmsn",
    "M/G/1":        "mg1",
    "Prioridades":  "prioridades",
}

IMPLEMENTADOS = {"M/M/1", "M/M/s", "M/M/1/K", "M/M/s/K", "M/M/1/N", "M/M/s/N", "M/G/1"}

with st.sidebar:
    st.title("📊 Teoria das Filas")
    st.caption("Trabalho desenvolvido por:")
    st.caption("Lilyan Oliveira · 301GES")
    st.caption("Matheus Vieira · 525GES")
    st.caption("Warley Ruivo · 424GES")
    st.markdown("---")

    st.markdown("**Selecione o modelo:**")
    escolha = st.radio("", list(MODELOS.keys()), label_visibility="collapsed")

    st.markdown("---")

    # ── Botão limpar campos ────────────────────────────────────────────────
    from modelos.utils import botao_limpar
    botao_limpar()

    st.markdown("---")

    # ── Botão consultar fórmulas ───────────────────────────────────────────
    if st.button("📐 Consultar Fórmulas", use_container_width=True):
        st.session_state["pagina"] = "formulas"

    st.markdown("---")

    with st.expander("📖 Glossário"):
        st.markdown("""
| Símbolo | Nome / relação |
|---|---|
| λ | taxa de chegada |
| TMC | tempo médio entre chegadas — λ = 1/TMC |
| μ | taxa de atendimento |
| TMS | tempo médio de serviço — μ = 1/TMS |
| ρ | taxa de utilização — ρ = λ/μ |
| Wq | tempo médio na fila |
| W | tempo médio no sistema |
| Lq | nº médio de clientes na fila |
| L | nº médio de clientes no sistema |
| s | nº de servidores (M/M/s e derivados) |
| K | capacidade máxima (M/M/s/K) |
| N | tamanho da população (M/M/s/N) |
| σ² | variância do tempo de serviço (M/G/1) |
""")

# ── inicializar página padrão ──────────────────────────────────────────────────
if "pagina" not in st.session_state:
    st.session_state["pagina"] = "calculadora"

# ── ao trocar de modelo no radio, voltar à calculadora ─────────────────────────
if "ultima_escolha" not in st.session_state:
    st.session_state["ultima_escolha"] = escolha

if st.session_state["ultima_escolha"] != escolha:
    st.session_state["ultima_escolha"] = escolha
    st.session_state["pagina"] = "calculadora"

# ── roteamento principal ───────────────────────────────────────────────────────
if st.session_state["pagina"] == "formulas":
    from modelos.formulas import render as render_formulas
    render_formulas()
    if st.button("← Voltar para a calculadora"):
        st.session_state["pagina"] = "calculadora"
        st.rerun()

else:
    if escolha not in IMPLEMENTADOS:
        st.header(f"Modelo {escolha}")
        st.info(f"🚧 Este modelo ainda será implementado. "
                f"Modelos disponíveis: {', '.join(IMPLEMENTADOS)}.")
    else:
        modulo = MODELOS[escolha]
        if modulo == "mm1":
            from modelos.mm1 import render
        elif modulo == "mms":
            from modelos.mms import render
        elif modulo == "mm1k":
            from modelos.mm1k import render
        elif modulo == "mmsk":
            from modelos.mmsk import render
        elif modulo == "mm1n":
            from modelos.mm1n import render
        elif modulo == "mmsn":
            from modelos.mmsn import render
        elif modulo == "mg1":
            from modelos.mg1 import render
        render()