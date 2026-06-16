"""
Modelo M/M/1/N — fila única, servidor único, população finita N.
"""
import math
import streamlit as st
from modelos.utils import (fmt, fmtp, inputs_basicos, inputs_auxiliares,
                           render_parametros, resolve_mm1, safe)


def calcular(lam, mu, N):
    r = lam / mu

    # P0 = 1 / Σ(n=0..N) [N!/(N-n)! · r^n]  onde N!/(N-n)! = perm(N,n)
    denom = sum(math.perm(N, n) * r ** n for n in range(N + 1))
    P0 = 1.0 / denom

    L      = N - (mu / lam) * (1 - P0)
    Lq     = N - ((lam + mu) / lam) * (1 - P0)
    lam_ef = lam * (N - L)
    W      = L / lam_ef
    Wq     = Lq / lam_ef

    return dict(P0=P0, L=L, Lq=Lq, lam_ef=lam_ef, W=W, Wq=Wq)


def calcular_Pn(lam, mu, N, P0, n):
    """
    Pn = P0 · N!/(N-n)! · (λ/μ)ⁿ,  para n = 0, 1, ..., N
    Fórmula do slide M/M/1/N — equações básicas.
    """
    if n > N:
        return 0.0
    r = lam / mu
    return P0 * math.perm(N, n) * r ** n


def render():
    st.header("Modelo M/M/1/N")
    st.caption("Fila única · Servidor único · População finita N")

    N_raw = st.text_input("N — tamanho da população finita", placeholder="ex: 10", key="N_mm1n")
    N_val = safe(N_raw)

    inp = inputs_basicos()
    aux = inputs_auxiliares(com_n=True, com_t=False, com_x=False, com_fator=False)

    lam, mu, rho = resolve_mm1(**inp)
    render_parametros(lam, mu, rho)

    st.markdown("---")
    st.markdown("### Saídas")

    if lam is None or mu is None:
        st.warning("⚠️ Dados insuficientes para resolver λ e μ. Preencha mais campos.")
        return

    if N_val is None or N_val < 1:
        st.warning("⚠️ Informe o tamanho da população **N** (inteiro ≥ 1).")
        return

    N   = int(N_val)
    res = calcular(lam, mu, N)

    st.success(
        f"✅ N = {N}  |  P(0) = {fmtp(res['P0'])}  |  λ̄ = {fmt(res['lam_ef'])}"
    )

    st.markdown("**Tempos e filas**")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("W",  fmt(res["W"]),  help="L / λ̄")
    c2.metric("Wq", fmt(res["Wq"]), help="Lq / λ̄")
    c3.metric("L",  fmt(res["L"]),  help="N − (μ/λ)·(1 − P₀)")
    c4.metric("Lq", fmt(res["Lq"]), help="N − ((λ+μ)/λ)·(1 − P₀)")

    st.markdown("**Probabilidades**")
    c1, c2 = st.columns(2)
    c1.metric("P(0) — sistema vazio", fmtp(res["P0"]),    help="1 / Σ perm(N,n)·(λ/μ)ⁿ")
    c2.metric("λ̄ — taxa efetiva",    fmt(res["lam_ef"]), help="λ · (N − L)")

    st.markdown("**Unidades operacionais**")
    st.metric("N − L — unidades operacionais", fmt(N - res["L"]),
              help="N menos o número médio fora de serviço (em reparo ou aguardando)")

    # ── Auxiliares opcionais ───────────────────────────────────────────────────
    n_val = aux.get("n_val")
    if n_val is not None and float(n_val) == int(n_val) and n_val >= 0:
        n = int(n_val)
        if n > N:
            st.warning(f"⚠️ n = {n} > N = {N}. P(N=n) = 0 para n acima da população.")
        else:
            Pn  = calcular_Pn(lam, mu, N, res["P0"], n)
            Pgt = sum(calcular_Pn(lam, mu, N, res["P0"], i) for i in range(n + 1, N + 1))
            st.markdown("**Probabilidades de estado**")
            c1, c2 = st.columns(2)
            c1.metric(f"P(N={n})",  fmtp(Pn),  help="P₀ · N!/(N−n)! · (λ/μ)ⁿ")
            c2.metric(f"P(N>{n})",  fmtp(Pgt), help="Σ Pᵢ, i=n+1..N")
    else:
        st.caption("Informe **n** para calcular P(N=n) e P(N>n).")

    with st.expander("📐 Fórmulas — M/M/1/N"):
        st.latex(
            r"P_0 = \frac{1}{\displaystyle\sum_{n=0}^{N}"
            r"\frac{N!}{(N-n)!}\left(\frac{\lambda}{\mu}\right)^n}"
        )
        st.latex(r"P_n = P_0\,\frac{N!}{(N-n)!}\left(\frac{\lambda}{\mu}\right)^n")
        st.latex(r"L = N - \frac{\mu}{\lambda}(1 - P_0)")
        st.latex(r"L_q = N - \frac{\lambda + \mu}{\lambda}(1 - P_0)")
        st.latex(r"\bar{\lambda} = \lambda\,(N - L)")
        st.latex(r"W = \frac{L}{\bar{\lambda}}, \qquad W_q = \frac{L_q}{\bar{\lambda}}")