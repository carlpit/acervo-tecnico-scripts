"""Geometria da seção retangular (unidades: cm)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SecaoRetangular:
    b: float  # largura (cm)
    h: float  # altura total (cm)
    d: float  # altura útil (cm)
    d_linha: float = 4.0  # distância da face comprimida ao CG da armadura comprimida (cm)

    def __post_init__(self) -> None:
        if self.b <= 0 or self.h <= 0:
            raise ValueError("b e h devem ser positivos.")
        if not 0 < self.d < self.h:
            raise ValueError(f"d = {self.d} cm deve estar entre 0 e h = {self.h} cm.")
        if not 0 < self.d_linha < self.d:
            raise ValueError("d' deve estar entre 0 e d.")

    @property
    def area(self) -> float:
        """Área bruta Ac (cm²)."""
        return self.b * self.h
