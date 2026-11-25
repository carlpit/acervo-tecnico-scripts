"""Fixtures: JPEGs de teste com EXIF sintético (coordenadas e serial fictícios)."""

from __future__ import annotations

from pathlib import Path

import piexif
import pytest
from PIL import Image

# 10°30'00" N, 20°15'36" E → 10.5, 20.26 (valores propositalmente fictícios)
FAKE_GPS_LAT = ((10, 1), (30, 1), (0, 1))
FAKE_GPS_LON = ((20, 1), (15, 1), (36, 1))
EXPECTED_LAT = 10.5
EXPECTED_LON = 20.26


def _save_jpeg(
    path: Path,
    exif_dict: dict | None = None,
    color: tuple[int, int, int] = (40, 80, 120),
) -> Path:
    image = Image.new("RGB", (64, 48), color=color)
    kwargs: dict = {"format": "JPEG", "quality": 90}
    if exif_dict is not None:
        kwargs["exif"] = piexif.dump(exif_dict)
    image.save(path, **kwargs)
    return path


def _exif(
    *,
    make: str | None = None,
    model: str | None = None,
    software: str | None = None,
    datetime: str | None = None,
    serial: str | None = None,
    gps: tuple | None = None,
) -> dict:
    zeroth: dict = {}
    exif_ifd: dict = {}
    gps_ifd: dict = {}
    if make:
        zeroth[piexif.ImageIFD.Make] = make
    if model:
        zeroth[piexif.ImageIFD.Model] = model
    if software:
        zeroth[piexif.ImageIFD.Software] = software
    if datetime:
        zeroth[piexif.ImageIFD.DateTime] = datetime
        exif_ifd[piexif.ExifIFD.DateTimeOriginal] = datetime
    if serial:
        exif_ifd[piexif.ExifIFD.BodySerialNumber] = serial
    if gps:
        lat, lat_ref, lon, lon_ref = gps
        gps_ifd[piexif.GPSIFD.GPSLatitude] = lat
        gps_ifd[piexif.GPSIFD.GPSLatitudeRef] = lat_ref
        gps_ifd[piexif.GPSIFD.GPSLongitude] = lon
        gps_ifd[piexif.GPSIFD.GPSLongitudeRef] = lon_ref
    return {"0th": zeroth, "Exif": exif_ifd, "GPS": gps_ifd}


@pytest.fixture
def photos_dir(tmp_path: Path) -> Path:
    folder = tmp_path / "fotos"
    folder.mkdir()

    _save_jpeg(
        folder / "com_gps.jpg",
        _exif(
            make="FakePhone",
            model="Pixel Test",
            software="TestCam 1.0",
            datetime="2026:11:25 12:00:00",
            serial="SN-TEST-0001",
            gps=(FAKE_GPS_LAT, "N", FAKE_GPS_LON, "E"),
        ),
        color=(200, 30, 30),
    )
    _save_jpeg(
        folder / "so_aparelho.jpg",
        _exif(make="FakePhone", model="Pixel Test", software="TestCam 1.0"),
        color=(30, 200, 30),
    )
    _save_jpeg(
        folder / "so_serial.jpg",
        _exif(serial="SN-TEST-0002"),
        color=(30, 30, 200),
    )
    _save_jpeg(
        folder / "so_data.jpg",
        _exif(datetime="2026:01:02 03:04:05", software="Editor 2.0"),
        color=(200, 200, 30),
    )
    _save_jpeg(folder / "limpa.jpg", color=(180, 180, 180))
    _save_jpeg(
        folder / "gps_sw.jpg",
        _exif(gps=(FAKE_GPS_LAT, "S", FAKE_GPS_LON, "W")),
        color=(200, 30, 200),
    )
    return folder
