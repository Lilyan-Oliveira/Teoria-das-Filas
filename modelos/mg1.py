"""
Modelo M/G/1 — fila única, servidor único, distribuição de serviço geral.
Todas as fórmulas dos slides Teoria_das_filas_Modelo_MG1_e_com_prioridades.pdf (pág. 5).
"""
import math
import streamlit as st
from modelos.utils import (fmt, fmtp, inputs_basicos, render_parametros,
                           resolve_mm1, check_estabilidade, safe)


def calcular(lam, mu, sigma2):
    """
    Calcula todas as medidas de efetividade do M/G/1.

    Fórmulas do slide pág. 5 (Pollaczek-Khintchine):
      ρ  = λ/μ
      P0 = 1 − ρ
      Lq = (λ²·σ² + ρ²) / [2·(1 − ρ)]
      Wq = Lq / λ
      L  = ρ + Lq
      W  = Wq + 1/μ
    """
    rho = lam / mu
    P0  = 1 - rho
    Lq  = (lam ** 2 * sigma2 + rho ** 2) / (2 * (1 - rho))
    Wq  = Lq / lam
    L   = rho + Lq
    W   = Wq + 1 / mu
    return dict(rho=rho, P0=P0, Lq=Lq, Wq=Wq, L=L, W=W)


def render():
    st.header("Modelo M/G/1")
    st.caption("Fila única · Servidor único · Distribuição de serviço geral")

    # ── Entradas padrão ────────────────────────────────────────────────────────
    inp = inputs_basicos()
    lam, mu, rho_inp = resolve_mm1(**inp)
    render_parametros(lam, mu, rho_inp)

    # ── Entrada específica: σ² ─────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### Variância do tempo de serviço")
    st.caption(
        "Informe **σ²** diretamente, **ou** informe **σ** e o app calcula σ² = σ². "
        "Deixe ambos em branco apenas se a distribuição for exponencial (σ² = 1/μ² será usado automaticamente)."
    )

    col1, col2 = st.columns(2)
    with col1:
        sigma2_raw = st.text_input("σ² — variância do tempo de serviço", placeholder="ex: 0.04", key="sigma2_mg1")
    with col2:
        sigma_raw  = st.text_input("σ — desvio padrão (opcional)", placeholder="ex: 0.2", key="sigma_mg1")

    sigma2_val = safe(sigma2_raw)
    sigma_val  = safe(sigma_raw)

    # Resolver σ²
    sigma2 = None
    fonte_sigma2 = ""

    if sigma2_val is not None and sigma2_val >= 0:
        sigma2 = sigma2_val
        fonte_sigma2 = "σ² informado diretamente"
    elif sigma_val is not None and sigma_val >= 0:
        sigma2 = sigma_val ** 2
        fonte_sigma2 = f"σ² = σ² = {fmt(sigma_val)}² = {fmt(sigma2)}"
    elif mu is not None:
        sigma2 = 1 / (mu ** 2)
        fonte_sigma2 = f"σ² = 1/μ² = 1/{fmt(mu)}² = {fmt(sigma2)}  *(distribuição exponencial assumida)*"

    st.markdown("---")
    st.markdown("### Saídas")

    if lam is None or mu is None:
        st.warning("⚠️ Dados insuficientes para resolver λ e μ. Preencha mais campos.")
        return

    estavel, rho = check_estabilidade(lam, mu)
    if not estavel:
        st.error(f"🚫 Sistema instável — ρ = λ/μ = {fmt(rho)} ≥ 1. Resultados não definidos.")
        return

    if sigma2 is None:
        st.warning("⚠️ Informe σ² ou σ para calcular as saídas.")
        return

    st.info(f"ℹ️ {fonte_sigma2}")
    st.success(f"✅ Sistema estável — ρ = {fmt(rho)} < 1")

    res = calcular(lam, mu, sigma2)

    st.markdown("**Tempos e filas**")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("W",  fmt(res["W"]),  help="Wq + 1/μ")
    c2.metric("Wq", fmt(res["Wq"]), help="Lq / λ")
    c3.metric("L",  fmt(res["L"]),  help="ρ + Lq")
    c4.metric("Lq", fmt(res["Lq"]), help="(λ²σ² + ρ²) / [2(1−ρ)]  — Pollaczek-Khintchine")

    st.markdown("**Probabilidades**")
    c1, c2 = st.columns(2)
    c1.metric("P(0) — sistema vazio", fmtp(res["P0"]), help="1 − ρ")
    c2.metric("ρ — utilização",       fmtp(res["rho"]), help="λ / μ")

    with st.expander("📐 Fórmulas — M/G/1  (Pollaczek-Khintchine)"):
        st.latex(r"\rho = \frac{\lambda}{\mu}")
        st.latex(r"P_0 = 1 - \rho")
        st.latex(r"L_q = \frac{\lambda^2\sigma^2 + \rho^2}{2(1 - \rho)}")
        st.latex(r"W_q = \frac{L_q}{\lambda}")
        st.latex(r"L = \rho + L_q")
        st.latex(r"W = W_q + \frac{1}{\mu}")
        st.markdown(
            "**σ²** é a variância do tempo de serviço (entrada do problema).\n\n"
            "- Distribuição **exponencial** (M/M/1): σ² = 1/μ²\n"
            "- Distribuição **constante/determinística**: σ² = 0"
        )