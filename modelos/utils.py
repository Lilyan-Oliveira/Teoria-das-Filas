"""
Funções utilitárias compartilhadas entre todos os modelos.
"""
import math
import streamlit as st


# ── Chaves de todos os campos de texto usados nos modelos ──────────────────────
_TODAS_AS_CHAVES = [
    # inputs_basicos
    "lam", "mu", "rho", "tmc", "tms",
    "W_in", "Wq_in", "L_in", "Lq_in",
    # inputs_auxiliares
    "n_val", "t_val", "x_val", "fator",
    # específicos por modelo
    "s_mms", "s_mmsk", "s_mmsn",
    "K_mm1k", "K_mmsk",
    "N_mm1n", "N_mmsn",
    # M/G/1
    "sigma2_mg1", "sigma_mg1",
]


def botao_limpar():
    """
    Renderiza um botão 🗑️ Limpar campos na sidebar.
    Ao clicar, zera todos os campos de texto de todos os modelos via session_state.
    """
    if st.sidebar.button("🗑️ Limpar campos", use_container_width=True):
        for chave in _TODAS_AS_CHAVES:
            if chave in st.session_state:
                st.session_state[chave] = ""
        st.rerun()


def safe(val):
    """Converte string para float; retorna None se vazio ou inválido."""
    if val is None:
        return None
    try:
        v = float(str(val).replace(",", ".").strip())
        return v if not math.isnan(v) else None
    except Exception:
        return None


def fmt(x, d=4):
    """Formata número removendo zeros à direita."""
    if x is None:
        return "—"
    return f"{x:.{d}f}".rstrip("0").rstrip(".")


def fmtp(x, d=4):
    """Formata como percentual."""
    if x is None:
        return "—"
    return f"{x * 100:.{d}f}%"


def render_parametros(lam, mu, rho):
    """Exibe bloco de parâmetros resolvidos."""
    st.markdown("### Parâmetros resolvidos")
    c1, c2, c3 = st.columns(3)
    c1.metric("λ", fmt(lam))
    c2.metric("μ", fmt(mu))
    c3.metric("ρ", fmt(rho))


def inputs_basicos():
    """
    Renderiza os campos de entrada comuns a todos os modelos.
    Retorna dicionário com os valores inseridos.
    """
    st.markdown("### Entradas")
    st.caption("Preencha o que o exercício fornece. Deixe em branco o restante.")

    col1, col2 = st.columns(2)
    with col1:
        lam   = st.text_input("λ — taxa de chegada",                      placeholder="ex: 4",    key="lam")
        mu    = st.text_input("μ — taxa de atendimento",                   placeholder="ex: 5",    key="mu")
        rho   = st.text_input("ρ — taxa de utilização",                    placeholder="ex: 0.8",  key="rho")
        tmc   = st.text_input("TMC — tempo médio entre chegadas (λ=1/TMC)",placeholder="ex: 15",   key="tmc")
        tms   = st.text_input("TMS — tempo médio de serviço (μ=1/TMS)",    placeholder="ex: 12",   key="tms")
    with col2:
        W_in  = st.text_input("W  — tempo médio no sistema",               placeholder="ex: 18.75",key="W_in")
        Wq_in = st.text_input("Wq — tempo médio na fila",                  placeholder="ex: 15",   key="Wq_in")
        L_in  = st.text_input("L  — número médio no sistema",              placeholder="ex: 4",    key="L_in")
        Lq_in = st.text_input("Lq — número médio na fila",                 placeholder="ex: 3.2",  key="Lq_in")

    return dict(lam=safe(lam), mu=safe(mu), rho=safe(rho),
                tmc=safe(tmc), tms=safe(tms),
                W_in=safe(W_in), Wq_in=safe(Wq_in),
                L_in=safe(L_in), Lq_in=safe(Lq_in))


def inputs_auxiliares(com_n=True, com_t=True, com_x=True, com_fator=True):
    """Renderiza campos auxiliares opcionais."""
    st.markdown("---")
    st.markdown("**Auxiliares opcionais**")

    cols = []
    if com_n: cols.append("n")
    if com_t: cols.append("t")
    if com_x: cols.append("x")

    result = {}
    colunas = st.columns(len(cols)) if cols else []

    for i, nome in enumerate(cols):
        with colunas[i]:
            if nome == "n":
                result["n_val"] = safe(st.text_input(
                    "n — nº clientes", placeholder="ex: 10", key="n_val",
                    help="P(N=n), P(N>n), P(N≤n)"))
            elif nome == "t":
                result["t_val"] = safe(st.text_input(
                    "t — tempo de referência", placeholder="ex: 30", key="t_val",
                    help="P(W>t) e P(Wq>t)"))
            elif nome == "x":
                result["x_val"] = safe(st.text_input(
                    "x — valor Poisson", placeholder="ex: 10", key="x_val",
                    help="P(X=x)"))

    if com_fator:
        result["fator"] = safe(st.text_input(
            "Fator de conversão para Poisson (opcional)",
            placeholder="ex: 60 — se dados em /min e quer Poisson em /hora",
            key="fator"))

    return result


def resolve_mm1(lam, mu, rho, tmc, tms, W_in, Wq_in, L_in, Lq_in):
    """
    Infere λ e μ a partir de qualquer combinação válida de entradas.
    Fórmulas exclusivamente dos slides M/M/1.
    """
    if tmc is not None and tmc > 0 and lam is None:
        lam = 1 / tmc
    if tms is not None and tms > 0 and mu is None:
        mu = 1 / tms

    changed = True
    while changed:
        changed = False

        if lam is not None and mu is not None and rho is None:
            rho = lam / mu; changed = True
        if lam is not None and rho is not None and rho > 0 and mu is None:
            mu = lam / rho; changed = True
        if mu is not None and rho is not None and mu > 0 and lam is None:
            lam = mu * rho; changed = True

        if lam is not None and mu is None and W_in is not None and W_in > 0:
            mu = 1 / W_in + lam; changed = True
        if mu is not None and lam is None and W_in is not None and W_in > 0:
            lam = mu - 1 / W_in; changed = True

        if (rho is not None and Wq_in is not None and Wq_in > 0
                and lam is None and mu is None and 0 < rho < 1):
            mu = rho / (Wq_in * (1 - rho))
            lam = mu * rho; changed = True

        if (rho is not None and W_in is not None and W_in > 0
                and lam is None and mu is None and 0 < rho < 1):
            mu = 1 / (W_in * (1 - rho))
            lam = mu * rho; changed = True

        if lam is not None and mu is None and Wq_in is not None and Wq_in > 0:
            a = Wq_in; b = -(2 * lam * Wq_in + 1); c = lam
            disc = b ** 2 - 4 * a * c
            if disc >= 0:
                r1 = (-b + math.sqrt(disc)) / (2 * a)
                r2 = (-b - math.sqrt(disc)) / (2 * a)
                cand = r1 if r1 > lam else (r2 if r2 > lam else None)
                if cand is not None:
                    mu = cand; changed = True

        if L_in is not None and W_in is not None and lam is None and W_in > 0:
            lam = L_in / W_in; changed = True
        if Lq_in is not None and Wq_in is not None and lam is None and Wq_in > 0:
            lam = Lq_in / Wq_in; changed = True
        if L_in is not None and lam is not None and mu is None and lam > 0:
            Wc = L_in / lam
            if Wc > 0:
                mu = 1 / Wc + lam; changed = True

        if (rho is not None and L_in is not None
                and lam is None and mu is None and 0 < rho < 1):
            lam = L_in * (1 - rho)
            if lam > 0: mu = lam / rho; changed = True
            else: lam = None

        if (rho is not None and Lq_in is not None
                and lam is None and mu is None and 0 < rho < 1):
            L_calc = Lq_in + rho
            lam = L_calc * (1 - rho)
            if lam > 0: mu = lam / rho; changed = True
            else: lam = None

    return lam, mu, rho


def check_estabilidade(lam, mu, rho=None):
    """
    Valida estabilidade do sistema.
    Retorna (estavel: bool, rho: float|None).
    """
    if lam is None or mu is None:
        return False, rho
    if rho is None:
        rho = lam / mu
    return rho < 1, rho


def glossario():
    """Exibe glossário expansível."""
    with st.expander("📖 Glossário — nomes alternativos dos parâmetros"):
        st.markdown("""
| Nome no exercício | Símbolo | Relação |
|---|---|---|
| Taxa de chegada | λ | entrada direta |
| Tempo médio entre chegadas (TMC) | → λ | λ = 1/TMC |
| Taxa de atendimento | μ | entrada direta |
| Tempo médio de serviço (TMS) | → μ | μ = 1/TMS |
| Taxa de utilização / ocupação | ρ | ρ = λ/μ |
| Tempo médio na fila (TF) | Wq | saída calculada |
| Tempo médio no sistema (TS) | W | saída calculada |
| Nº médio de clientes na fila | Lq | saída calculada |
| Nº médio de clientes no sistema | L | saída calculada |
| Nº de servidores/canais | s | entrada (M/M/s e derivados) |
| Capacidade máxima do sistema | K | entrada (M/M/s/K) |
| Tamanho da população | N | entrada (M/M/s/N) |
| Variância do tempo de serviço | σ² | entrada (M/G/1) |
""")