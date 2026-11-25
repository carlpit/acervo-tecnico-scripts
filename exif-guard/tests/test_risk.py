from exif_guard.exif import PhotoMetadata, read_exif
from exif_guard.risk import LEVEL_ALTO, LEVEL_BAIXO, LEVEL_MEDIO, score_risk


def test_gps_e_alto(photos_dir):
    risk = score_risk(read_exif(photos_dir / "com_gps.jpg"))
    assert risk.level == LEVEL_ALTO
    assert any("GPS" in reason for reason in risk.reasons)


def test_aparelho_sem_gps_e_medio(photos_dir):
    risk = score_risk(read_exif(photos_dir / "so_aparelho.jpg"))
    assert risk.level == LEVEL_MEDIO
    assert any("aparelho" in reason for reason in risk.reasons)


def test_serial_sem_gps_e_medio(photos_dir):
    risk = score_risk(read_exif(photos_dir / "so_serial.jpg"))
    assert risk.level == LEVEL_MEDIO
    assert any("série" in reason for reason in risk.reasons)


def test_apenas_data_e_baixo(photos_dir):
    risk = score_risk(read_exif(photos_dir / "so_data.jpg"))
    assert risk.level == LEVEL_BAIXO


def test_imagem_limpa_e_baixa(photos_dir):
    risk = score_risk(read_exif(photos_dir / "limpa.jpg"))
    assert risk.level == LEVEL_BAIXO
    assert risk.reasons == ["sem metadados sensíveis"]


def test_erro_fica_baixo():
    risk = score_risk(PhotoMetadata(path="x.jpg", error="falha ao ler EXIF: teste"))
    assert risk.level == LEVEL_BAIXO
    assert "não foi possível classificar" in risk.reasons[0]
