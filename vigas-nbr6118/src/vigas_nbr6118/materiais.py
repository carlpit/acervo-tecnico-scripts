"""Materiais: concreto e aço (NBR 6118 / NBR 7480).

Unidades internas: MPa para resistências; as conversões para kN/cm² ficam
explícitas nas propriedades ``*_kn_cm2`` (1 kN/cm² = 10 MPa).
"""

from __future__ import annotations

from dataclasses import dataclass

GAMMA_C_PADRAO = 1.4  # NBR 6118, tabela 12.1 (combinações normais)
GAMMA_S_PADRAO = 1.15  # NBR 6118, tabela 12.1 (combinações normais)
ES_MPA = 210_000.0  # NBR 6118, 8.3.5
EPS_CU = 3.5e-3  # encurtamento último do concreto, fck <= 50 MPa (8.2.10.1)
EPS_SU = 10.0e-3  # alongamento último convencional do aço (17.2.2)

FCK_MIN = 20.0
FCK_MAX = 50.0  # escopo da v1: grupo I (parâmetros λ = 0,8 e αc = 0,85)

ACOS_FYK = {"CA-25": 250.0, "CA-50": 500.0, "CA-60": 600.0}


@dataclass(frozen=True)
class Concreto:
    fck: float  # MPa
    gamma_c: float = GAMMA_C_PADRAO

    def __post_init__(self) -> None:
        if not FCK_MIN <= self.fck <= FCK_MAX:
            raise ValueError(
                f"fck = {self.fck} MPa fora do escopo ({FCK_MIN:.0f} a {FCK_MAX:.0f} MPa)."
            )
        if self.gamma_c < 1.0:
            raise ValueError("gamma_c deve ser >= 1,0.")

    @property
    def fcd(self) -> float:
        """Resistência de cálculo à compressão (MPa)."""
        return self.fck / self.gamma_c

    @property
    def fcd_kn_cm2(self) -> float:
        return self.fcd / 10.0


@dataclass(frozen=True)
class Aco:
    nome: str
    fyk: float  # MPa
    gamma_s: float = GAMMA_S_PADRAO
    es: float = ES_MPA  # MPa

    def __post_init__(self) -> None:
        if self.fyk <= 0:
            raise ValueError("fyk deve ser positivo.")
        if self.gamma_s < 1.0:
            raise ValueError("gamma_s deve ser >= 1,0.")

    @classmethod
    def from_nome(cls, nome: str, gamma_s: float = GAMMA_S_PADRAO) -> Aco:
        chave = nome.strip().upper().replace(" ", "-")
        if chave not in ACOS_FYK:
            raise ValueError(
                f"Aço '{nome}' desconhecido. Opções: {', '.join(ACOS_FYK)}."
            )
        return cls(nome=chave, fyk=ACOS_FYK[chave], gamma_s=gamma_s)

    @property
    def fyd(self) -> float:
        """Resistência de cálculo ao escoamento (MPa)."""
        return self.fyk / self.gamma_s

    @property
    def fyd_kn_cm2(self) -> float:
        return self.fyd / 10.0

    @property
    def es_kn_cm2(self) -> float:
        return self.es / 10.0

    @property
    def eps_yd(self) -> float:
        """Deformação de início de escoamento de cálculo (adimensional)."""
        return self.fyd / self.es
