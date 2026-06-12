"""
Consulta de Fórmulas — todas extraídas dos slides de Teoria das Filas.
Organizado por modelo, com notação LaTeX idêntica à dos slides.
"""
import streamlit as st


def render():
    st.header("📐 Consulta de Fórmulas")
    st.caption("Fórmulas extraídas diretamente dos slides. Use quando a calculadora não for suficiente.")

    modelo = st.selectbox(
        "Selecione o modelo:",
        [
            "M/M/1",
            "M/M/s",
            "M/M/1/K",
            "M/M/s/K",
            "M/M/1/N",
            "M/M/s/N",
            "M/G/1",
            "Prioridades (sem interrupção)",
            "Prioridades (com interrupção)",
            "Relações universais (Lei de Little)",
        ],
    )

    st.markdown("---")

    # ── Relações universais ─────────────────────────────────────────────────
    if modelo == "Relações universais (Lei de Little)":
        st.subheader("Relações entre Wq, W, Lq e L")
        st.markdown("Válidas para **todos** os modelos de fila.")
        col1, col2 = st.columns(2)
        with col1:
            st.latex(r"L_q = \lambda \cdot W_q")
            st.latex(r"L_q = L - \frac{\lambda}{\mu}")
        with col2:
            st.latex(r"L = \lambda \cdot W")
            st.latex(r"W_q = W - \frac{1}{\mu}")

    # ── M/M/1 ───────────────────────────────────────────────────────────────
    elif modelo == "M/M/1":
        st.subheader("Modelo M/M/1")
        st.caption("Fila única · Servidor único · População infinita · Capacidade infinita")
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

    # ── M/M/s ───────────────────────────────────────────────────────────────
    elif modelo == "M/M/s":
        st.subheader("Modelo M/M/s")
        st.caption("Fila única · Múltiplos servidores · População infinita · Capacidade infinita")
        st.markdown("**Condição de estabilidade:** λ < s·μ  →  ρ < 1")

        st.markdown("#### Parâmetro")
        st.latex(r"\rho = \frac{\lambda}{s\,\mu}")

        st.markdown("#### Probabilidade de estado 0")
        st.latex(
            r"P_0 = \frac{1}{\displaystyle\sum_{n=0}^{s-1}\frac{(\lambda/\mu)^n}{n!}"
            r"+ \frac{(\lambda/\mu)^s}{s!\,(1 - \lambda/(s\mu))}}"
        )

        st.markdown("#### Probabilidade de estado n")
        st.latex(
            r"P_n = \frac{(\lambda/\mu)^n}{n!}\,P_0 \qquad (0 \leq n \leq s)"
        )
        st.latex(
            r"P_n = \frac{(\lambda/\mu)^n}{s!\,s^{n-s}}\,P_0 \qquad (n > s)"
        )

        st.markdown("#### Medidas de efetividade")
        st.latex(
            r"L_q = \frac{P_0\,(\lambda/\mu)^s\,\rho}{s!\,(1-\rho)^2}"
        )
        st.latex(r"W_q = \frac{L_q}{\lambda}")
        st.latex(r"L = L_q + \frac{\lambda}{\mu}")
        st.latex(r"W = \frac{L}{\lambda}")

        st.markdown("#### Probabilidades de tempo")
        st.latex(
            r"P(W > t) = e^{-\mu t}\left[1 + \frac{P_0\,(\lambda/\mu)^s}{s!\,(1-\rho)}"
            r"\cdot\frac{1 - e^{-\mu t(s-1-\lambda/\mu)}}{s-1-\lambda/\mu}\right]"
        )
        st.latex(
            r"P(W_q > t) = \left[1 - P(W_q = 0)\right] e^{-s\mu(1-\rho)\,t}"
        )
        st.latex(
            r"P(W_q = 0) = \sum_{n=0}^{s-1} P_n"
        )

    # ── M/M/1/K ─────────────────────────────────────────────────────────────
    elif modelo == "M/M/1/K":
        st.subheader("Modelo M/M/1/K")
        st.caption("Fila única · Servidor único · Capacidade máxima K")
        st.markdown("**Não exige condição de estabilidade** (sistema sempre limitado).")

        st.markdown("#### Parâmetro")
        st.latex(r"\rho = \frac{\lambda}{\mu}")

        st.markdown("#### Probabilidade de estado 0")
        st.latex(r"P_0 = \frac{1 - \rho}{1 - \rho^{K+1}}")
        st.markdown("*Caso especial ρ = 1:*")
        st.latex(r"P_0 = \frac{1}{K+1}")

        st.markdown("#### Probabilidade de estado n")
        st.latex(r"P_n = P_0 \cdot \rho^n \qquad (0 \leq n \leq K)")

        st.markdown("#### Taxa efetiva de chegada")
        st.latex(r"P_K = P_0 \cdot \rho^K")
        st.latex(r"\bar{\lambda} = \lambda\,(1 - P_K)")

        st.markdown("#### Medidas de efetividade")
        st.latex(
            r"L = \frac{\rho}{1-\rho} - \frac{(K+1)\,\rho^{K+1}}{1-\rho^{K+1}}"
        )
        st.markdown("*Caso especial ρ = 1:*")
        st.latex(r"L = \frac{K}{2}")
        st.latex(r"L_q = L - (1 - P_0)")
        st.latex(r"W = \frac{L}{\bar{\lambda}} \qquad W_q = \frac{L_q}{\bar{\lambda}}")

    # ── M/M/s/K ─────────────────────────────────────────────────────────────
    elif modelo == "M/M/s/K":
        st.subheader("Modelo M/M/s/K")
        st.caption("Fila única · Múltiplos servidores · Capacidade máxima K  (K ≥ s)")
        st.markdown("**Não exige condição de estabilidade** (sistema sempre limitado).")

        st.markdown("#### Parâmetro")
        st.latex(r"\rho = \frac{\lambda}{s\,\mu}")

        st.markdown("#### Probabilidade de estado 0")
        st.latex(
            r"P_0 = \frac{1}{\displaystyle\sum_{n=0}^{s}\frac{(\lambda/\mu)^n}{n!}"
            r"+ \frac{(\lambda/\mu)^s}{s!}\sum_{m=1}^{K-s}\rho^m}"
        )

        st.markdown("#### Probabilidade de estado n")
        st.latex(r"P_n = \frac{(\lambda/\mu)^n}{n!}\,P_0 \qquad (0 \leq n \leq s)")
        st.latex(r"P_n = \frac{(\lambda/\mu)^n}{s!\,s^{n-s}}\,P_0 \qquad (s < n \leq K)")

        st.markdown("#### Taxa efetiva de chegada")
        st.latex(r"\bar{\lambda} = \lambda\,(1 - P_K)")

        st.markdown("#### Medidas de efetividade")
        st.latex(r"L_q = \sum_{n=s}^{K}(n-s)\,P_n")
        st.latex(r"L = \sum_{n=0}^{K} n\,P_n")
        st.latex(r"W = \frac{L}{\bar{\lambda}} \qquad W_q = \frac{L_q}{\bar{\lambda}}")

    # ── M/M/1/N ─────────────────────────────────────────────────────────────
    elif modelo == "M/M/1/N":
        st.subheader("Modelo M/M/1/N")
        st.caption("Fila única · Servidor único · População finita N")
        st.markdown("**Não exige condição de estabilidade** (população limitada).")

        st.markdown("#### Probabilidade de estado 0")
        st.latex(
            r"P_0 = \frac{1}{\displaystyle\sum_{n=0}^{N}"
            r"\frac{N!}{(N-n)!}\left(\frac{\lambda}{\mu}\right)^n}"
        )

        st.markdown("#### Probabilidade de estado n")
        st.latex(
            r"P_n = P_0\,\frac{N!}{(N-n)!}\left(\frac{\lambda}{\mu}\right)^n"
            r"\qquad (0 \leq n \leq N)"
        )

        st.markdown("#### Medidas de efetividade")
        st.latex(r"L = N - \frac{\mu}{\lambda}(1 - P_0)")
        st.latex(r"L_q = N - \frac{\lambda + \mu}{\lambda}(1 - P_0)")
        st.latex(r"\bar{\lambda} = \lambda\,(N - L)")
        st.latex(r"W = \frac{L}{\bar{\lambda}} \qquad W_q = \frac{L_q}{\bar{\lambda}}")

    # ── M/M/s/N ─────────────────────────────────────────────────────────────
    elif modelo == "M/M/s/N":
        st.subheader("Modelo M/M/s/N")
        st.caption("Fila única · Múltiplos servidores · População finita N")
        st.markdown("**Não exige condição de estabilidade** (população limitada).")

        st.markdown("#### Parâmetro")
        st.latex(r"\rho = \frac{N\lambda}{s\,\mu}")

        st.markdown("#### Probabilidade de estado 0")
        st.latex(
            r"P_0 = 1\Bigg/\left["
            r"\sum_{n=0}^{s-1}\frac{N!}{(N-n)!\,n!}\left(\frac{\lambda}{\mu}\right)^n"
            r"+ \sum_{n=s}^{N}\frac{N!}{(N-n)!\,s!\,s^{n-s}}\left(\frac{\lambda}{\mu}\right)^n"
            r"\right]"
        )

        st.markdown("#### Probabilidade de estado n")
        st.latex(
            r"P_n = \frac{N!}{(N-n)!\,n!}\left(\frac{\lambda}{\mu}\right)^n P_0"
            r"\qquad (n \leq s)"
        )
        st.latex(
            r"P_n = \frac{N!}{(N-n)!\,s!\,s^{n-s}}\left(\frac{\lambda}{\mu}\right)^n P_0"
            r"\qquad (s \leq n \leq N)"
        )
        st.latex(r"P_n = 0 \qquad (n > N)")

        st.markdown("#### Medidas de efetividade")
        st.latex(r"L = \sum_{n=1}^{N} n\,P_n")
        st.latex(r"L_q = L - \frac{\lambda}{\mu}(N - L)")
        st.latex(r"\bar{\lambda} = \lambda\,(N - L)")
        st.latex(r"W = \frac{L}{\bar{\lambda}} \qquad W_q = \frac{L_q}{\bar{\lambda}}")

    # ── M/G/1 ───────────────────────────────────────────────────────────────
    elif modelo == "M/G/1":
        st.subheader("Modelo M/G/1  —  Fórmula de Pollaczek-Khintchine")
        st.caption("Fila única · Servidor único · Distribuição de serviço geral · σ² = variância do tempo de serviço")
        st.markdown("**Condição de estabilidade:** ρ = λ/μ < 1")

        st.markdown("#### Parâmetro")
        st.latex(r"\rho = \frac{\lambda}{\mu}")

        st.markdown("#### Medidas de efetividade")
        st.latex(r"P_0 = 1 - \rho")
        st.latex(r"L_q = \frac{\lambda^2\sigma^2 + \rho^2}{2(1 - \rho)}")
        st.latex(r"W_q = \frac{L_q}{\lambda}")
        st.latex(r"L = \rho + L_q")
        st.latex(r"W = W_q + \frac{1}{\mu}")

        st.info(
            "**σ²** é a variância do tempo de serviço (entrada do problema).\n\n"
            "- Se serviço **exponencial** (M/M/1): σ² = 1/μ²\n"
            "- Se serviço **constante** (determinístico): σ² = 0"
        )

    # ── Prioridades sem interrupção ─────────────────────────────────────────
    elif modelo == "Prioridades (sem interrupção)":
        st.subheader("Modelo com Prioridades — Sem interrupção")
        st.caption("k classes de prioridade · Processo de Poisson · Tempos exponenciais")
        st.markdown(
            "O cliente em atendimento **não é interrompido** se chegar um cliente de maior prioridade. "
            "A prioridade 1 é a mais alta."
        )

        st.markdown("#### Parâmetros por classe")
        st.latex(r"\rho_j = \frac{\lambda_j}{\mu} \qquad \rho = \sum_{j=1}^{k} \rho_j")
        st.latex(
            r"\sigma_j = \sum_{i=1}^{j} \rho_i \qquad "
            r"(\sigma_0 = 0,\; \sigma_k = \rho < 1)"
        )

        st.markdown("#### Tempo médio de espera na fila — classe j")
        st.latex(
            r"W_{q_j} = \frac{W_0}{(1 - \sigma_{j-1})(1 - \sigma_j)}"
        )
        st.markdown("onde:")
        st.latex(
            r"W_0 = \frac{\displaystyle\sum_{j=1}^{k} \frac{\rho_j}{\mu}}{"
            r"1 - \rho} \cdot \frac{1}{2}"
            r"\quad\text{(termo de trabalho médio pendente)}"
        )

        st.markdown("#### Demais medidas — classe j")
        st.latex(r"L_{q_j} = \lambda_j \cdot W_{q_j}")
        st.latex(r"W_j = W_{q_j} + \frac{1}{\mu}")
        st.latex(r"L_j = \lambda_j \cdot W_j")

    # ── Prioridades com interrupção ─────────────────────────────────────────
    elif modelo == "Prioridades (com interrupção)":
        st.subheader("Modelo com Prioridades — Com interrupção (preemptivo)")
        st.caption("k classes de prioridade · Processo de Poisson · Tempos exponenciais")
        st.markdown(
            "O cliente em atendimento **é interrompido** (preemptado) se chegar um de maior prioridade. "
            "A prioridade 1 é a mais alta."
        )

        st.markdown("#### Parâmetros por classe")
        st.latex(r"\rho_j = \frac{\lambda_j}{\mu} \qquad \sigma_j = \sum_{i=1}^{j}\rho_i")

        st.markdown("#### Tempo médio no sistema — classe j (s servidores)")
        st.latex(
            r"W_j = \frac{(1/\mu)}{"
            r"\left(1 - \displaystyle\sum_{i=1}^{j-1}\frac{\lambda_i}{s\mu}\right)"
            r"\left(1 - \displaystyle\sum_{i=1}^{j}\frac{\lambda_i}{s\mu}\right)}"
        )

        st.markdown("#### Demais medidas — classe j")
        st.latex(r"W_{q_j} = W_j - \frac{1}{\mu}")
        st.latex(r"L_j = \lambda_j \cdot W_j")
        st.latex(r"L_{q_j} = \lambda_j \cdot W_{q_j}")

        st.markdown("#### Tempo médio ponderado (mistura das classes)")
        st.latex(
            r"\bar{W}_{1-k} = \sum_{j=1}^{k} \frac{\lambda_j}{\lambda} W_j"
        )

    st.markdown("---")
    st.caption("📌 Todas as fórmulas foram extraídas dos slides fornecidos pelo docente.")