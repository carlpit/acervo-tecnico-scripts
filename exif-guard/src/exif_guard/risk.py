"""Classificação de risco de privacidade a partir dos metadados EXIF."""

from __future__ import annotations

from dataclasses import dataclass, field

from exif_guard.exif import PhotoMetadata

LEVEL_ALTO = "alto"
LEVEL_MEDIO = "medio"
LEVEL_BAIXO = "baixo"

_LEVEL_LABEL = {
    LEVEL_ALTO: "Alto",
    LEVEL_MEDIO: "Médio",
    LEVEL_BAIXO: "Baixo",
}


@dataclass
class RiskAssessment:
    level: str
    reasons: list[str] = field(default_factory=list)

    @property
    def label(self) -> str:
        return _LEVEL_LABEL.get(self.level, self.level)

    def to_dict(self) -> dict:
        return {"level": self.level, "label": self.label, "reasons": list(self.reasons)}


def score_risk(meta: PhotoMetadata) -> RiskAssessment:
    """GPS = alto; fabricante, modelo ou serial = médio; demais casos = baixo."""
    if meta.error:
        return RiskAssessment(LEVEL_BAIXO, [f"não foi possível classificar: {meta.error}"])

    reasons: list[str] = []
    has_gps = meta.latitude is not None and meta.longitude is not None
    has_device = bool(meta.make or meta.model)
    has_serial = bool(meta.serial)

    if has_gps:
        reasons.append("GPS presente (localização exata)")
    if has_device:
        parts = [part for part in (meta.make, meta.model) if part]
        reasons.append("aparelho: " + " ".join(parts))
    if has_serial:
        reasons.append("número de série do dispositivo")

    if has_gps:
        return RiskAssessment(LEVEL_ALTO, reasons)
    if has_device or has_serial:
        return RiskAssessment(LEVEL_MEDIO, reasons)
    if meta.datetime:
        reasons.append("data/hora da captura")
    if meta.software:
        reasons.append(f"software: {meta.software}")
    if not reasons:
        reasons.append("sem metadados sensíveis")
    return RiskAssessment(LEVEL_BAIXO, reasons)
