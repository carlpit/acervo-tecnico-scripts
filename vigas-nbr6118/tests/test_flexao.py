import math

import pytest

from vigas_nbr6118.flexao import dimensionar, rho_min_percentual, sugerir_barras
from vigas_nbr6118.materiais import Aco, Concreto
from vigas_nbr6118.secao import SecaoRetangular

CA50 = Aco.from_nome("CA-50")


def secao_20x50():
    return SecaoRetangular(b=20, h=50, d=45)


def test_caso_referencia_armadura_simples():
    """20×50, d = 45, C25, CA-50, Mk = 100 kN·m — conferido à mão."""
    r = dimensionar(secao_20x50(), Concreto(25), CA50, mk_knm=100)
    assert r.md == pytest.approx(14_000)
    assert r.x == pytest.approx(14.74, abs=0.02)
    assert r.x_d == pytest.approx(0.327, abs=0.002)
    assert r.as_tracao == pytest.approx(8.23, abs=0.02)
    assert r.dominio == "3"
    assert not r.armadura_dupla
    assert r.atende_as_max


def test_equilibrio_armadura_simples():
    """Rcc = Rst e Rcc·z = Md (independe da fórmula fechada)."""
    s, c = secao_20x50(), Concreto(30)
    r = dimensionar(s, c, CA50, mk_knm=120)
    rcc = 0.68 * c.fcd_kn_cm2 * s.b * r.x
    rst = r.as_calculada * CA50.fyd_kn_cm2
    assert rcc == pytest.approx(rst, rel=1e-9)
    assert rcc * r.z == pytest.approx(r.md, rel=1e-9)


def test_armadura_minima_governa():
    r = dimensionar(secao_20x50(), Concreto(25), CA50, mk_knm=5)
    assert r.as_calculada < r.as_min
    assert r.as_tracao == pytest.approx(0.0015 * 20 * 50)
    assert any("mínima" in a for a in r.avisos)


def test_armadura_dupla_e_equilibrio():
    s, c = secao_20x50(), Concreto(25)
    r = dimensionar(s, c, CA50, mk_knm=250)
    assert r.armadura_dupla
    assert r.x_d == pytest.approx(0.45)
    assert r.as_compressao > 0
    rcc = 0.68 * c.fcd_kn_cm2 * s.b * r.x
    # equilíbrio de forças
    assert rcc + r.as_compressao * r.sigma_s2 == pytest.approx(
        r.as_calculada * CA50.fyd_kn_cm2, rel=1e-9
    )
    # equilíbrio de momentos em torno da armadura tracionada
    m = rcc * r.z + r.as_compressao * r.sigma_s2 * (s.d - s.d_linha)
    assert m == pytest.approx(r.md, rel=1e-9)


def test_limite_ductilidade_exato():
    """Md exatamente igual a Md,lim deve dar x/d = 0,45 com armadura simples."""
    s, c = secao_20x50(), Concreto(25)
    ref = dimensionar(s, c, CA50, mk_knm=1)
    mk_lim = ref.md_lim / 100 / 1.4
    r = dimensionar(s, c, CA50, mk_knm=mk_lim)
    assert not r.armadura_dupla
    assert r.x_d == pytest.approx(0.45, abs=1e-9)


@pytest.mark.parametrize(
    "fck, esperado", [(20, 0.150), (30, 0.150), (35, 0.164), (37.5, 0.1715), (50, 0.208)]
)
def test_rho_min(fck, esperado):
    assert rho_min_percentual(fck) == pytest.approx(esperado)


def test_limites_dominio_ca50():
    r = dimensionar(secao_20x50(), Concreto(25), CA50, mk_knm=10)
    assert r.x23 == pytest.approx(0.2593 * 45, rel=1e-3)
    assert r.x34 == pytest.approx(0.6283 * 45, rel=1e-3)
    assert r.dominio == "2"


def test_as_max_estoura():
    s = SecaoRetangular(b=12, h=30, d=26)
    r = dimensionar(s, Concreto(20), CA50, mk_knm=200)
    assert not r.atende_as_max


def test_aviso_fck_acima_40():
    r = dimensionar(secao_20x50(), Concreto(45), CA50, mk_knm=100)
    assert any("40 MPa" in a for a in r.avisos)


@pytest.mark.parametrize(
    "kwargs",
    [dict(b=0, h=50, d=45), dict(b=20, h=50, d=55), dict(b=20, h=50, d=45, d_linha=50)],
)
def test_secao_invalida(kwargs):
    with pytest.raises(ValueError):
        SecaoRetangular(**kwargs)


@pytest.mark.parametrize("fck", [15, 55])
def test_fck_fora_do_escopo(fck):
    with pytest.raises(ValueError):
        Concreto(fck)


def test_aco_invalido():
    with pytest.raises(ValueError):
        Aco.from_nome("CA-70")


def test_momento_nao_positivo():
    with pytest.raises(ValueError):
        dimensionar(secao_20x50(), Concreto(25), CA50, mk_knm=0)


def test_sugerir_barras_cobre_as():
    for phi, n, aef in sugerir_barras(8.23):
        assert aef >= 8.23
        assert n >= 2
        assert aef == pytest.approx(n * math.pi * (phi / 10) ** 2 / 4)
