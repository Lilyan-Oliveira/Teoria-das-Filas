"""
Modelo M/M/s — fila única, múltiplos servidores, população infinita.
Todas as fórmulas dos slides Teoria_das_filas_Modelo_MMs.pdf
"""
import math
import streamlit as st
from modelos.utils import (fmt, fmtp, inputs_basicos, inputs_auxiliares,
                           render_parametros, resolve_mm1, check_estabilidade, safe)


def calcular_P0(lam, mu, s):
    """
    P0 = 1 / [ Σ(n=0..s-1) (λ/μ)^n/n!  +  (λ/μ)^s / (s! · (1 − λ/(s·μ))) ]
    Fórmula do slide M/M/s>1, equações básicas.
    """
    r = lam / mu  # λ/μ
    soma = sum((r ** n) / math.factorial(n) for n in range(s))
    ultimo = (r ** s) / (math.factorial(s) * (1 - lam / (s * mu)))
    return 1 / (soma + ultimo)


def calcular(lam, mu, s):
    """Calcula todas as medidas de efetividade do M/M/s."""
    rho = lam / (s * mu)          # taxa de ocupação por servidor
    P0  = calcular_P0(lam, mu, s)
    r   = lam / mu                # λ/μ

    # Lq = P0·(λ/μ)^s·ρ / (s!·(1−ρ)²)
    Lq_c = (P0 * (r ** s) * rho) / (math.factorial(s) * (1 - rho) ** 2)
    Wq_c = Lq_c / lam             # Lei de Little
    L_c  = Lq_c + lam / mu        # L = Lq + λ/μ
    W_c  = L_c  / lam             # Lei de Little: W = L/λ

    return dict(rho=rho, P0=P0, Lq=Lq_c, Wq=Wq_c, L=L_c, W=W_c)


def calcular_Pn(lam, mu, s, P0, n):
    """
    Pn = (λ/μ)^n / n! · P0          para n ≤ s
    Pn = (λ/μ)^n / (s! · s^(n-s)) · P0  para n > s
    """
    r = lam / mu
    if n <= s:
        return (r ** n / math.factorial(n)) * P0
    else:
        return (r ** n / (math.factorial(s) * s ** (n - s))) * P0


def calcular_PWT(lam, mu, s, P0, rho, t):
    """
    P(W>t) = e^(−μt) · [1 + P0·(λ/μ)^s / (s!·(1−ρ)) · (1−e^(−μt(s−1−λ/μ))) / (s−1−λ/μ)]
    Fórmula do slide M/M/s>1, pág 47.
    ⚠️ Requer s−1 ≠ λ/μ para evitar divisão por zero.
    """
    r = lam / mu
    frac = (P0 * (r ** s)) / (math.factorial(s) * (1 - rho))
    denom = s - 1 - r
    if abs(denom) < 1e-10:
        return None  # caso especial — não calculado
    inner = (1 - math.exp(-mu * t * denom)) / denom
    return math.exp(-mu * t) * (1 + frac * inner)


def calcular_PWqT(lam, mu, s, P0, rho, t):
    """
    P(Wq>t) = [1 − P(Wq=0)] · e^(−s·μ·(1−ρ)·t)
    P(Wq=0) = Σ(n=0..s-1) Pn
    Fórmula do slide M/M/s>1, pág 47.
    """
    PWq0 = sum(calcular_Pn(lam, mu, s, P0, n) for n in range(s))
    return (1 - PWq0) * math.exp(-s * mu * (1 - rho) * t)


def render():
    st.header("Modelo M/M/s")
    st.caption("Fila única · Múltiplos servidores · População infinita · Capacidade infinita")

    # entrada do número de servidores
    s_raw = st.text_input("s — número de servidores", placeholder="ex: 2", key="s_mms")
    s_val = safe(s_raw)

    inp = inputs_basicos()
    aux = inputs_auxiliares()

    lam, mu, rho_mm1 = resolve_mm1(**inp)
    render_parametros(lam, mu, rho_mm1)

    st.markdown("---")
    st.markdown("### Saídas")

    if lam is None or mu is None:
        st.warning("⚠️ Dados insuficientes para resolver λ e μ. Preencha mais campos.")
        return

    if s_val is None or s_val < 1:
        st.warning("⚠️ Informe o número de servidores **s** (inteiro ≥ 1).")
        return

    s = int(s_val)

    # estabilidade M/M/s: λ < s·μ
    rho = lam / (s * mu)
    if rho >= 1:
        st.error(f"🚫 Sistema instável — ρ = λ/(s·μ) = {fmt(rho)} ≥ 1. "
                 f"Aumente s ou reduza λ.")
        return

    st.success(f"✅ Sistema estável — ρ = λ/(s·μ) = {fmt(rho)} < 1  |  s = {s}")

    res = calcular(lam, mu, s)
    P0  = res["P0"]

    # tempos e filas
    st.markdown("**Tempos e filas**")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("W",  fmt(res["W"]),  help="L / λ  =  Wq + 1/μ")
    c2.metric("Wq", fmt(res["Wq"]), help="Lq / λ")
    c3.metric("L",  fmt(res["L"]),  help="Lq + λ/μ")
    c4.metric("Lq", fmt(res["Lq"]), help="P0·(λ/μ)^s·ρ / (s!·(1−ρ)²)")

    # probabilidades de estado
    st.markdown("**Probabilidades de estado**")
    c1, c2 = st.columns(2)
    c1.metric("P(0) — sistema vazio",   fmtp(P0),  help="fórmula somatório slides")
    c2.metric("ρ por servidor",          fmtp(rho), help="λ / (s·μ)")

    n_val = aux.get("n_val")
    if n_val is not None and n_val >= 0 and float(n_val) == int(n_val):
        n  = int(n_val)
        Pn = calcular_Pn(lam, mu, s, P0, n)
        # P(N>n) = 1 − Σ(k=0..n) Pk
        Pgt = 1 - sum(calcular_Pn(lam, mu, s, P0, k) for k in range(n + 1))
        c1, c2 = st.columns(2)
        c1.metric(f"P(N={n})",  fmtp(Pn),  help="fórmula Pn dos slides")
        c2.metric(f"P(N>{n})",  fmtp(Pgt), help="1 − Σ P(k), k=0..n")
    else:
        st.caption("Informe **n** para calcular P(N=n) e P(N>n).")

    # probabilidades de tempo
    st.markdown("**Probabilidades de tempo**")
    t_val = aux.get("t_val")
    if t_val is not None and t_val >= 0:
        PWt  = calcular_PWT(lam, mu, s, P0, rho, t_val)
        PWqt = calcular_PWqT(lam, mu, s, P0, rho, t_val)
        c1, c2 = st.columns(2)
        if PWt is not None:
            c1.metric(f"P(W>{fmt(t_val)})",  fmtp(PWt),  help="fórmula slide pág 47")
        else:
            c1.metric(f"P(W>{fmt(t_val)})", "N/A", help="s−1 = λ/μ — caso especial")
        c2.metric(f"P(Wq>{fmt(t_val)})", fmtp(PWqt), help="(1−P(Wq=0))·e^(−sμ(1−ρ)t)")
    else:
        st.caption("Informe **t** para calcular P(W>t) e P(Wq>t).")

    with st.expander("📐 Fórmulas — M/M/s"):
        st.markdown("**Condição de estabilidade:** λ < s·μ  →  ρ < 1")
        st.markdown("#### Parâmetro")
        st.latex(r"\rho = \frac{\lambda}{s\,\mu}")
        st.markdown("#### Probabilidade de estado 0")
        st.latex(
            r"P_0 = \frac{1}{\displaystyle\sum_{n=0}^{s-1}\frac{(\lambda/\mu)^n}{n!}"
            r"+ \frac{(\lambda/\mu)^s}{s!\,(1 - \lambda/(s\mu))}}"
        )
        st.markdown("#### Probabilidade de estado n")
        st.latex(r"P_n = \frac{(\lambda/\mu)^n}{n!}\,P_0 \qquad (0 \leq n \leq s)")
        st.latex(r"P_n = \frac{(\lambda/\mu)^n}{s!\,s^{n-s}}\,P_0 \qquad (n > s)")
        st.markdown("#### Medidas de efetividade")
        st.latex(r"L_q = \frac{P_0\,(\lambda/\mu)^s\,\rho}{s!\,(1-\rho)^2}")
        st.latex(r"W_q = \frac{L_q}{\lambda}")
        st.latex(r"L = L_q + \frac{\lambda}{\mu}")
        st.latex(r"W = \frac{L}{\lambda}")
        st.markdown("#### Probabilidades de tempo")
        st.latex(
            r"P(W > t) = e^{-\mu t}\left[1 + \frac{P_0\,(\lambda/\mu)^s}{s!\,(1-\rho)}"
            r"\cdot\frac{1 - e^{-\mu t(s-1-\lambda/\mu)}}{s-1-\lambda/\mu}\right]"
        )
        st.latex(r"P(W_q > t) = \left[1 - P(W_q = 0)\right] e^{-s\mu(1-\rho)\,t}")
        st.latex(r"P(W_q = 0) = \sum_{n=0}^{s-1} P_n")