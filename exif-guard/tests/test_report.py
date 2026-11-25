import json
from pathlib import Path

from exif_guard.exif import read_exif
from exif_guard.report import assess_files, render_json, render_markdown, write_reports


def test_relatorio_markdown_e_json(photos_dir, tmp_path: Path):
    metas = [read_exif(path) for path in sorted(photos_dir.glob("*.jpg"))]
    reports = assess_files(metas)

    markdown = render_markdown(reports, pasta=str(photos_dir))
    assert "# Relatório exif-guard" in markdown
    assert "America/Fortaleza" in markdown
    assert "com_gps.jpg" in markdown
    assert "Alto" in markdown
    assert "openstreetmap.org" in markdown

    payload = json.loads(render_json(reports, pasta=str(photos_dir)))
    assert payload["timezone"] == "America/Fortaleza"
    assert payload["summary"]["files"] == len(reports)
    assert payload["summary"]["alto"] >= 1
    names = {Path(item["path"]).name for item in payload["files"]}
    assert "com_gps.jpg" in names
    gps_file = next(item for item in payload["files"] if item["path"].endswith("com_gps.jpg"))
    assert gps_file["risk"]["level"] == "alto"
    assert gps_file["latitude"] == 10.5

    md_path, json_path = write_reports(
        reports,
        pasta=str(photos_dir),
        markdown_path=tmp_path / "relatorio-exif.md",
        json_path=tmp_path / "relatorio-exif.json",
    )
    assert md_path.is_file()
    assert json_path.is_file()
    assert "com_gps.jpg" in md_path.read_text(encoding="utf-8")
