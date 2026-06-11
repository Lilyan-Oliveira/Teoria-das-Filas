"""
Modelo M/M/s/K — fila única, múltiplos servidores, capacidade máxima K.
"""
import math
import streamlit as st
from modelos.utils import (fmt, fmtp, inputs_basicos, render_parametros,
                           resolve_mm1, safe)


def calcular(lam, mu, s, K):
    r   = lam / mu        # λ/μ
    rho = lam / (s * mu)  # λ/(s·μ)

    # denominador de P0
    denom = sum(r ** n / math.factorial(n) for n in range(s + 1))
    denom += (r ** s / math.factorial(s)) * sum(rho ** m for m in range(1, K - s + 1))
    P0 = 1.0 / denom

    def Pn(n):
        if n <= s:
            return r ** n / math.factorial(n) * P0
        return r ** n / (math.factorial(s) * s ** (n - s)) * P0

    probs  = [Pn(n) for n in range(K + 1)]
    PK     = probs[K]
    lam_ef = lam * (1 - PK)
    Lq     = sum((n - s) * probs[n] for n in range(s, K + 1))
    L      = sum(n * probs[n] for n in range(K + 1))
    W      = L / lam_ef
    Wq     = Lq / lam_ef

    return dict(rho=rho, P0=P0, PK=PK, lam_ef=lam_ef, L=L, Lq=Lq, W=W, Wq=Wq)


def render():
    st.header("Modelo M/M/s/K")
    st.caption("Fila única · Múltiplos servidores · Capacidade máxima K")

    col1, col2 = st.columns(2)
    with col1:
        s_raw = st.text_input("s — número de servidores", placeholder="ex: 2", key="s_mmsk")
    with col2:
        K_raw = st.text_input("K — capacidade máxima (K ≥ s)", placeholder="ex: 5", key="K_mmsk")

    s_val = safe(s_raw)
    K_val = safe(K_raw)

    inp = inputs_basicos()
    lam, mu, rho = resolve_mm1(**inp)
    render_parametros(lam, mu, rho)

    st.markdown("---")
    st.markdown("### Saídas")

    if lam is None or mu is None:
        st.warning("⚠️ Dados insuficientes para resolver λ e μ. Preencha mais campos.")
        return

    if s_val is None or s_val < 1:
        st.warning("⚠️ Informe o número de servidores **s** (inteiro ≥ 1).")
        return

    if K_val is None or K_val < 1:
        st.warning("⚠️ Informe a capacidade máxima **K** (inteiro ≥ 1).")
        return

    s = int(s_val)
    K = int(K_val)

    if K < s:
        st.error(f"🚫 K deve ser ≥ s. K = {K}, s = {s}.")
        return

    res = calcular(lam, mu, s, K)

    st.success(
        f"✅ ρ = λ/(s·μ) = {fmt(res['rho'])}  |  s = {s}  |  K = {K}"
        f"  |  λ̄ = {fmt(res['lam_ef'])}"
    )

    st.markdown("**Tempos e filas**")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("W",  fmt(res["W"]),  help="L / λ̄")
    c2.metric("Wq", fmt(res["Wq"]), help="Lq / λ̄")
    c3.metric("L",  fmt(res["L"]),  help="Σ n·Pn, n=0..K")
    c4.metric("Lq", fmt(res["Lq"]), help="Σ (n−s)·Pn, n=s..K")

    st.markdown("**Probabilidades**")
    c1, c2, c3 = st.columns(3)
    c1.metric("P(0) — sistema vazio", fmtp(res["P0"]),    help="fórmula somatório slides")
    c2.metric("P(K) — sistema cheio", fmtp(res["PK"]),    help="Pₖ calculado via fórmula Pn")
    c3.metric("λ̄ — taxa efetiva",    fmt(res["lam_ef"]), help="λ · (1 − P(K))")

    with st.expander("📐 Fórmulas — M/M/s/K"):
        st.latex(r"\rho = \frac{\lambda}{s\,\mu}")
        st.latex(
            r"P_0 = \frac{1}{\displaystyle\sum_{n=0}^{s}\frac{(\lambda/\mu)^n}{n!}"
            r"+ \frac{(\lambda/\mu)^s}{s!}\sum_{m=1}^{K-s}\rho^m}"
        )
        st.latex(r"P_n = \frac{(\lambda/\mu)^n}{n!}\,P_0, \quad 0 \leq n \leq s")
        st.latex(r"P_n = \frac{(\lambda/\mu)^n}{s!\,s^{n-s}}\,P_0, \quad s < n \leq K")
        st.latex(r"\bar{\lambda} = \lambda\,(1 - P_K)")
        st.latex(r"L_q = \sum_{n=s}^{K}(n-s)\,P_n")
        st.latex(r"L = \sum_{n=0}^{K} n\,P_n")
        st.latex(r"W = \frac{L}{\bar{\lambda}}, \qquad W_q = \frac{L_q}{\bar{\lambda}}")
