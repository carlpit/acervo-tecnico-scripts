"""Relatórios de auditoria EXIF em Markdown e JSON."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from exif_guard.exif import PhotoMetadata
from exif_guard.risk import RiskAssessment, score_risk

REPORT_TZ = ZoneInfo("America/Fortaleza")


@dataclass
class FileReport:
    meta: PhotoMetadata
    risk: RiskAssessment

    def to_dict(self) -> dict:
        payload = self.meta.to_dict()
        payload["risk"] = self.risk.to_dict()
        return payload


def assess_files(metas: list[PhotoMetadata]) -> list[FileReport]:
    return [FileReport(meta=meta, risk=score_risk(meta)) for meta in metas]


def _counts(reports: list[FileReport]) -> dict[str, int]:
    counts = {"alto": 0, "medio": 0, "baixo": 0}
    for item in reports:
        counts[item.risk.level] = counts.get(item.risk.level, 0) + 1
    return counts


def render_markdown(reports: list[FileReport], *, pasta: str) -> str:
    now = datetime.now(REPORT_TZ).strftime("%Y-%m-%d %H:%M")
    counts = _counts(reports)
    lines = [
        "# Relatório exif-guard",
        "",
        f"- Pasta auditada: `{pasta}`",
        f"- Gerado em: {now} (America/Fortaleza, UTC-3)",
        f"- Arquivos: {len(reports)}",
        f"- Risco alto: {counts['alto']} · médio: {counts['medio']} · baixo: {counts['baixo']}",
        "",
        "> Aviso: este relatório deve ser usado apenas para arquivos próprios ou com autorização.",
        "",
        "| Arquivo | Risco | GPS | Aparelho | Serial | Data/hora | Motivos |",
        "|---|---|---|---|---|---|---|",
    ]
    for item in reports:
        meta = item.meta
        gps = "—"
        if meta.latitude is not None and meta.longitude is not None:
            gps = f"{meta.latitude:.6f}, {meta.longitude:.6f}"
            if meta.map_url:
                gps = f"[{gps}]({meta.map_url})"
        aparelho = " ".join(part for part in (meta.make, meta.model) if part) or "—"
        motivos = "; ".join(item.risk.reasons) if item.risk.reasons else "—"
        name = Path(meta.path).name
        lines.append(
            f"| `{name}` | {item.risk.label} | {gps} | {aparelho} | "
            f"{meta.serial or '—'} | {meta.datetime or '—'} | {motivos} |"
        )

    altos = [item for item in reports if item.risk.level == "alto"]
    if altos:
        lines.extend(["", "## Arquivos com risco alto (GPS)", ""])
        for item in altos:
            meta = item.meta
            lines.append(f"### {Path(meta.path).name}")
            lines.append("")
            lines.append(f"- Caminho: `{meta.path}`")
            lines.append(f"- Coordenadas: {meta.latitude:.6f}, {meta.longitude:.6f}")
            if meta.map_url:
                lines.append(f"- Mapa: {meta.map_url}")
            lines.append("")

    lines.extend(
        [
            "## Como reduzir o risco",
            "",
            "Use `exif-guard PASTA --strip --out PASTA_LIMPA` para gerar **cópias** sem metadados.",
            "Os arquivos originais não são alterados.",
            "",
        ]
    )
    return "\n".join(lines)


def render_json(reports: list[FileReport], *, pasta: str) -> str:
    now = datetime.now(REPORT_TZ).isoformat()
    payload = {
        "generated_at": now,
        "timezone": "America/Fortaleza",
        "folder": pasta,
        "summary": {"files": len(reports), **_counts(reports)},
        "files": [item.to_dict() for item in reports],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def write_reports(
    reports: list[FileReport],
    *,
    pasta: str,
    markdown_path: str | Path,
    json_path: str | Path,
) -> tuple[Path, Path]:
    md_path = Path(markdown_path)
    js_path = Path(json_path)
    md_path.write_text(render_markdown(reports, pasta=pasta), encoding="utf-8")
    js_path.write_text(render_json(reports, pasta=pasta), encoding="utf-8")
    return md_path, js_path
