import streamlit as st
import math

st.set_page_config(page_title="Teoria das Filas", page_icon="📊", layout="centered")
st.title("📊 Teoria das Filas")
st.caption("Modelo M/M/1")

# ── helpers ──────────────────────────────────────────────────────────────────
def safe(val):
    try:
        v = float(str(val).replace(",", "."))
        return v if not math.isnan(v) else None
    except Exception:
        return None

def fmt(x, d=4):
    if x is None: return "—"
    return f"{x:.{d}f}".rstrip("0").rstrip(".")

def fmtp(x, d=4):
    if x is None: return "—"
    return f"{x*100:.{d}f}%"

# ── inferência em cascata ─────────────────────────────────────────────────────
def resolve(lam, mu, rho, tmc, tms, W_in, Wq_in, L_in, Lq_in):
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
            a = Wq_in
            b = -(2 * lam * Wq_in + 1)
            c = lam
            disc = b**2 - 4*a*c
            if disc >= 0:
                r1 = (-b + math.sqrt(disc)) / (2*a)
                r2 = (-b - math.sqrt(disc)) / (2*a)
                cand = r1 if r1 > lam else (r2 if r2 > lam else None)
                if cand is not None:
                    mu = cand; changed = True

        if L_in is not None and W_in is not None and lam is None and W_in > 0:
            lam = L_in / W_in; changed = True
        if Lq_in is not None and Wq_in is not None and lam is None and Wq_in > 0:
            lam = Lq_in / Wq_in; changed = True
        if L_in is not None and lam is not None and mu is None and lam > 0:
            Wc = L_in / lam
            if Wc > 0: mu = 1 / Wc + lam; changed = True

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

# ── entradas ──────────────────────────────────────────────────────────────────
st.markdown("### Entradas")
st.caption("Preencha o que o exercício fornece. Deixe em branco o que não foi dado.")

col1, col2 = st.columns(2)
with col1:
    i_lam = st.text_input("λ — taxa de chegada", placeholder="ex: 4")
    i_mu  = st.text_input("μ — taxa de atendimento", placeholder="ex: 5")
    i_rho = st.text_input("ρ — taxa de utilização", placeholder="ex: 0.8")
    i_tmc = st.text_input("TMC — tempo médio entre chegadas  (λ = 1/TMC)", placeholder="ex: 15")
    i_tms = st.text_input("TMS — tempo médio de serviço  (μ = 1/TMS)", placeholder="ex: 12")
with col2:
    i_W   = st.text_input("W — tempo médio no sistema", placeholder="ex: 18.75")
    i_Wq  = st.text_input("Wq — tempo médio na fila", placeholder="ex: 15")
    i_L   = st.text_input("L — número médio no sistema", placeholder="ex: 4")
    i_Lq  = st.text_input("Lq — número médio na fila", placeholder="ex: 3.2")

st.markdown("---")
st.markdown("**Auxiliares opcionais**")
col3, col4, col5 = st.columns(3)
with col3:
    i_n = st.text_input("n — nº clientes", placeholder="ex: 10",
                        help="Usado em P(N=n), P(N>n) e P(N≤n)")
with col4:
    i_t = st.text_input("t — tempo de referência", placeholder="ex: 30",
                        help="Usado em P(W>t) e P(Wq>t) — mesma unidade dos dados")
with col5:
    i_x = st.text_input("x — valor Poisson", placeholder="ex: 10",
                        help="Usado em P(X=x) para chegadas e atendimentos")

i_fator = st.text_input(
    "Fator de conversão para Poisson (opcional)",
    placeholder="ex: 60  — se λ/μ estão em /min e quer Poisson em /hora",
    help="Multiplica λ e μ antes de calcular P(X=x). Deixe em branco para usar λ e μ diretos."
)

# ── resolução ─────────────────────────────────────────────────────────────────
lam, mu, rho = resolve(
    safe(i_lam), safe(i_mu), safe(i_rho),
    safe(i_tmc), safe(i_tms),
    safe(i_W), safe(i_Wq), safe(i_L), safe(i_Lq)
)

# ── parâmetros resolvidos ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Parâmetros resolvidos")
pc1, pc2, pc3 = st.columns(3)
pc1.metric("λ", fmt(lam))
pc2.metric("μ", fmt(mu))
pc3.metric("ρ", fmt(rho))

# ── validação ────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Saídas")

if lam is None or mu is None:
    st.warning("⚠️ Dados insuficientes para resolver λ e μ. Preencha mais campos.")
    st.stop()

if rho is None:
    rho = lam / mu

if rho >= 1:
    st.error(f"🚫 Sistema instável — ρ = {fmt(rho)} ≥ 1. Resultados não definidos.")
    st.stop()

st.success(f"✅ Sistema estável — ρ = {fmt(rho)} < 1")

# ── cálculo ───────────────────────────────────────────────────────────────────
W_c  = 1 / (mu - lam)
Wq_c = lam / (mu * (mu - lam))
L_c  = lam / (mu - lam)
Lq_c = (lam ** 2) / (mu * (mu - lam))
P0   = 1 - rho

st.markdown("**Tempos e filas**")
m1, m2, m3, m4 = st.columns(4)
m1.metric("W", fmt(W_c),  help="Tempo médio no sistema = 1/(μ−λ)")
m2.metric("Wq", fmt(Wq_c), help="Tempo médio na fila = λ/[μ(μ−λ)]")
m3.metric("L", fmt(L_c),  help="Número médio no sistema = λ·W")
m4.metric("Lq", fmt(Lq_c), help="Número médio na fila = λ·Wq")

st.markdown("**Probabilidades de estado**")
p1, p2 = st.columns(2)
p1.metric("P(0) — sistema ocioso", fmtp(P0), help="P(0) = 1 − ρ")
p2.metric("P(ocupado) = ρ", fmtp(rho), help="P(n>0) = ρ = λ/μ")

n_val = safe(i_n)
if n_val is not None and n_val >= 0 and float(n_val) == int(n_val):
    n_val = int(n_val)
    Pn  = P0 * (rho ** n_val)
    Pgt = rho ** (n_val + 1)
    Ple = 1 - rho ** (n_val + 1)
    p3, p4, p5 = st.columns(3)
    p3.metric(f"P(N={n_val})",  fmtp(Pn),  help="(1−ρ)·ρⁿ")
    p4.metric(f"P(N>{n_val})", fmtp(Pgt), help="ρⁿ⁺¹")
    p5.metric(f"P(N≤{n_val})", fmtp(Ple), help="1 − ρⁿ⁺¹")
else:
    st.caption("Informe **n** para calcular P(N=n), P(N>n) e P(N≤n).")

st.markdown("**Probabilidades de tempo**")
t_val = safe(i_t)
if t_val is not None and t_val >= 0:
    exp_val = math.exp(-mu * (1 - rho) * t_val)
    pt1, pt2 = st.columns(2)
    pt1.metric(f"P(W>{fmt(t_val)})",  fmtp(exp_val),       help="e^[−μ(1−ρ)t]")
    pt2.metric(f"P(Wq>{fmt(t_val)})", fmtp(rho * exp_val), help="ρ·e^[−μ(1−ρ)t]")
else:
    st.caption("Informe **t** para calcular P(W>t) e P(Wq>t).")

st.markdown("**Distribuição de Poisson**")
x_val = safe(i_x)
fator = safe(i_fator) if i_fator.strip() != "" else 1.0
if fator is None: fator = 1.0

if x_val is not None and x_val >= 0 and float(x_val) == int(x_val):
    x_val = int(x_val)
    lam_p = lam * fator
    mu_p  = mu  * fator
    fl = math.factorial(x_val)
    Pxl = (math.exp(-lam_p) * (lam_p ** x_val)) / fl
    Pxm = (math.exp(-mu_p)  * (mu_p  ** x_val)) / fl
    label_fator = f" × {fmt(fator)}" if fator != 1.0 else ""
    px1, px2 = st.columns(2)
    px1.metric(f"P(X={x_val}) chegadas  [λ{label_fator}={fmt(lam_p)}]",
               fmtp(Pxl), help="e^(−λ)·λˣ/x!")
    px2.metric(f"P(X={x_val}) atendimentos  [μ{label_fator}={fmt(mu_p)}]",
               fmtp(Pxm), help="e^(−μ)·μˣ/x!")
else:
    st.caption("Informe **x** para calcular P(X=x) por Poisson.")

# ── glossário ─────────────────────────────────────────────────────────────────
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
""")