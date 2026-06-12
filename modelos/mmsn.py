"""
Modelo M/M/s/N — fila única, múltiplos servidores, população finita N.
Todas as fórmulas dos slides Teoria_das_filas_Modelo_MMsK_e_MMsN.pdf (págs. 21-22).
"""
import math
import streamlit as st
from modelos.utils import (fmt, fmtp, inputs_basicos, render_parametros,
                           resolve_mm1, safe)


def calcular_Pn(lam, mu, s, N, P0, n):
    """
    Pn — probabilidade de haver n clientes no sistema.

    Slide pág. 21:
      n <= s  →  Pn = N! / [(N-n)! · n!] · (λ/μ)^n · P0
      s <= n <= N  →  Pn = N! / [(N-n)! · s! · s^(n-s)] · (λ/μ)^n · P0
      n > N  →  Pn = 0
    """
    if n > N:
        return 0.0
    r = lam / mu
    if n <= s:
        return (math.factorial(N) / (math.factorial(N - n) * math.factorial(n))) * (r ** n) * P0
    else:
        return (math.factorial(N) / (math.factorial(N - n) * math.factorial(s) * (s ** (n - s)))) * (r ** n) * P0


def calcular(lam, mu, s, N):
    """
    Calcula todas as medidas de efetividade do M/M/s/N.

    Fórmulas do slide pág. 21-22:
      ρ = Nλ / (s·μ)
      P0 = 1 / [Σ(n=0..s-1) N!/((N-n)!·n!) · (λ/μ)^n
               + Σ(n=s..N) N!/((N-n)!·s!·s^(n-s)) · (λ/μ)^n]
      L  = Σ(n=1..N) n·Pn
      Lq = L − (λ/μ)·(N − L)
      λ̄  = λ·(N − L)
      Wq = Lq / λ̄
      W  = L  / λ̄
    """
    r = lam / mu  # λ/μ

    # ── P0 ────────────────────────────────────────────────────────────────────
    soma1 = sum(
        (math.factorial(N) / (math.factorial(N - n) * math.factorial(n))) * (r ** n)
        for n in range(min(s, N + 1))
    )
    soma2 = sum(
        (math.factorial(N) / (math.factorial(N - n) * math.factorial(s) * (s ** (n - s)))) * (r ** n)
        for n in range(s, N + 1)
    )
    P0 = 1.0 / (soma1 + soma2)

    rho = (N * lam) / (s * mu)  # conforme slide pág. 21

    # ── L = Σ n·Pn, n=1..N ────────────────────────────────────────────────────
    L = sum(n * calcular_Pn(lam, mu, s, N, P0, n) for n in range(1, N + 1))

    # ── Lq = L − (λ/μ)·(N − L) ───────────────────────────────────────────────
    Lq = L - r * (N - L)

    # ── λ̄ = λ·(N − L) ─────────────────────────────────────────────────────────
    lam_ef = lam * (N - L)

    if lam_ef <= 0:
        return dict(rho=rho, P0=P0, L=L, Lq=Lq, lam_ef=lam_ef, W=None, Wq=None)

    W  = L  / lam_ef
    Wq = Lq / lam_ef

    return dict(rho=rho, P0=P0, L=L, Lq=Lq, lam_ef=lam_ef, W=W, Wq=Wq)


def render():
    st.header("Modelo M/M/s/N")
    st.caption("Fila única · Múltiplos servidores · População finita N")

    col1, col2 = st.columns(2)
    with col1:
        s_raw = st.text_input("s — número de servidores", placeholder="ex: 2", key="s_mmsn")
    with col2:
        N_raw = st.text_input("N — tamanho da população finita", placeholder="ex: 10", key="N_mmsn")

    s_val = safe(s_raw)
    N_val = safe(N_raw)

    inp = inputs_basicos()
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

    if N_val is None or N_val < 1:
        st.warning("⚠️ Informe o tamanho da população **N** (inteiro ≥ 1).")
        return

    s = int(s_val)
    N = int(N_val)

    if s > N:
        st.error(f"🚫 s deve ser ≤ N. s = {s}, N = {N}.")
        return

    res = calcular(lam, mu, s, N)

    st.success(
        f"✅ ρ = Nλ/(s·μ) = {fmt(res['rho'])}  |  s = {s}  |  N = {N}"
        f"  |  λ̄ = {fmt(res['lam_ef'])}"
    )

    st.markdown("**Tempos e filas**")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("W",  fmt(res["W"]),  help="L / λ̄")
    c2.metric("Wq", fmt(res["Wq"]), help="Lq / λ̄")
    c3.metric("L",  fmt(res["L"]),  help="Σ n·Pn, n=1..N")
    c4.metric("Lq", fmt(res["Lq"]), help="L − (λ/μ)·(N − L)")

    st.markdown("**Probabilidades**")
    c1, c2 = st.columns(2)
    c1.metric("P(0) — sistema vazio", fmtp(res["P0"]), help="fórmula somatório slides pág. 21")
    c2.metric("λ̄ — taxa efetiva",    fmt(res["lam_ef"]), help="λ · (N − L)")

    with st.expander("📐 Fórmulas — M/M/s/N"):
        st.latex(r"\rho = \frac{N\lambda}{s\,\mu}")
        st.latex(
            r"P_0 = 1\Bigg/\left["
            r"\sum_{n=0}^{s-1}\frac{N!}{(N-n)!\,n!}\left(\frac{\lambda}{\mu}\right)^n"
            r"+ \sum_{n=s}^{N}\frac{N!}{(N-n)!\,s!\,s^{n-s}}\left(\frac{\lambda}{\mu}\right)^n"
            r"\right]"
        )
        st.latex(
            r"P_n = \frac{N!}{(N-n)!\,n!}\left(\frac{\lambda}{\mu}\right)^n P_0"
            r"\qquad (n \leq s)"
        )
        st.latex(
            r"P_n = \frac{N!}{(N-n)!\,s!\,s^{n-s}}\left(\frac{\lambda}{\mu}\right)^n P_0"
            r"\qquad (s \leq n \leq N)"
        )
        st.latex(r"P_n = 0 \qquad (n > N)")
        st.latex(r"L = \sum_{n=1}^{N} n\,P_n")
        st.latex(r"L_q = L - \frac{\lambda}{\mu}(N - L)")
        st.latex(r"\bar{\lambda} = \lambda\,(N - L)")
        st.latex(r"W = \frac{L}{\bar{\lambda}} \qquad W_q = \frac{L_q}{\bar{\lambda}}")