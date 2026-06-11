"""
Modelo M/M/1/K — fila única, servidor único, capacidade máxima K.
"""
import math
import streamlit as st
from modelos.utils import (fmt, fmtp, inputs_basicos, render_parametros,
                           resolve_mm1, safe)


def calcular(lam, mu, K):
    rho = lam / mu

    if abs(rho - 1) < 1e-10:
        P0 = 1.0 / (K + 1)
        L  = K / 2.0
    else:
        P0 = (1 - rho) / (1 - rho ** (K + 1))
        L  = rho / (1 - rho) - (K + 1) * rho ** (K + 1) / (1 - rho ** (K + 1))

    PK     = P0 * rho ** K
    lam_ef = lam * (1 - PK)
    Lq     = L - (1 - P0)
    W      = L / lam_ef
    Wq     = Lq / lam_ef

    return dict(rho=rho, P0=P0, PK=PK, lam_ef=lam_ef, L=L, Lq=Lq, W=W, Wq=Wq)


def render():
    st.header("Modelo M/M/1/K")
    st.caption("Fila única · Servidor único · Capacidade máxima K")

    K_raw = st.text_input("K — capacidade máxima do sistema", placeholder="ex: 5", key="K_mm1k")
    K_val = safe(K_raw)

    inp = inputs_basicos()
    lam, mu, rho = resolve_mm1(**inp)
    render_parametros(lam, mu, rho)

    st.markdown("---")
    st.markdown("### Saídas")

    if lam is None or mu is None:
        st.warning("⚠️ Dados insuficientes para resolver λ e μ. Preencha mais campos.")
        return

    if K_val is None or K_val < 1:
        st.warning("⚠️ Informe a capacidade máxima **K** (inteiro ≥ 1).")
        return

    K   = int(K_val)
    res = calcular(lam, mu, K)

    st.success(
        f"✅ ρ = λ/μ = {fmt(res['rho'])}  |  K = {K}  |  λ̄ = {fmt(res['lam_ef'])}"
    )

    st.markdown("**Tempos e filas**")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("W",  fmt(res["W"]),  help="L / λ̄")
    c2.metric("Wq", fmt(res["Wq"]), help="Lq / λ̄")
    c3.metric("L",  fmt(res["L"]),  help="ρ/(1−ρ) − (K+1)ρᴷ⁺¹/(1−ρᴷ⁺¹)")
    c4.metric("Lq", fmt(res["Lq"]), help="L − (1 − P₀)")

    st.markdown("**Probabilidades**")
    c1, c2, c3 = st.columns(3)
    c1.metric("P(0) — sistema vazio", fmtp(res["P0"]),    help="(1−ρ)/(1−ρᴷ⁺¹)")
    c2.metric("P(K) — sistema cheio", fmtp(res["PK"]),    help="P₀ · ρᴷ")
    c3.metric("λ̄ — taxa efetiva",    fmt(res["lam_ef"]), help="λ · (1 − P(K))")

    with st.expander("📐 Fórmulas — M/M/1/K"):
        st.latex(r"\rho = \frac{\lambda}{\mu}")
        st.latex(r"P_0 = \frac{1 - \rho}{1 - \rho^{K+1}}")
        st.latex(r"P_n = P_0 \cdot \rho^n, \quad 0 \leq n \leq K")
        st.latex(r"P_K = P_0 \cdot \rho^K")
        st.latex(r"\bar{\lambda} = \lambda \cdot (1 - P_K)")
        st.latex(r"L = \frac{\rho}{1-\rho} - \frac{(K+1)\,\rho^{K+1}}{1-\rho^{K+1}}")
        st.latex(r"L_q = L - (1 - P_0)")
        st.latex(r"W = \frac{L}{\bar{\lambda}}, \qquad W_q = \frac{L_q}{\bar{\lambda}}")
