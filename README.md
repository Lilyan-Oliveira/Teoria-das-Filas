# Teoria das Filas

Calculadora interativa de modelos de teoria das filas, desenvolvida como trabalho da disciplina **P108 — Otimização II** (Inatel).

🔗 **Acesse o app:** https://teoria-das-filas.streamlit.app/

---

## Modelos implementados

| Modelo | Descrição |
|---|---|
| M/M/1 | Fila única, servidor único, população e capacidade infinitas |
| M/M/s | Fila única, múltiplos servidores, população e capacidade infinitas |
| M/M/1/K | Servidor único, capacidade máxima K |
| M/M/s/K | Múltiplos servidores, capacidade máxima K |
| M/M/1/N | Servidor único, população finita N |
| M/M/s/N | Múltiplos servidores, população finita N |
| M/G/1 | Servidor único, distribuição de serviço geral (Pollaczek-Khintchine) |
| Prioridades — Sem interrupção (M/M/s) | Disciplina não-preemptiva, qualquer s |
| Prioridades — Com interrupção (M/M/s) | Disciplina preemptiva, qualquer s |
| Prioridades — M/G/1 com prioridades | Não-preemptiva com tempos de serviço gerais, s=1 |

Todas as fórmulas foram extraídas diretamente dos slides do Prof. Dr. Paulo Roberto Maia.

---

## Funcionalidades

- **Resolução flexível de entradas:** informe λ, μ, ρ, TMC, TMS, W, Wq, L ou Lq — o app infere os demais automaticamente
- **Verificação de estabilidade** automática (ρ < 1 ou Λ < s·μ)
- **Consulta de fórmulas** por modelo, com notação LaTeX idêntica à dos slides
- **Glossário** de símbolos no menu lateral
- **Limpeza de campos** com um clique

---

## Como rodar localmente

```bash
# Instalar dependências
pip install -r requirements.txt

# Iniciar o app
streamlit run app.py
```

---

## Como rodar os testes

```bash
pytest tests/
```

---

## Estrutura do projeto

```
modelos/
├── mm1.py          # M/M/1
├── mms.py          # M/M/s
├── mm1k.py         # M/M/1/K
├── mmsk.py         # M/M/s/K
├── mm1n.py         # M/M/1/N
├── mmsn.py         # M/M/s/N
├── mg1.py          # M/G/1
├── prioridades.py  # Modelos com prioridades
├── formulas.py     # Página de consulta de fórmulas
└── utils.py        # Funções utilitárias compartilhadas
tests/
└── test_prioridades.py  # Testes automáticos do módulo de prioridades
```

---

## Autores

- Lilyan Oliveira — 301GES
- Matheus Vieira — 525GES
- Warley Ruivo — 424GES