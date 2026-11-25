"""Gera cópias de imagens sem metadados, sem alterar os originais."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError


class StripError(Exception):
    """Falha ao gerar a cópia limpa (nunca indica alteração do original)."""


def _format_for(src: Path, image: Image.Image) -> str:
    name = (image.format or src.suffix.lstrip(".") or "JPEG").upper()
    if name == "JPG":
        return "JPEG"
    return name


def strip_copy(src: str | Path, dest: str | Path) -> Path:
    """Grava uma cópia sem EXIF/IPTC/XMP. Recusa sobrescrever qualquer arquivo existente."""
    src = Path(src)
    dest = Path(dest)
    if dest.resolve() == src.resolve():
        raise StripError("recusando sobrescrever o arquivo original")
    if dest.exists():
        raise StripError(f"destino já existe, recusando sobrescrita: {dest}")

    dest.parent.mkdir(parents=True, exist_ok=True)

    try:
        with Image.open(src) as image:
            image = ImageOps.exif_transpose(image) or image
            cleaned = Image.frombytes(image.mode, image.size, image.tobytes())
            format_name = _format_for(src, image)
    except (UnidentifiedImageError, OSError) as exc:
        raise StripError(f"não foi possível abrir {src}: {exc}") from exc

    save_kwargs: dict = {}
    if format_name == "JPEG":
        save_kwargs["quality"] = 95
        save_kwargs["exif"] = b""

    try:
        cleaned.save(dest, format=format_name, **save_kwargs)
    except OSError as exc:
        raise StripError(f"não foi possível gravar {dest}: {exc}") from exc
    return dest


def destination_for(src: Path, root: Path, out_dir: Path) -> Path:
    try:
        relative = src.relative_to(root)
    except ValueError:
        relative = Path(src.name)
    return out_dir / relative
