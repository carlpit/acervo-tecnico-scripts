import hashlib
from pathlib import Path

import piexif
import pytest
from PIL import Image

from exif_guard.exif import read_exif
from exif_guard.strip import StripError, destination_for, strip_copy


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_strip_remove_exif_e_preserva_original(photos_dir, tmp_path: Path):
    src = photos_dir / "com_gps.jpg"
    before = _sha256(src)
    dest = tmp_path / "limpo" / "com_gps.jpg"

    result = strip_copy(src, dest)
    assert result == dest
    assert dest.is_file()
    assert _sha256(src) == before

    meta = read_exif(dest)
    assert meta.latitude is None
    assert meta.longitude is None
    assert meta.make is None
    assert meta.model is None
    assert meta.serial is None
    assert meta.datetime is None
    assert meta.software is None
    assert meta.error is None

    residual = Image.open(dest).getexif()
    assert len(residual) == 0


def test_strip_recusa_destino_existente(photos_dir, tmp_path: Path):
    src = photos_dir / "com_gps.jpg"
    dest = tmp_path / "com_gps.jpg"
    dest.write_bytes(b"ocupado")
    with pytest.raises(StripError, match="já existe"):
        strip_copy(src, dest)
    assert dest.read_bytes() == b"ocupado"


def test_strip_recusa_sobrescrever_original(photos_dir):
    src = photos_dir / "com_gps.jpg"
    before = _sha256(src)
    with pytest.raises(StripError, match="original"):
        strip_copy(src, src)
    assert _sha256(src) == before


def test_destination_preserva_subpasta(tmp_path: Path):
    root = tmp_path / "fotos"
    src = root / "album" / "praia.jpg"
    out = tmp_path / "limpo"
    assert destination_for(src, root, out) == out / "album" / "praia.jpg"


def test_piexif_nao_encontra_gps_depois_do_strip(photos_dir, tmp_path: Path):
    src = photos_dir / "com_gps.jpg"
    dest = tmp_path / "limpo.jpg"
    strip_copy(src, dest)
    try:
        loaded = piexif.load(str(dest))
    except piexif.InvalidImageDataError:
        return
    gps = loaded.get("GPS") or {}
    zeroth = loaded.get("0th") or {}
    assert not gps
    assert piexif.ImageIFD.Make not in zeroth
