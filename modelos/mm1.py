"""
Modelo M/M/1 — fila única, servidor único, população infinita.
Todas as fórmulas dos slides Teoria_das_filas_Modelo_MMs.pdf
"""
import math
import streamlit as st
from modelos.utils import (fmt, fmtp, inputs_basicos, inputs_auxiliares,
                           render_parametros, resolve_mm1, check_estabilidade)


def calcular(lam, mu, rho):
    """Calcula todas as medidas de efetividade do M/M/1."""
    W_c  = 1 / (mu - lam)
    Wq_c = lam / (mu * (mu - lam))
    L_c  = lam / (mu - lam)
    Lq_c = (lam ** 2) / (mu * (mu - lam))
    P0   = 1 - rho
    return dict(W=W_c, Wq=Wq_c, L=L_c, Lq=Lq_c, P0=P0)


def render():
    st.header("Modelo M/M/1")
    st.caption("Fila única · Servidor único · População infinita · Capacidade infinita")

    inp = inputs_basicos()
    aux = inputs_auxiliares()

    lam, mu, rho = resolve_mm1(**inp)
    render_parametros(lam, mu, rho)

    st.markdown("---")
    st.markdown("### Saídas")

    if lam is None or mu is None:
        st.warning("⚠️ Dados insuficientes para resolver λ e μ. Preencha mais campos.")
        return

    estavel, rho = check_estabilidade(lam, mu, rho)
    if not estavel:
        st.error(f"🚫 Sistema instável — ρ = {fmt(rho)} ≥ 1. Resultados não definidos.")
        return

    st.success(f"✅ Sistema estável — ρ = {fmt(rho)} < 1")
    res = calcular(lam, mu, rho)

    # tempos e filas
    st.markdown("**Tempos e filas**")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("W",  fmt(res["W"]),  help="1 / (μ − λ)")
    c2.metric("Wq", fmt(res["Wq"]), help="λ / [μ·(μ − λ)]")
    c3.metric("L",  fmt(res["L"]),  help="λ · W")
    c4.metric("Lq", fmt(res["Lq"]), help="λ · Wq")

    # probabilidades de estado
    st.markdown("**Probabilidades de estado**")
    c1, c2 = st.columns(2)
    c1.metric("P(0) — ocioso",  fmtp(res["P0"]),  help="1 − ρ")
    c2.metric("P(ocupado) = ρ", fmtp(rho),        help="λ / μ")

    n_val = aux.get("n_val")
    if n_val is not None and n_val >= 0 and float(n_val) == int(n_val):
        n = int(n_val)
        c1, c2, c3 = st.columns(3)
        c1.metric(f"P(N={n})",  fmtp(res["P0"] * rho ** n),     help="(1−ρ)·ρⁿ")
        c2.metric(f"P(N>{n})",  fmtp(rho ** (n + 1)),            help="ρⁿ⁺¹")
        c3.metric(f"P(N≤{n})",  fmtp(1 - rho ** (n + 1)),        help="1 − ρⁿ⁺¹")
    else:
        st.caption("Informe **n** para calcular P(N=n), P(N>n) e P(N≤n).")

    # probabilidades de tempo
    st.markdown("**Probabilidades de tempo**")
    t_val = aux.get("t_val")
    if t_val is not None and t_val >= 0:
        exp_v = math.exp(-mu * (1 - rho) * t_val)
        c1, c2 = st.columns(2)
        c1.metric(f"P(W>{fmt(t_val)})",  fmtp(exp_v),        help="e^[−μ(1−ρ)t]")
        c2.metric(f"P(Wq>{fmt(t_val)})", fmtp(rho * exp_v),  help="ρ·e^[−μ(1−ρ)t]")
    else:
        st.caption("Informe **t** para calcular P(W>t) e P(Wq>t).")

    # poisson
    st.markdown("**Distribuição de Poisson**")
    x_val = aux.get("x_val")
    fator = aux.get("fator") or 1.0
    if x_val is not None and x_val >= 0 and float(x_val) == int(x_val):
        x  = int(x_val)
        lp = lam * fator
        mp = mu  * fator
        fl = math.factorial(x)
        lbl = f" ×{fmt(fator)}" if fator != 1.0 else ""
        c1, c2 = st.columns(2)
        c1.metric(f"P(X={x}) chegadas [λ{lbl}={fmt(lp)}]",
                  fmtp((math.exp(-lp) * lp ** x) / fl), help="e^(−λ)·λˣ/x!")
        c2.metric(f"P(X={x}) atend.   [μ{lbl}={fmt(mp)}]",
                  fmtp((math.exp(-mp) * mp ** x) / fl), help="e^(−μ)·μˣ/x!")
    else:
        st.caption("Informe **x** (e fator, se necessário) para calcular P(X=x).")

    with st.expander("📐 Fórmulas — M/M/1"):
        st.markdown("**Condição de estabilidade:** λ < μ  →  ρ < 1")
        st.markdown("#### Parâmetro")
        st.latex(r"\rho = \frac{\lambda}{\mu}")
        st.markdown("#### Probabilidades de estado")
        st.latex(r"P_0 = 1 - \rho")
        st.latex(r"P_n = (1 - \rho)\,\rho^n")
        st.latex(r"P(N > n) = \rho^{n+1}")
        st.latex(r"P(N \leq n) = 1 - \rho^{n+1}")
        st.markdown("#### Medidas de efetividade")
        st.latex(r"L = \frac{\lambda}{\mu - \lambda}")
        st.latex(r"L_q = \frac{\lambda^2}{\mu(\mu - \lambda)}")
        st.latex(r"W = \frac{1}{\mu - \lambda}")
        st.latex(r"W_q = \frac{\lambda}{\mu(\mu - \lambda)}")
        st.markdown("#### Probabilidades de tempo")
        st.latex(r"P(W > t) = e^{-\mu(1-\rho)\,t}")
        st.latex(r"P(W_q > t) = \rho \cdot e^{-\mu(1-\rho)\,t}")
        st.markdown("#### Distribuição de Poisson")
        st.latex(r"P(X = x) = \frac{e^{-\lambda}\,\lambda^x}{x!}")