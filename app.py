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

IMPLEMENTADOS = {"M/M/1", "M/M/s"}

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

# ── roteamento ────────────────────────────────────────────────────────────────
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
    render()