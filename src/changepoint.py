"""Modèles de signature énergétique à point d'inflexion (ASHRAE Guideline 14).

    3P refroidissement : E = b0 + b1 * max(0, T - Tc)
    3P chauffage       : E = b0 + b1 * max(0, Th - T)
    5P                 : E = b0 + bh * max(0, Th - T) + bc * max(0, T - Tc),  Th <= Tc

Les températures d'inflexion sont trouvées par balayage (grid search) ; pour chaque
valeur candidate, les coefficients sont obtenus par moindres carrés ordinaires.
"""

from dataclasses import dataclass

import numpy as np

GRID = np.arange(0, 35.01, 0.25)


@dataclass
class ChangePointModel:
    kind: str  # "3PC", "3PH" ou "5P"
    th: float | None
    tc: float | None
    coef: np.ndarray
    sse: float
    n_params: int

    def design(self, T):
        return _design(np.asarray(T, float), self.kind, self.th, self.tc)

    def predict(self, T):
        return self.design(T) @ self.coef

    def __str__(self):
        parts = [f"{self.kind}", f"talon={self.coef[0]:.0f}"]
        if self.kind == "3PC":
            parts += [f"Tc={self.tc:.2f} °C", f"pente froid={self.coef[1]:.1f}"]
        elif self.kind == "3PH":
            parts += [f"Th={self.th:.2f} °C", f"pente chaud={self.coef[1]:.1f}"]
        else:
            parts += [
                f"Th={self.th:.2f} °C",
                f"pente chaud={self.coef[1]:.1f}",
                f"Tc={self.tc:.2f} °C",
                f"pente froid={self.coef[2]:.1f}",
            ]
        return " | ".join(parts)


def _design(T, kind, th, tc):
    cols = [np.ones_like(T)]
    if kind in ("3PH", "5P"):
        cols.append(np.maximum(0, th - T))
    if kind in ("3PC", "5P"):
        cols.append(np.maximum(0, T - tc))
    return np.column_stack(cols)


def _ols(X, E):
    coef, *_ = np.linalg.lstsq(X, E, rcond=None)
    return coef, float(((E - X @ coef) ** 2).sum())


def fit(T, E, kind: str = "3PC", grid=GRID) -> ChangePointModel:
    T, E = np.asarray(T, float), np.asarray(E, float)
    best = None
    if kind == "3PC":
        candidates = [(None, tc) for tc in grid]
    elif kind == "3PH":
        candidates = [(th, None) for th in grid]
    elif kind == "5P":
        candidates = [(th, tc) for th in grid for tc in grid if tc >= th]
    else:
        raise ValueError(kind)

    for th, tc in candidates:
        coef, sse = _ols(_design(T, kind, th, tc), E)
        if best is None or sse < best[0]:
            best = (sse, th, tc, coef)
    sse, th, tc, coef = best
    n_params = {"3PC": 3, "3PH": 3, "5P": 5}[kind]
    return ChangePointModel(kind, th, tc, coef, sse, n_params)
