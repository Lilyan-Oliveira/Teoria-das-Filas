# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app locally
streamlit run app.py
```

No test suite or linter is configured.

## Architecture

This is a **Streamlit single-page app** for queueing theory calculations, deployed at https://teoria-das-filas.streamlit.app/.

**Entry point:** `app.py` — handles sidebar navigation, model selection via `st.radio`, and routes to the selected model's `render()` function. A `pagina` key in `st.session_state` toggles between the calculator and the formula reference page.

**`modelos/` package:**

| File | Model |
|---|---|
| `mm1.py` | M/M/1 |
| `mms.py` | M/M/s |
| `mm1k.py` | M/M/1/K (finite capacity) |
| `mmsk.py` | M/M/s/K |
| `mm1n.py` | M/M/1/N (finite population) |
| `mmsn.py` | M/M/s/N |
| `mg1.py` | M/G/1 (Pollaczek-Khintchine) |
| `prioridades.py` | Priority queues — non-preemptive, preemptive, M/G/1 with priorities |
| `formulas.py` | Read-only formula reference with LaTeX rendering |
| `utils.py` | Shared UI helpers and math |

**Pattern every model follows:**
1. A `calcular(lam, mu, ...)` function that takes resolved parameters and returns a dict of results.
2. A `render()` function called by `app.py` that renders inputs, resolves parameters, checks stability, and displays outputs as `st.metric` cards.

**`modelos/utils.py`** is the core shared library:
- `inputs_basicos()` / `inputs_auxiliares()` — render the standard input fields (λ, μ, ρ, TMC, TMS, W, Wq, L, Lq, plus optional n/t/x fields). All fields use named `st.session_state` keys so they can be cleared globally.
- `resolve_mm1()` — iterative solver that infers λ and μ from any valid subset of inputs using M/M/1 algebraic relations. Multi-server and finite-population models have their own resolvers.
- `botao_limpar()` — clears all known `session_state` keys. When adding a new model with new input fields, add their keys to `_TODAS_AS_CHAVES`. Dynamic keys (generated in a loop) can instead be cleared by prefix: add the prefix string to `_PREFIXOS_DINAMICOS`.
- `fmt()` / `fmtp()` — number formatters (removes trailing zeros; `fmtp` formats as percentage).
- `check_estabilidade()` — validates ρ < 1; finite-capacity models skip this check.

**Adding a new model:**
1. Create `modelos/<name>.py` with `calcular()` and `render()`.
2. Add its `session_state` input keys to `_TODAS_AS_CHAVES` in `utils.py`.
3. Register it in the `MODELOS` dict and `IMPLEMENTADOS` set in `app.py`, and add an `elif` branch in the routing block.
