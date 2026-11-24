"""Dimensionamento à flexão simples — seção retangular, NBR 6118.

Modelo: diagrama retangular simplificado de tensões no concreto
(8.2.10.1, 17.2.2), com λ = 0,8 e αc = 0,85, válido para fck <= 50 MPa.

Unidades internas: kN e cm (momentos em kN·cm, tensões em kN/cm²).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from .materiais import EPS_CU, EPS_SU, Aco, Concreto
from .secao import SecaoRetangular

LAMBDA = 0.8
ALPHA_C = 0.85
X_D_LIM = 0.45  # ductilidade, fck <= 50 MPa (14.6.4.3)
RHO_MAX = 0.04  # As + As' <= 4 % Ac (17.3.5.2.4)

# Tabela 17.3 — taxas mínimas de armadura de flexão (%), seção retangular,
# γc = 1,4 e γs = 1,15. Valores intermediários: interpolação linear.
TABELA_RHO_MIN = {20: 0.150, 25: 0.150, 30: 0.150, 35: 0.164, 40: 0.179, 45: 0.194, 50: 0.208}

BITOLAS_MM = (8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 32.0)


@dataclass
class ResultadoFlexao:
    md: float  # kN·cm
    kmd: float  # Md / (b·d²·fcd)
    x: float  # cm
    x_d: float
    z: float  # cm
    dominio: str
    x23: float  # cm
    x34: float  # cm
    md_lim: float  # kN·cm (momento resistente com x/d = 0,45)
    armadura_dupla: bool
    as_calculada: float  # cm²
    as_min: float  # cm²
    as_tracao: float  # cm² (adotada = max(calculada, mínima))
    as_compressao: float  # cm²
    sigma_s2: float  # kN/cm² (tensão na armadura comprimida; 0 se simples)
    rho_min_pct: float
    as_max: float  # cm²
    atende_as_max: bool
    avisos: list[str] = field(default_factory=list)


def rho_min_percentual(fck: float) -> float:
    """Taxa mínima ρmín (%) pela tabela 17.3, com interpolação linear."""
    chaves = sorted(TABELA_RHO_MIN)
    if fck <= chaves[0]:
        return TABELA_RHO_MIN[chaves[0]]
    if fck >= chaves[-1]:
        return TABELA_RHO_MIN[chaves[-1]]
    for a, b in zip(chaves, chaves[1:], strict=False):
        if a <= fck <= b:
            ra, rb = TABELA_RHO_MIN[a], TABELA_RHO_MIN[b]
            return ra + (rb - ra) * (fck - a) / (b - a)
    raise AssertionError("inalcançável")


def classificar_dominio(x: float, x23: float, x34: float) -> str:
    if x <= x23:
        return "2"
    if x <= x34:
        return "3"
    return "4"


def dimensionar(
    secao: SecaoRetangular,
    concreto: Concreto,
    aco: Aco,
    mk_knm: float,
    gamma_f: float = 1.4,
) -> ResultadoFlexao:
    """Dimensiona As (e As', se preciso) para o momento característico ``mk_knm`` (kN·m)."""
    if mk_knm <= 0:
        raise ValueError("Mk deve ser positivo (kN·m).")
    if gamma_f < 1.0:
        raise ValueError("gamma_f deve ser >= 1,0.")

    b, d, dl = secao.b, secao.d, secao.d_linha
    fcd = concreto.fcd_kn_cm2
    fyd = aco.fyd_kn_cm2
    k = ALPHA_C * LAMBDA  # 0,68
    avisos: list[str] = []

    md = mk_knm * 100.0 * gamma_f  # kN·m -> kN·cm
    kmd = md / (b * d**2 * fcd)

    x23 = EPS_CU / (EPS_CU + EPS_SU) * d
    x34 = EPS_CU / (EPS_CU + aco.eps_yd) * d

    x_lim = X_D_LIM * d
    md_lim = k * fcd * b * x_lim * (d - LAMBDA / 2 * x_lim)

    if md <= md_lim * (1 + 1e-12):  # tolerância de arredondamento
        # Md = 0,68·fcd·b·x·(d − 0,4x)  →  x = 1,25·d·[1 − √(1 − Md/(0,425·b·d²·fcd))]
        # Raiz da equação do 2º grau em x; coef = k/(2λ) = 0,68/1,6 = 0,425
        coef = k / (2 * LAMBDA)
        x = d / LAMBDA * (1.0 - math.sqrt(1.0 - kmd / coef))
        z = d - LAMBDA / 2 * x
        as_calc = md / (fyd * z)
        as2 = 0.0
        sigma_s2 = 0.0
        dupla = False
    else:
        dupla = True
        x = x_lim
        z = d - LAMBDA / 2 * x
        if dl >= x:
            raise ValueError(
                f"d' = {dl} cm >= x_lim = {x:.2f} cm: armadura comprimida ficaria tracionada. "
                "Aumente a seção."
            )
        delta_m = md - md_lim
        eps_s2 = EPS_CU * (x - dl) / x
        sigma_s2 = min(aco.es_kn_cm2 * eps_s2, fyd)
        as2 = delta_m / (sigma_s2 * (d - dl))
        as_calc = md_lim / (fyd * z) + delta_m / (fyd * (d - dl))
        avisos.append(
            "x/d > 0,45 com armadura simples: adotada armadura dupla. "
            "Avalie aumentar h — costuma sair mais barato e mais rígido."
        )

    rho_min = rho_min_percentual(concreto.fck)
    as_min = rho_min / 100.0 * secao.area
    as_adot = max(as_calc, as_min)
    if as_min > as_calc:
        avisos.append("Armadura mínima governa (As,calc < As,mín).")

    as_max = RHO_MAX * secao.area
    atende_max = (as_adot + as2) <= as_max
    if not atende_max:
        avisos.append("As + As' > 4 % Ac: seção insuficiente, redimensione.")

    if concreto.fck > 40:
        avisos.append(
            "fck > 40 MPa: confira na NBR 6118 vigente se há fator redutor adicional "
            "da resistência do concreto (ex.: ηc) não contemplado neste modelo."
        )

    return ResultadoFlexao(
        md=md,
        kmd=kmd,
        x=x,
        x_d=x / d,
        z=z,
        dominio=classificar_dominio(x, x23, x34),
        x23=x23,
        x34=x34,
        md_lim=md_lim,
        armadura_dupla=dupla,
        as_calculada=as_calc,
        as_min=as_min,
        as_tracao=as_adot,
        as_compressao=as2,
        sigma_s2=sigma_s2,
        rho_min_pct=rho_min,
        as_max=as_max,
        atende_as_max=atende_max,
        avisos=avisos,
    )


def area_barra(phi_mm: float) -> float:
    """Área de uma barra (cm²)."""
    return math.pi * (phi_mm / 10.0) ** 2 / 4.0


def sugerir_barras(
    as_cm2: float, n_min: int = 2, n_max: int = 10
) -> list[tuple[float, int, float]]:
    """Combinações (φ mm, nº de barras, As efetiva cm²) de uma só bitola.

    Não verifica espaçamento horizontal (18.3.2.2) nem cobrimento — conferir no detalhamento.
    """
    if as_cm2 <= 0:
        return []
    opcoes = []
    for phi in BITOLAS_MM:
        n = max(n_min, math.ceil(as_cm2 / area_barra(phi) - 1e-9))
        if n <= n_max:
            opcoes.append((phi, n, n * area_barra(phi)))
    return opcoes
