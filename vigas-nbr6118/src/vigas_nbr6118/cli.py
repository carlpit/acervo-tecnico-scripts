"""Interface de linha de comando (Typer)."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Annotated, Optional

import typer

from . import __version__
from .flexao import dimensionar, sugerir_barras
from .materiais import Aco, Concreto
from .memorial import gerar_memorial
from .secao import SecaoRetangular

app = typer.Typer(
    help="Dimensionamento de vigas retangulares de concreto armado à flexão simples (NBR 6118).",
    no_args_is_help=True,
    add_completion=False,
)


def _versao(valor: bool) -> None:
    if valor:
        typer.echo(f"vigas-nbr6118 {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    versao: Annotated[
        Optional[bool],
        typer.Option("--versao", callback=_versao, is_eager=True, help="Mostra a versão."),
    ] = None,
) -> None:
    """vigas-nbr6118."""


@app.command("dimensionar")
def cmd_dimensionar(
    b: Annotated[float, typer.Option(help="Largura b (cm).")],
    h: Annotated[float, typer.Option(help="Altura h (cm).")],
    fck: Annotated[float, typer.Option(help="fck do concreto (MPa), 20 a 50.")],
    mk: Annotated[float, typer.Option(help="Momento característico Mk (kN·m).")],
    d: Annotated[Optional[float], typer.Option(help="Altura útil d (cm). Padrão: h − 5.")] = None,
    d_linha: Annotated[
        float, typer.Option("--d-linha", help="d' da armadura comprimida (cm).")
    ] = 4.0,
    aco: Annotated[str, typer.Option(help="CA-25, CA-50 ou CA-60.")] = "CA-50",
    gamma_f: Annotated[float, typer.Option("--gamma-f", help="Coeficiente γf.")] = 1.4,
    gamma_c: Annotated[float, typer.Option("--gamma-c", help="Coeficiente γc.")] = 1.4,
    gamma_s: Annotated[float, typer.Option("--gamma-s", help="Coeficiente γs.")] = 1.15,
    titulo: Annotated[str, typer.Option(help="Nome da viga no memorial.")] = "Viga",
    memorial: Annotated[
        Optional[Path], typer.Option(help="Salva o memorial em Markdown neste arquivo.")
    ] = None,
    saida_json: Annotated[bool, typer.Option("--json", help="Saída em JSON.")] = False,
) -> None:
    """Calcula As (e As', se necessário) e o domínio de deformação."""
    try:
        d_util = d if d is not None else h - 5.0
        secao = SecaoRetangular(b=b, h=h, d=d_util, d_linha=d_linha)
        concreto = Concreto(fck=fck, gamma_c=gamma_c)
        mat_aco = Aco.from_nome(aco, gamma_s=gamma_s)
        r = dimensionar(secao, concreto, mat_aco, mk, gamma_f)
    except ValueError as e:
        typer.secho(f"Erro: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from e

    if saida_json:
        dados = asdict(r)
        dados["entrada"] = {"b": b, "h": h, "d": d_util, "d_linha": d_linha, "fck": fck,
                            "aco": mat_aco.nome, "mk_knm": mk, "gamma_f": gamma_f}
        typer.echo(json.dumps(dados, ensure_ascii=False, indent=2))
    else:
        if d is None:
            typer.echo(f"(d não informado: assumido d = h − 5 = {d_util:g} cm)")
        typer.echo(f"Md      = {r.md / 100:.2f} kN·m")
        typer.echo(f"x       = {r.x:.2f} cm   (x/d = {r.x_d:.3f}, domínio {r.dominio})")
        typer.echo(f"As,calc = {r.as_calculada:.2f} cm²   As,mín = {r.as_min:.2f} cm²")
        typer.secho(f"As      = {r.as_tracao:.2f} cm²", bold=True)
        if r.armadura_dupla:
            typer.secho(f"As'     = {r.as_compressao:.2f} cm²", bold=True)
        barras = ", ".join(f"{n}φ{phi:g}" for phi, n, _ in sugerir_barras(r.as_tracao)[:4])
        typer.echo(f"Barras  : {barras}")
        for av in r.avisos:
            typer.secho(f"⚠ {av}", fg=typer.colors.YELLOW)

    if memorial is not None:
        memorial.write_text(
            gerar_memorial(secao, concreto, mat_aco, mk, gamma_f, r, titulo), encoding="utf-8"
        )
        typer.echo(f"Memorial salvo em {memorial}", err=saida_json)

    if not r.atende_as_max:
        raise typer.Exit(code=2)


if __name__ == "__main__":
    app()
