import pytest

from exif_guard.exif import dms_to_decimal, iter_images, map_link, read_exif

# Mesmos valores fictícios gerados em conftest.py
FAKE_GPS_LAT = ((10, 1), (30, 1), (0, 1))
FAKE_GPS_LON = ((20, 1), (15, 1), (36, 1))
EXPECTED_LAT = 10.5
EXPECTED_LON = 20.26


def test_dms_to_decimal_norte_leste():
    assert dms_to_decimal(FAKE_GPS_LAT, "N") == pytest.approx(EXPECTED_LAT)
    assert dms_to_decimal(FAKE_GPS_LON, "E") == pytest.approx(EXPECTED_LON)


def test_dms_to_decimal_sul_oeste():
    assert dms_to_decimal(FAKE_GPS_LAT, "S") == pytest.approx(-EXPECTED_LAT)
    assert dms_to_decimal(FAKE_GPS_LON, "W") == pytest.approx(-EXPECTED_LON)


def test_map_link_contem_coordenadas():
    url = map_link(10.5, 20.26)
    assert "10.500000" in url
    assert "20.260000" in url
    assert url.startswith("https://www.openstreetmap.org/")


def test_read_exif_gps(photos_dir):
    meta = read_exif(photos_dir / "com_gps.jpg")
    assert meta.latitude == pytest.approx(EXPECTED_LAT)
    assert meta.longitude == pytest.approx(EXPECTED_LON)
    assert meta.map_url is not None
    assert "10.500000" in meta.map_url
    assert meta.make == "FakePhone"
    assert meta.model == "Pixel Test"
    assert meta.serial == "SN-TEST-0001"
    assert meta.datetime == "2026:11:25 12:00:00"
    assert meta.software == "TestCam 1.0"
    assert meta.error is None


def test_read_exif_hemisphere_sul_oeste(photos_dir):
    meta = read_exif(photos_dir / "gps_sw.jpg")
    assert meta.latitude == pytest.approx(-EXPECTED_LAT)
    assert meta.longitude == pytest.approx(-EXPECTED_LON)
    assert meta.map_url is not None


def test_read_exif_sem_gps(photos_dir):
    meta = read_exif(photos_dir / "so_aparelho.jpg")
    assert meta.latitude is None
    assert meta.longitude is None
    assert meta.map_url is None
    assert meta.make == "FakePhone"


def test_read_exif_imagem_limpa(photos_dir):
    meta = read_exif(photos_dir / "limpa.jpg")
    assert meta.make is None
    assert meta.latitude is None
    assert meta.error is None


def test_iter_images_ignora_nao_imagem(photos_dir):
    (photos_dir / "notas.txt").write_text("oi", encoding="utf-8")
    names = {path.name for path in iter_images(photos_dir)}
    assert "com_gps.jpg" in names
    assert "limpa.jpg" in names
    assert "notas.txt" not in names
