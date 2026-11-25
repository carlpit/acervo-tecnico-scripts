from pathlib import Path

from exif_guard.cli import main


def test_cli_lista_gps(photos_dir, capsys):
    code = main([str(photos_dir)])
    assert code == 0
    out = capsys.readouterr().out
    assert "com_gps.jpg" in out
    assert "10.500000" in out
    assert "openstreetmap.org" in out


def test_cli_pasta_invalida(tmp_path: Path, capsys):
    code = main([str(tmp_path / "nao-existe")])
    assert code == 1
    err = capsys.readouterr().err
    assert "não é uma pasta" in err
