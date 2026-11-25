"""CLI do exif-guard."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from exif_guard.exif import iter_images, read_exif
from exif_guard.report import assess_files, write_reports


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="exif-guard",
        description=(
            "Audita metadados EXIF de fotos próprias: GPS (decimal + link de mapa), "
            "aparelho, serial, data/hora e software, com score de risco e relatório. "
            "Use apenas em arquivos seus ou com autorização expressa."
        ),
    )
    parser.add_argument("pasta", type=Path, help="Pasta com as fotos")
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Percorre subpastas",
    )
    parser.add_argument(
        "--md",
        type=Path,
        default=Path("relatorio-exif.md"),
        help="Caminho do relatório Markdown (padrão: relatorio-exif.md)",
    )
    parser.add_argument(
        "--json",
        type=Path,
        default=Path("relatorio-exif.json"),
        help="Caminho do relatório JSON (padrão: relatorio-exif.json)",
    )
    parser.add_argument(
        "--no-report",
        action="store_true",
        help="Não grava relatórios em arquivo",
    )
    return parser


def _print_item(item) -> None:
    meta = item.meta
    print(f"arquivo : {meta.path}")
    if meta.error:
        print(f"  erro  : {meta.error}")
        print()
        return
    print(f"  risco : {item.risk.label}")
    print(f"  make  : {meta.make or '—'}")
    print(f"  model : {meta.model or '—'}")
    print(f"  serial: {meta.serial or '—'}")
    print(f"  data  : {meta.datetime or '—'}")
    print(f"  soft  : {meta.software or '—'}")
    if meta.latitude is not None and meta.longitude is not None:
        print(f"  GPS   : {meta.latitude:.6f}, {meta.longitude:.6f}")
        print(f"  mapa  : {meta.map_url}")
    else:
        print("  GPS   : —")
    if item.risk.reasons:
        print(f"  motivos: {'; '.join(item.risk.reasons)}")
    print()


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    pasta = args.pasta
    if not pasta.is_dir():
        print(f"erro: não é uma pasta: {pasta}", file=sys.stderr)
        return 1

    fotos = iter_images(pasta, recursive=args.recursive)
    if not fotos:
        print(f"nenhuma imagem encontrada em {pasta}")
        return 0

    reports = assess_files([read_exif(foto) for foto in fotos])
    for item in reports:
        _print_item(item)

    altos = sum(1 for item in reports if item.risk.level == "alto")
    medios = sum(1 for item in reports if item.risk.level == "medio")
    baixos = sum(1 for item in reports if item.risk.level == "baixo")
    print(f"resumo: {len(reports)} arquivo(s) — alto: {altos}, médio: {medios}, baixo: {baixos}")

    if not args.no_report:
        md_path, json_path = write_reports(
            reports,
            pasta=str(pasta),
            markdown_path=args.md,
            json_path=args.json,
        )
        print(f"relatório Markdown: {md_path}")
        print(f"relatório JSON    : {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
