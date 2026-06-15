"""
Modelos com prioridades — sem interrupção, com interrupção (preemptiva) e M/G/1.
Fórmulas dos slides Teoria_das_filas_Modelo_MG1_e_com_prioridades.pdf.
"""
import math
from modelos.utils import fmt, safe


# ── Funções de cálculo puras ───────────────────────────────────────────────────

def _w_mms(lam, mu, s):
    """W (tempo médio no sistema) de um M/M/s auxiliar."""
    from modelos.mms import calcular as mms_calcular
    return mms_calcular(lam, mu, s)["W"]


def calcular_nao_preemptivo(lambdas, mu, s):
    """
    Prioridade sem interrupção (não-preemptiva), atendimento exponencial, qualquer s.
    Fórmula do slide 11:
      r = Λ/μ,  Λ = Σλᵢ
      A = s! · (sμ − Λ) / r^s · Σ(j=0..s-1) r^j/j!  +  sμ
      Wk = 1 / (A · B_{k-1} · B_k)  +  1/μ
      onde B_k = 1 − Σ(i=1..k) λᵢ / (sμ)
    Retorna lista de dicts {W, Wq, L, Lq} por classe (índice 0 = maior prioridade).
    """
    Lambda = sum(lambdas)
    r = Lambda / mu
    soma_j = sum(r**j / math.factorial(j) for j in range(s))
    A = (math.factorial(s) * (s * mu - Lambda) / r**s * soma_j) + s * mu

    res = []
    B_ant = 1.0
    acum = 0.0
    for lam_k in lambdas:
        acum += lam_k
        B_k = 1.0 - acum / (s * mu)
        W = 1.0 / (A * B_ant * B_k) + 1.0 / mu
        Wq = W - 1.0 / mu
        res.append({"W": W, "Wq": Wq, "L": lam_k * W, "Lq": lam_k * Wq})
        B_ant = B_k
    return res


def calcular_preemptivo(lambdas, mu, s):
    """
    Prioridade com interrupção (preemptiva), atendimento exponencial.
    Fórmula do slide 10:
      Wk = (1/μ) / [(1 − Σ(i=1..k-1) λᵢ/(sμ)) · (1 − Σ(i=1..k) λᵢ/(sμ))]
    s=1: aplicação direta da fórmula fechada.
    s>1: recursão via M/M/s conforme slides 16-17:
      W_m = (Λ_m/λ_m)·W_MMs(Λ_m) − Σ_{i<m} (λᵢ/λ_m)·Wᵢ
    Retorna lista de dicts {W, Wq, L, Lq} por classe (índice 0 = maior prioridade).
    """
    if s == 1:
        res = []
        B_ant = 1.0
        acum = 0.0
        for lam_k in lambdas:
            acum += lam_k
            B_k = 1.0 - acum / mu
            W = (1.0 / mu) / (B_ant * B_k)
            Wq = W - 1.0 / mu
            res.append({"W": W, "Wq": Wq, "L": lam_k * W, "Lq": lam_k * Wq})
            B_ant = B_k
        return res

    # s > 1: W_m = (Λ_m/λ_m)·W_MMs(Λ_m) − Σ_{i<m} (λᵢ/λ_m)·Wᵢ
    Ws = []
    acum_lam = 0.0
    for m, lam_m in enumerate(lambdas):
        acum_lam += lam_m
        w_mms = _w_mms(acum_lam, mu, s)
        soma_ant = sum(lambdas[i] / lam_m * Ws[i] for i in range(m))
        W = (acum_lam / lam_m) * w_mms - soma_ant
        Ws.append(W)

    res = []
    for lam_k, W in zip(lambdas, Ws):
        Wq = W - 1.0 / mu
        res.append({"W": W, "Wq": Wq, "L": lam_k * W, "Lq": lam_k * Wq})
    return res


def calcular_mg1_prioridade(lambdas, es, vs):
    """
    M/G/1 com prioridades não-preemptiva, s=1.
    Fórmula do slide 19 (Pollaczek-Khintchine estendida):
      ρᵢ = λᵢ · E(Sᵢ)
      num = Σᵢ λᵢ · [V(Sᵢ) + E(Sᵢ)²]
      E(Wq_k) = num / [2 · (1 − Σ_{i<k} ρᵢ) · (1 − Σ_{i≤k} ρᵢ)]
      E(Wk)   = E(Sk) + E(Wq_k)
    es[i] = E(S_i) = 1/μᵢ ; vs[i] = Var(S_i) = σ²ᵢ.
    """
    rhos = [lam * e for lam, e in zip(lambdas, es)]
    num = sum(lam * (v + e**2) for lam, v, e in zip(lambdas, vs, es))
    res = []
    acum_rho = 0.0
    for k, lam_k in enumerate(lambdas):
        denom = 2.0 * (1.0 - acum_rho) * (1.0 - (acum_rho + rhos[k]))
        Wq = num / denom
        W = es[k] + Wq
        res.append({"W": W, "Wq": Wq, "L": lam_k * W, "Lq": lam_k * Wq})
        acum_rho += rhos[k]
    return res


# ── Interface Streamlit ────────────────────────────────────────────────────────

def render():
    import streamlit as st
    from modelos.utils import fmtp

    st.header("Modelo com Prioridades")
    st.caption("Sem interrupção (M/M/s) · Com interrupção (M/M/s) · M/G/1 com prioridades")

    # ── Seletor de disciplina ──────────────────────────────────────────────────
    disc = st.radio(
        "**Disciplina de prioridade:**",
        [
            "Sem interrupção — M/M/s (não-preemptiva)",
            "Com interrupção — M/M/s (preemptiva)",
            "M/G/1 com prioridades (não-preemptiva)",
        ],
        key="prio_disc",
        horizontal=True,
    )
    mg1_mode = disc.startswith("M/G/1")

    st.markdown("---")
    st.markdown("### Entradas")

    col_s, col_k = st.columns(2)
    with col_s:
        if mg1_mode:
            s = 1
            st.info("M/G/1 com prioridades: restrito a **s = 1** servidor por definição do modelo.")
        else:
            s = st.number_input("s — número de atendentes", min_value=1, value=1,
                                step=1, key="prio_s")

    with col_k:
        k = st.number_input("k — número de classes de prioridade", min_value=2,
                            max_value=8, value=2, step=1, key="prio_k")

    k = int(k)
    s = int(s)

    # ── μ global (modos M/M/s) ou entradas por classe (M/G/1) ─────────────────
    if not mg1_mode:
        st.markdown("**μ — taxa de atendimento (igual para todas as classes)**")
        mu_raw = st.text_input("μ", placeholder="ex: 3", key="prio_mu")
        mu = safe(mu_raw)
    else:
        mu = None

    # ── Campos por classe ──────────────────────────────────────────────────────
    st.markdown("**Taxas de chegada por classe** (classe 1 = maior prioridade)")
    lambdas = []
    es_list = []
    vs_list = []

    for i in range(k):
        if mg1_mode:
            c1, c2, c3 = st.columns(3)
            with c1:
                lv = safe(st.text_input(f"λ_{i+1}", placeholder="ex: 10",
                                        key=f"prio_lambda_{i}"))
            with c2:
                ev = safe(st.text_input(f"E(S_{i+1}) = 1/μ_{i+1}", placeholder="ex: 0.05",
                                        key=f"prio_es_{i}"))
            with c3:
                vv = safe(st.text_input(f"σ²_{i+1} (variância)", placeholder="ex: 0.0006",
                                        key=f"prio_var_{i}"))
            lambdas.append(lv)
            es_list.append(ev)
            vs_list.append(vv)
        else:
            lv = safe(st.text_input(f"λ_{i+1} — taxa de chegada da classe {i+1}",
                                    placeholder="ex: 2", key=f"prio_lambda_{i}"))
            lambdas.append(lv)

    # ── Validação e cálculo ────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### Saídas")

    if mg1_mode:
        if any(v is None for v in lambdas + es_list + vs_list):
            st.warning("⚠️ Preencha λᵢ, E(Sᵢ) e σ²ᵢ para todas as classes.")
            return
        if any(v <= 0 for v in lambdas + es_list):
            st.warning("⚠️ λᵢ e E(Sᵢ) devem ser positivos.")
            return

        rhos = [lam * e for lam, e in zip(lambdas, es_list)]
        rho_total = sum(rhos)
        if rho_total >= 1:
            st.error(f"🚫 Sistema instável — Σρᵢ = {fmt(rho_total)} ≥ 1.")
            return

        st.success(f"✅ Sistema estável — Σρᵢ = {fmt(rho_total)} < 1")
        resultados = calcular_mg1_prioridade(lambdas, es_list, vs_list)
        _exibir_resultados(resultados, lambdas, mu_global=None, mg1_mode=True,
                           es_list=es_list)

        with st.expander("📐 Fórmulas — M/G/1 com prioridades (slide 19)"):
            st.latex(r"\rho_i = \lambda_i \cdot E(S_i)")
            st.latex(
                r"E(W_{q_k}) = \frac{\displaystyle\sum_{i=1}^{r}"
                r"\lambda_i\!\left[V(S_i) + E(S_i)^2\right]}"
                r"{2\!\left(1 - \displaystyle\sum_{i=1}^{k-1}\rho_i\right)"
                r"\!\left(1 - \displaystyle\sum_{i=1}^{k}\rho_i\right)}"
            )
            st.latex(r"E(W_k) = E(S_k) + E(W_{q_k})")
            st.latex(r"L_k = \lambda_k \cdot E(W_k)")
            st.latex(r"L_{q_k} = \lambda_k \cdot E(W_{q_k})")
            st.caption("r = número total de classes. O numerador soma sobre todas as classes.")

    else:
        if mu is None or mu <= 0:
            st.warning("⚠️ Informe μ (taxa de atendimento).")
            return
        if any(v is None or v <= 0 for v in lambdas):
            st.warning("⚠️ Preencha λᵢ > 0 para todas as classes.")
            return

        Lambda = sum(lambdas)
        rho = Lambda / (s * mu)
        if rho >= 1:
            st.error(f"🚫 Sistema instável — ρ = Λ/(s·μ) = {fmt(rho)} ≥ 1.")
            return

        st.success(f"✅ Sistema estável — ρ = {fmt(rho)} < 1  |  Λ = {fmt(Lambda)}  |  s = {s}")

        if disc.startswith("Sem"):
            resultados = calcular_nao_preemptivo(lambdas, mu, s)
            _exibir_resultados(resultados, lambdas, mu_global=mu)

            with st.expander("📐 Fórmulas — Sem interrupção / não-preemptiva (slide 11)"):
                st.latex(r"r = \frac{\Lambda}{\mu} \qquad \Lambda = \sum_{i=1}^{k}\lambda_i")
                st.latex(
                    r"W_k = \frac{1}{\left["
                    r"s!\,\dfrac{s\mu - \Lambda}{r^s}"
                    r"\displaystyle\sum_{j=0}^{s-1}\frac{r^j}{j!}"
                    r"+ s\mu\right]"
                    r"\!\left(1 - \dfrac{\displaystyle\sum_{i=1}^{k-1}\lambda_i}{s\mu}\right)"
                    r"\!\left(1 - \dfrac{\displaystyle\sum_{i=1}^{k}\lambda_i}{s\mu}\right)}"
                    r"+ \frac{1}{\mu}"
                )
                st.latex(r"W_{q_k} = W_k - \frac{1}{\mu}")
                st.latex(r"L_k = \lambda_k \cdot W_k")
                st.latex(r"L_{q_k} = \lambda_k \cdot W_{q_k}")

        else:
            resultados = calcular_preemptivo(lambdas, mu, s)
            _exibir_resultados(resultados, lambdas, mu_global=mu)

            with st.expander("📐 Fórmulas — Com interrupção / preemptiva (slide 10)"):
                st.latex(
                    r"W_k = \frac{1/\mu}{"
                    r"\left(1 - \dfrac{\displaystyle\sum_{i=1}^{k-1}\lambda_i}{s\mu}\right)"
                    r"\left(1 - \dfrac{\displaystyle\sum_{i=1}^{k}\lambda_i}{s\mu}\right)}"
                )
                st.latex(r"W_{q_k} = W_k - \frac{1}{\mu}")
                st.latex(r"L_k = \lambda_k \cdot W_k")
                st.latex(r"L_{q_k} = \lambda_k \cdot W_{q_k}")
                if s > 1:
                    st.markdown("**Para s > 1**, cada Wₖ é obtido via recursão (slides 16-17):")
                    st.latex(
                        r"W_m = \frac{\Lambda_m}{\lambda_m}\,W_{\text{M/M/s}}(\Lambda_m)"
                        r"- \sum_{i=1}^{m-1}\frac{\lambda_i}{\lambda_m}\,W_i"
                    )
                    st.latex(r"\Lambda_m = \sum_{i=1}^{m} \lambda_i")


def _exibir_resultados(resultados, lambdas, mu_global, mg1_mode=False, es_list=None):
    import streamlit as st
    from modelos.utils import fmtp
    for i, (res, lam_k) in enumerate(zip(resultados, lambdas)):
        mu_label = f"  |  E(S) = {fmt(es_list[i])}" if mg1_mode else ""
        st.markdown(f"#### Classe {i+1}  (λ = {fmt(lam_k)}{mu_label})")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("W",  fmt(res["W"]),  help="tempo médio no sistema")
        c2.metric("Wq", fmt(res["Wq"]), help="tempo médio na fila")
        c3.metric("L",  fmt(res["L"]),  help="nº médio no sistema")
        c4.metric("Lq", fmt(res["Lq"]), help="nº médio na fila")