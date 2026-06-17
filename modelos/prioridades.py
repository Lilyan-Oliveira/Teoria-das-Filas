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
    Prioridade sem interrupção, atendimento exponencial, qualquer s.
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
        W  = 1.0 / (A * B_ant * B_k) + 1.0 / mu
        Wq = W - 1.0 / mu
        res.append({"W": W, "Wq": Wq, "L": lam_k * W, "Lq": lam_k * Wq})
        B_ant = B_k
    return res


def calcular_preemptivo(lambdas, mu, s):
    """
    Prioridade com interrupção (preemptiva), atendimento exponencial.
    s=1: fórmula fechada de Hillier-Lieberman.
    s>1: recursão via M/M/s (método dos slides 16-17).

    L e Lq usam Λₖ (soma acumulada das lambdas), conforme fórmula do slide:
      Lₖ  = Λₖ · Wₖ          (slide pág. 15 e 17)
      Lqₖ = Lₖ − Λₖ/μ
    """
    if s == 1:
        res   = []
        B_ant = 1.0
        acum  = 0.0
        for lam_k in lambdas:
            acum += lam_k              # Λₖ = λ₁ + ... + λₖ
            B_k   = 1.0 - acum / mu
            W     = (1.0 / mu) / (B_ant * B_k)
            Wq    = W - 1.0 / mu
            L     = acum * W           # Lₖ = Λₖ · Wₖ
            Lq    = L - acum / mu      # Lqₖ = Lₖ − Λₖ/μ
            res.append({"W": W, "Wq": Wq, "L": L, "Lq": Lq})
            B_ant = B_k
        return res

    # s > 1: W_m = (Λ_m/λ_m)·W_MMs(Λ_m) − Σ_{i<m} (λ_i/λ_m)·W_i
    Ws    = []
    acums = []                         # Λₖ para cada classe
    acum_lam = 0.0
    for m, lam_m in enumerate(lambdas):
        acum_lam += lam_m
        acums.append(acum_lam)
        w_mms    = _w_mms(acum_lam, mu, s)
        soma_ant = sum(lambdas[i] / lam_m * Ws[i] for i in range(m))
        W = (acum_lam / lam_m) * w_mms - soma_ant
        Ws.append(W)

    res = []
    for k, (lam_k, W) in enumerate(zip(lambdas, Ws)):
        Wq = W - 1.0 / mu
        L  = acums[k] * W             # Lₖ = Λₖ · Wₖ
        Lq = L - acums[k] / mu        # Lqₖ = Lₖ − Λₖ/μ
        res.append({"W": W, "Wq": Wq, "L": L, "Lq": Lq})
    return res


def calcular_mg1_prioridade(lambdas, es, vs):
    """
    M/G/1 com prioridades não-preemptiva, s=1.
    es[i] = E(S_i) = 1/μ_i ; vs[i] = Var(S_i) = σ²_i.
    """
    rhos    = [lam * e for lam, e in zip(lambdas, es)]
    num     = sum(lam * (v + e**2) for lam, v, e in zip(lambdas, vs, es))
    res     = []
    acum_rho = 0.0
    for k, lam_k in enumerate(lambdas):
        denom = 2.0 * (1.0 - acum_rho) * (1.0 - (acum_rho + rhos[k]))
        Wq    = num / denom
        W     = es[k] + Wq
        res.append({"W": W, "Wq": Wq, "L": lam_k * W, "Lq": lam_k * Wq})
        acum_rho += rhos[k]
    return res


# ── Interface Streamlit ────────────────────────────────────────────────────────

def render():
    import streamlit as st
    from modelos.utils import fmtp
    st.header("Modelo com Prioridades")
    st.caption("Sem interrupção · Com interrupção (preemptiva) · M/G/1 com prioridades")

    # ── Seletor de disciplina ──────────────────────────────────────────────────
    disc = st.radio(
        "**Disciplina de prioridade:**",
        ["Sem interrupção (não-preemptiva)", "Com interrupção (preemptiva)",
         "M/G/1 com prioridades (tempos gerais)"],
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
            st.info("M/G/1 com prioridades: s = 1 (servidor único).")
        else:
            s = st.number_input("s — número de atendentes", min_value=1, value=1,
                                step=1, key="prio_s")

    with col_k:
        k = st.number_input("k — número de classes de prioridade", min_value=2,
                            max_value=8, value=2, step=1, key="prio_k")

    k = int(k)
    s = int(s)

    # ── Campos por classe ──────────────────────────────────────────────────────
    st.markdown("**μ global (taxa de atendimento)**" if not mg1_mode else
                "**Entradas por classe** (E(Sᵢ) = 1/μᵢ)")

    if not mg1_mode:
        mu_raw = st.text_input("μ — taxa de atendimento (igual para todas as classes)",
                               placeholder="ex: 3", key="prio_mu")
        mu = safe(mu_raw)
    else:
        mu = None  # não usado no modo M/G/1

    st.markdown("**Taxas de chegada por classe** (classe 1 = maior prioridade)")
    lambdas  = []
    es_list  = []
    vs_list  = []

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

    # ── Validação de entradas ──────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### Saídas")

    if mg1_mode:
        if any(v is None for v in lambdas + es_list + vs_list):
            st.warning("⚠️ Preencha λᵢ, E(Sᵢ) e σ²ᵢ para todas as classes.")
            return
        if any(v <= 0 for v in lambdas + es_list):
            st.warning("⚠️ λᵢ e E(Sᵢ) devem ser positivos.")
            return

        rhos      = [lam * e for lam, e in zip(lambdas, es_list)]
        rho_total = sum(rhos)
        if rho_total >= 1:
            st.error(f"🚫 Sistema instável — Σρᵢ = {fmt(rho_total)} ≥ 1.")
            return

        st.success(f"✅ Sistema estável — Σρᵢ = {fmt(rho_total)} < 1")
        resultados = calcular_mg1_prioridade(lambdas, es_list, vs_list)
        _exibir_resultados(resultados, lambdas, mu_global=None, mg1_mode=True,
                           es_list=es_list)

    else:
        if mu is None or mu <= 0:
            st.warning("⚠️ Informe μ (taxa de atendimento).")
            return
        if any(v is None or v <= 0 for v in lambdas):
            st.warning("⚠️ Preencha λᵢ > 0 para todas as classes.")
            return

        Lambda = sum(lambdas)
        rho    = Lambda / (s * mu)
        if rho >= 1:
            st.error(f"🚫 Sistema instável — ρ = Λ/(s·μ) = {fmt(rho)} ≥ 1.")
            return

        st.success(f"✅ Sistema estável — ρ = {fmt(rho)} < 1  |  Λ = {fmt(Lambda)}  |  s = {s}")

        if disc.startswith("Sem"):
            resultados = calcular_nao_preemptivo(lambdas, mu, s)
        else:
            resultados = calcular_preemptivo(lambdas, mu, s)

        _exibir_resultados(resultados, lambdas, mu_global=mu,
                           preemptivo=disc.startswith("Com"))


def _exibir_resultados(resultados, lambdas, mu_global, mg1_mode=False,
                       es_list=None, preemptivo=False):
    import streamlit as st
    for i, (res, lam_k) in enumerate(zip(resultados, lambdas)):
        mu_label = f"  |  E(S) = {fmt(es_list[i])}" if mg1_mode else ""
        st.markdown(f"#### Classe {i+1}  (λ = {fmt(lam_k)}{mu_label})")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("W",  fmt(res["W"]),  help="tempo médio no sistema")
        c2.metric("Wq", fmt(res["Wq"]), help="tempo médio na fila")

        if preemptivo and i > 0:
            # No modelo com interrupção L e Lq usam Λₖ (soma acumulada)
            c3.metric("L",  fmt(res["L"]),
                      help="Λₖ · Wₖ  (Λₖ = soma acumulada das lambdas até classe k)")
            c4.metric("Lq", fmt(res["Lq"]),
                      help="Lₖ − Λₖ/μ")
        else:
            c3.metric("L",  fmt(res["L"]),  help="λₖ · Wₖ")
            c4.metric("Lq", fmt(res["Lq"]), help="λₖ · Wqₖ")