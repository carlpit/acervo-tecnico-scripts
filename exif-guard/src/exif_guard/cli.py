"""CLI do exif-guard."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from exif_guard.exif import iter_images, read_exif


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="exif-guard",
        description=(
            "Audita metadados EXIF de fotos próprias: GPS (decimal + link de mapa), "
            "aparelho, serial, data/hora e software. Use apenas em arquivos seus "
            "ou com autorização expressa."
        ),
    )
    parser.add_argument("pasta", type=Path, help="Pasta com as fotos")
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Percorre subpastas",
    )
    return parser


def _print_meta(meta) -> None:
    print(f"arquivo : {meta.path}")
    if meta.error:
        print(f"  erro  : {meta.error}")
        print()
        return
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

    for foto in fotos:
        _print_meta(read_exif(foto))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
