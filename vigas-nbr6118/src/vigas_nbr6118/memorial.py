"""Geração do memorial de cálculo em Markdown."""

from __future__ import annotations

from datetime import date

from . import __version__
from .flexao import ALPHA_C, LAMBDA, X_D_LIM, ResultadoFlexao, sugerir_barras
from .materiais import EPS_CU, EPS_SU, Aco, Concreto
from .secao import SecaoRetangular


def _n(v: float, casas: int = 2) -> str:
    """Formata número no padrão brasileiro (vírgula decimal)."""
    return f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def gerar_memorial(
    secao: SecaoRetangular,
    concreto: Concreto,
    aco: Aco,
    mk_knm: float,
    gamma_f: float,
    r: ResultadoFlexao,
    titulo: str = "Viga",
) -> str:
    b, h, d, dl = secao.b, secao.h, secao.d, secao.d_linha
    fcd, fyd = concreto.fcd_kn_cm2, aco.fyd_kn_cm2
    L: list[str] = []
    a = L.append

    a(f"# Memorial de cálculo — {titulo}: flexão simples")
    a("")
    a(f"Gerado por `vigas-nbr6118` v{__version__} em {date.today():%d/%m/%Y}.")
    a("")
    a("> **Ferramenta de estudo.** Não substitui projeto estrutural elaborado e verificado por")
    a("> engenheiro habilitado, com ART recolhida no CREA.")
    a("")
    a("## 1. Dados de entrada")
    a("")
    a("| Grandeza | Valor |")
    a("|---|---|")
    a(f"| Seção b × h | {_n(b, 1)} × {_n(h, 1)} cm |")
    a(f"| Altura útil d | {_n(d, 1)} cm |")
    a(f"| d' (armadura comprimida) | {_n(dl, 1)} cm |")
    a(f"| Concreto | C{concreto.fck:g} (fck = {concreto.fck:g} MPa) |")
    a(f"| Aço | {aco.nome} (fyk = {aco.fyk:g} MPa) |")
    a(f"| Momento característico Mk | {_n(mk_knm)} kN·m |")
    a(f"| γf / γc / γs | {_n(gamma_f)} / {_n(concreto.gamma_c)} / {_n(aco.gamma_s)} |")
    a("")
    a("## 2. Premissas")
    a("")
    a("- NBR 6118 — Projeto de estruturas de concreto (verificar edição vigente).")
    a(f"- Diagrama retangular simplificado: λ = {_n(LAMBDA, 1)}, αc = {_n(ALPHA_C)} (fck ≤ 50 MPa).")
    a(f"- εcu = {_n(EPS_CU * 1000, 1)} ‰; εsu = {_n(EPS_SU * 1000, 1)} ‰; Es = {_n(aco.es, 0)} MPa.")
    a(f"- Ductilidade: x/d ≤ {_n(X_D_LIM)} (item 14.6.4.3).")
    a("- Armadura mínima pela tabela 17.3 (seção retangular); máxima As + As' ≤ 4 % Ac.")
    a("- Não verifica: cisalhamento, fissuração, flecha, ancoragem, espaçamento entre barras.")
    a("")
    a("## 3. Cálculo")
    a("")
    a("### 3.1 Resistências e esforço de cálculo")
    a("")
    a(f"- fcd = fck/γc = {concreto.fck:g}/{_n(concreto.gamma_c)} = {_n(concreto.fcd)} MPa = {_n(fcd, 4)} kN/cm²")
    a(f"- fyd = fyk/γs = {aco.fyk:g}/{_n(aco.gamma_s)} = {_n(aco.fyd)} MPa = {_n(fyd, 3)} kN/cm²")
    a(f"- εyd = fyd/Es = {_n(aco.eps_yd * 1000, 3)} ‰")
    a(f"- Md = γf·Mk = {_n(gamma_f)} × {_n(mk_knm)} = {_n(r.md / 100)} kN·m = {_n(r.md, 0)} kN·cm")
    a("")
    a("### 3.2 Limites de domínio")
    a("")
    a(f"- x₂₃ = εcu/(εcu + εsu)·d = {_n(r.x23)} cm")
    a(f"- x₃₄ = εcu/(εcu + εyd)·d = {_n(r.x34)} cm")
    a(f"- x_lim (ductilidade) = {_n(X_D_LIM)}·d = {_n(X_D_LIM * d)} cm")
    a(f"- Md,lim = 0,68·fcd·b·x_lim·(d − 0,4·x_lim) = {_n(r.md_lim / 100)} kN·m")
    a("")
    a("### 3.3 Linha neutra e armadura")
    a("")
    if not r.armadura_dupla:
        a(f"Md = {_n(r.md / 100)} kN·m ≤ Md,lim = {_n(r.md_lim / 100)} kN·m → **armadura simples**.")
        a("")
        a(f"- KMD = Md/(b·d²·fcd) = {_n(r.kmd, 4)}")
        a(f"- x = 1,25·d·[1 − √(1 − KMD/0,425)] = **{_n(r.x)} cm**")
        a(f"- x/d = {_n(r.x_d, 3)} ≤ {_n(X_D_LIM)} ✔")
        a(f"- z = d − 0,4·x = {_n(r.z)} cm")
        a(f"- As,calc = Md/(fyd·z) = **{_n(r.as_calculada)} cm²**")
    else:
        dm = r.md - r.md_lim
        a(f"Md = {_n(r.md / 100)} kN·m > Md,lim = {_n(r.md_lim / 100)} kN·m → **armadura dupla**.")
        a("")
        a(f"- x = x_lim = {_n(r.x)} cm; z = {_n(r.z)} cm")
        a(f"- ΔM = Md − Md,lim = {_n(dm / 100)} kN·m")
        a(f"- σs' = min(Es·εcu·(x − d')/x; fyd) = {_n(r.sigma_s2, 3)} kN/cm²")
        a(f"- As' = ΔM/[σs'·(d − d')] = **{_n(r.as_compressao)} cm²**")
        a(f"- As,calc = Md,lim/(fyd·z) + ΔM/[fyd·(d − d')] = **{_n(r.as_calculada)} cm²**")
    a(f"- Domínio de deformação: **{r.dominio}**")
    a("")
    a("### 3.4 Armaduras mínima e máxima")
    a("")
    a(f"- ρmín = {_n(r.rho_min_pct, 3)} % → As,mín = {_n(r.as_min)} cm²")
    a(f"- As,máx = 4 % Ac = {_n(r.as_max)} cm² → As + As' = {_n(r.as_tracao + r.as_compressao)} cm² "
      f"{'✔' if r.atende_as_max else '✘'}")
    a("")
    a("## 4. Resultado")
    a("")
    a(f"- **As (tracionada) = {_n(r.as_tracao)} cm²**")
    if r.armadura_dupla:
        a(f"- **As' (comprimida) = {_n(r.as_compressao)} cm²**")
    a("")
    a("Sugestões de barras (uma bitola; conferir espaçamento e cobrimento no detalhamento):")
    a("")
    a("| φ (mm) | nº barras | As,ef (cm²) |")
    a("|---|---|---|")
    for phi, n, aef in sugerir_barras(r.as_tracao):
        a(f"| {_n(phi, 1)} | {n} | {_n(aef)} |")
    if r.avisos:
        a("")
        a("## 5. Avisos")
        a("")
        for av in r.avisos:
            a(f"- ⚠ {av}")
    a("")
    return "\n".join(L)
