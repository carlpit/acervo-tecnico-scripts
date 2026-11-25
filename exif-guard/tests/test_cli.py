from pathlib import Path

from exif_guard.cli import main


def test_cli_lista_gps_e_risco(photos_dir, capsys, tmp_path: Path):
    md_path = tmp_path / "out.md"
    json_path = tmp_path / "out.json"
    code = main([str(photos_dir), "--md", str(md_path), "--json", str(json_path)])
    assert code == 0
    out = capsys.readouterr().out
    assert "com_gps.jpg" in out
    assert "10.500000" in out
    assert "openstreetmap.org" in out
    assert "Alto" in out
    assert "resumo:" in out
    assert md_path.is_file()
    assert json_path.is_file()
    assert "com_gps.jpg" in md_path.read_text(encoding="utf-8")


def test_cli_no_report(photos_dir, capsys, tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    code = main([str(photos_dir), "--no-report"])
    assert code == 0
    out = capsys.readouterr().out
    assert "relatório Markdown" not in out
    assert not (tmp_path / "relatorio-exif.md").exists()


def test_cli_pasta_invalida(tmp_path: Path, capsys):
    code = main([str(tmp_path / "nao-existe")])
    assert code == 1
    err = capsys.readouterr().err
    assert "não é uma pasta" in err
