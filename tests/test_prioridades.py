"""
Testes de aceitação para modelos/prioridades.py.
Todos os valores de referência foram conferidos contra os slides e gabaritos da lista.
Tolerância: abs ≤ 1e-3.
"""
import pytest
from modelos.prioridades import (
    calcular_nao_preemptivo,
    calcular_preemptivo,
    calcular_mg1_prioridade,
)

TOL = 1e-3


def check(resultados, esperado_W=None, esperado_Wq=None,
          esperado_L=None, esperado_Lq=None):
    for i, res in enumerate(resultados):
        if esperado_W:
            assert abs(res["W"] - esperado_W[i]) < TOL, (
                f"Classe {i+1}: W={res['W']:.5f}, esperado={esperado_W[i]}")
        if esperado_Wq:
            assert abs(res["Wq"] - esperado_Wq[i]) < TOL, (
                f"Classe {i+1}: Wq={res['Wq']:.5f}, esperado={esperado_Wq[i]}")
        if esperado_L:
            assert abs(res["L"] - esperado_L[i]) < TOL, (
                f"Classe {i+1}: L={res['L']:.5f}, esperado={esperado_L[i]}")
        if esperado_Lq:
            assert abs(res["Lq"] - esperado_Lq[i]) < TOL, (
                f"Classe {i+1}: Lq={res['Lq']:.5f}, esperado={esperado_Lq[i]}")


# T1 — sem interrupção, s=1, μ=3, λ=(0.2, 0.6, 1.2)
def test_T1_nao_preemptivo_s1():
    res = calcular_nao_preemptivo([0.2, 0.6, 1.2], mu=3, s=1)
    check(res,
          esperado_W=[0.5714, 0.6580, 1.2424],
          esperado_Wq=[0.2381, 0.3247, 0.9091])


# T2 — sem interrupção, s=2, μ=3, λ=(0.2, 0.6, 1.2)
def test_T2_nao_preemptivo_s2():
    res = calcular_nao_preemptivo([0.2, 0.6, 1.2], mu=3, s=2)
    check(res,
          esperado_W=[0.36207, 0.36649, 0.38141],
          esperado_Wq=[0.02874, 0.03316, 0.04808])


# T3 — com interrupção, s=1, μ=3, λ=(0.2, 0.6, 1.2)
def test_T3_preemptivo_s1():
    res = calcular_preemptivo([0.2, 0.6, 1.2], mu=3, s=1)
    check(res,
          esperado_W=[0.3571, 0.4870, 1.3636],
          esperado_Wq=[0.0238, 0.1537, 1.0303])


# T4 — com interrupção, s=2, μ=3, λ=(0.2, 0.6, 1.2)
def test_T4_preemptivo_s2():
    res = calcular_preemptivo([0.2, 0.6, 1.2], mu=3, s=2)
    check(res,
          esperado_W=[0.33370, 0.34126, 0.39875],
          esperado_Wq=[0.00037, 0.00793, 0.06542])


# T5 — M/G/1 prioridades, λ=(10,5), E(S)=(1/20,1/15), σ²=(1/1800,1/1800)
# Os slides arredondam: Wq1=1/18≈0.0556→0.06, W1=19/180≈0.1056→0.11. Tolerância 5e-3.
def test_T5_mg1_prioridade():
    lambdas = [10, 5]
    es = [1/20, 1/15]
    vs = [1/1800, 1/1800]
    res = calcular_mg1_prioridade(lambdas, es, vs)
    tol5 = 5e-3
    assert abs(res[0]["Wq"] - 1/18)    < tol5, f"Wq1={res[0]['Wq']:.6f}"
    assert abs(res[0]["W"]  - 19/180)  < tol5, f"W1={res[0]['W']:.6f}"
    assert abs(res[1]["Wq"] - 1/3)     < tol5, f"Wq2={res[1]['Wq']:.6f}"
    assert abs(res[1]["W"]  - 2/5)     < tol5, f"W2={res[1]['W']:.6f}"
    assert abs(res[0]["L"]  - 10*19/180) < tol5
    assert abs(res[1]["L"]  - 5*2/5)    < tol5


# T6 — sem interrupção, s=5, μ=7.5, λ=(10, 20)
def test_T6_nao_preemptivo_s5():
    res = calcular_nao_preemptivo([10, 20], mu=7.5, s=5)
    check(res, esperado_Wq=[0.0201, 0.1007])


# T7 — sem interrupção, s=1, μ=20, λ=(2, 10) — Lista Q4
# Nota: gabarito da prova traz Lq=0.083 para 2ª classe, mas o correto é 0.833
def test_T7_lista_q4():
    res = calcular_nao_preemptivo([2, 10], mu=20, s=1)
    check(res,
          esperado_Wq=[0.033, 0.083],
          esperado_W=[0.083, 0.133],
          esperado_Lq=[0.067, 0.833],  # 0.833 correto, não 0.083 do enunciado
          esperado_L=[0.167, 1.333])


# T8 — sem interrupção, s=1, μ=6, λ=(2, 3) — Lista Q5a
# Nota: gabarito embaralhou L/Lq da 1ª classe; W e Wq batem exatamente.
def test_T8_lista_q5a():
    res = calcular_nao_preemptivo([2, 3], mu=6, s=1)
    check(res,
          esperado_Wq=[0.208, 1.25],
          esperado_W=[0.375, 1.417],
          esperado_Lq=[0.417, 3.75],
          esperado_L=[0.75, 4.25])


# T9 — sem interrupção, s=2, μ=3, λ=(2, 3) — Lista Q5b
def test_T9_lista_q5b():
    res = calcular_nao_preemptivo([2, 3], mu=3, s=2)
    check(res,
          esperado_Wq=[0.189, 1.136],
          esperado_W=[0.523, 1.470],
          esperado_Lq=[0.379, 3.409],
          esperado_L=[1.045, 4.409])


# T10 — sem interrupção, s=1, μ=3, λ=(0.1, 0.4, 1.5) — Lista Q7
def test_T10_lista_q7_nao_preemptivo_s1():
    res = calcular_nao_preemptivo([0.1, 0.4, 1.5], mu=3, s=1)
    check(res, esperado_Wq=[0.230, 0.276, 0.800])


# T11 — com interrupção, s=1, μ=3, λ=(0.1, 0.4, 1.5) — Lista Q7
def test_T11_lista_q7_preemptivo_s1():
    res = calcular_preemptivo([0.1, 0.4, 1.5], mu=3, s=1)
    check(res, esperado_Wq=[0.011, 0.080, 0.867])


# T12 — sem interrupção, s=2, μ=3, λ=(0.1, 0.4, 1.5) — Lista Q7
def test_T12_lista_q7_nao_preemptivo_s2():
    res = calcular_nao_preemptivo([0.1, 0.4, 1.5], mu=3, s=2)
    check(res, esperado_Wq=[0.028, 0.031, 0.045])


# T13 — com interrupção, s=2, μ=3, λ=(0.1, 0.4, 1.5) — Lista Q7
def test_T13_lista_q7_preemptivo_s2():
    res = calcular_preemptivo([0.1, 0.4, 1.5], mu=3, s=2)
    check(res, esperado_Wq=[0.00009, 0.00289, 0.05493])
