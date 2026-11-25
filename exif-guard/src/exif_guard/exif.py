"""Leitura de metadados EXIF de imagens, com conversão de GPS para decimal."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import piexif
from PIL import Image, UnidentifiedImageError

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".tif", ".tiff", ".webp"}

# Tags comuns de número de série (Exif IFD).
# 0xA434 = CameraSerialNumber, constante ausente no piexif 1.1.3.
_SERIAL_TAGS = (
    piexif.ExifIFD.BodySerialNumber,
    0xA434,
    piexif.ExifIFD.LensSerialNumber,
)


def _decode(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, bytes):
        text = value.split(b"\x00", 1)[0].decode("utf-8", errors="replace").strip()
        return text or None
    text = str(value).strip()
    return text or None


def _ratio_to_float(value: Any) -> float:
    if isinstance(value, (tuple, list)) and len(value) == 2:
        num, den = value
        if den == 0:
            return 0.0
        return float(num) / float(den)
    return float(value)


def dms_to_decimal(dms: tuple | list, ref: str) -> float:
    """Converte graus/minutos/segundos EXIF e a referência N/S/E/W em decimal."""
    if len(dms) != 3:
        raise ValueError("coordenada GPS deve ter 3 componentes (graus, minutos, segundos)")
    degrees = _ratio_to_float(dms[0])
    minutes = _ratio_to_float(dms[1])
    seconds = _ratio_to_float(dms[2])
    decimal = degrees + minutes / 60.0 + seconds / 3600.0
    if ref.upper() in {"S", "W"}:
        decimal = -decimal
    return decimal


def map_link(latitude: float, longitude: float) -> str:
    """Link do OpenStreetMap centrado na coordenada (sem chamar a rede)."""
    return (
        f"https://www.openstreetmap.org/?mlat={latitude:.6f}&mlon={longitude:.6f}"
        f"#map=16/{latitude:.6f}/{longitude:.6f}"
    )


def extract_gps(gps_ifd: dict) -> tuple[float, float] | None:
    lat_ref = _decode(gps_ifd.get(piexif.GPSIFD.GPSLatitudeRef))
    lon_ref = _decode(gps_ifd.get(piexif.GPSIFD.GPSLongitudeRef))
    lat = gps_ifd.get(piexif.GPSIFD.GPSLatitude)
    lon = gps_ifd.get(piexif.GPSIFD.GPSLongitude)
    if not (lat_ref and lon_ref and lat and lon):
        return None
    return dms_to_decimal(lat, lat_ref), dms_to_decimal(lon, lon_ref)


def _serial_from_exif(exif_ifd: dict) -> str | None:
    for tag in _SERIAL_TAGS:
        serial = _decode(exif_ifd.get(tag))
        if serial:
            return serial
    return None


@dataclass
class PhotoMetadata:
    path: str
    make: str | None = None
    model: str | None = None
    serial: str | None = None
    datetime: str | None = None
    software: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    map_url: str | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "make": self.make,
            "model": self.model,
            "serial": self.serial,
            "datetime": self.datetime,
            "software": self.software,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "map_url": self.map_url,
            "error": self.error,
        }


def read_exif(path: str | Path) -> PhotoMetadata:
    """Lê EXIF de um arquivo de imagem. Não faz chamadas de rede."""
    path = Path(path)
    meta = PhotoMetadata(path=str(path))
    try:
        exif_dict = piexif.load(str(path))
    except piexif.InvalidImageDataError:
        try:
            with Image.open(path) as img:
                img.verify()
        except (UnidentifiedImageError, OSError) as exc:
            meta.error = f"arquivo de imagem inválido: {exc}"
        return meta
    except (ValueError, OSError) as exc:
        meta.error = f"falha ao ler EXIF: {exc}"
        return meta

    zeroth = exif_dict.get("0th") or {}
    exif_ifd = exif_dict.get("Exif") or {}
    gps_ifd = exif_dict.get("GPS") or {}

    meta.make = _decode(zeroth.get(piexif.ImageIFD.Make))
    meta.model = _decode(zeroth.get(piexif.ImageIFD.Model))
    meta.software = _decode(zeroth.get(piexif.ImageIFD.Software))
    meta.serial = _serial_from_exif(exif_ifd)
    meta.datetime = (
        _decode(exif_ifd.get(piexif.ExifIFD.DateTimeOriginal))
        or _decode(exif_ifd.get(piexif.ExifIFD.DateTimeDigitized))
        or _decode(zeroth.get(piexif.ImageIFD.DateTime))
    )

    coords = extract_gps(gps_ifd)
    if coords:
        meta.latitude, meta.longitude = coords
        meta.map_url = map_link(meta.latitude, meta.longitude)

    return meta


def iter_images(folder: str | Path, *, recursive: bool = False) -> list[Path]:
    root = Path(folder)
    if not root.is_dir():
        raise NotADirectoryError(f"não é uma pasta: {root}")
    pattern = "**/*" if recursive else "*"
    return [
        path
        for path in sorted(root.glob(pattern))
        if path.is_file()
        and path.suffix.lower() in IMAGE_EXTENSIONS
        and not path.name.startswith(".")
    ]
