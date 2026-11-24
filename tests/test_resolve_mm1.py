"""
Testes de resolve_mm1 com casos da Lista de exercícios Modelo MMs.
"""
import pytest
from modelos.utils import resolve_mm1


def resolve(**kw):
    args = dict(lam=None, mu=None, rho=None, tmc=None, tms=None,
                W_in=None, Wq_in=None, L_in=None, Lq_in=None)
    args.update(kw)
    return resolve_mm1(**args)


# Lista M/M/s, ex. 3: Lq = 3,2 e W = 0,5 h  →  λ = 8, μ = 10, P(n<6) = 0,7378
def test_lq_e_w():
    lam, mu, rho = resolve(Lq_in=3.2, W_in=0.5)
    assert lam == pytest.approx(8)
    assert mu == pytest.approx(10)
    assert 1 - rho ** 6 == pytest.approx(0.7378, abs=1e-4)


# Lista M/M/s, ex. 6: μ = 5 e Wq = 0,8 h  →  λ = 4
def test_mu_e_wq():
    lam, mu, rho = resolve(mu=5, Wq_in=0.8)
    assert lam == pytest.approx(4)
    assert rho == pytest.approx(0.8)


# Lista M/M/s, ex. 2: ρ = 0,8 e Wq = 0,25 h  →  μ = 16, λ = 12,8 (já suportado)
def test_rho_e_wq_continua_funcionando():
    lam, mu, _ = resolve(rho=0.8, Wq_in=0.25)
    assert lam == pytest.approx(12.8)
    assert mu == pytest.approx(16)
