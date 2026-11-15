"""Métriques de performance des modèles énergétiques (ASHRAE Guideline 14).

Seuils de calage G14 pour un modèle de référence (baseline) :
    - horaire  : CV(RMSE) <= 30 %, |NMBE| <= 10 %
    - mensuel  : CV(RMSE) <= 15 %, |NMBE| <= 5 %

Attention : sur les données d'entraînement, une régression linéaire avec constante
a un NMBE nul par construction. Le NMBE n'est informatif que hors échantillon.
"""

import numpy as np


def _arrays(y_true, y_pred):
    y, yhat = np.asarray(y_true, float), np.asarray(y_pred, float)
    mask = ~(np.isnan(y) | np.isnan(yhat))
    return y[mask], yhat[mask]


def r2(y_true, y_pred) -> float:
    y, yhat = _arrays(y_true, y_pred)
    return 1 - ((y - yhat) ** 2).sum() / ((y - y.mean()) ** 2).sum()


def cv_rmse(y_true, y_pred, n_params: int = 0) -> float:
    """CV(RMSE) en % : RMSE (corrigé des degrés de liberté) / moyenne mesurée."""
    y, yhat = _arrays(y_true, y_pred)
    rmse = np.sqrt(((y - yhat) ** 2).sum() / (len(y) - n_params))
    return 100 * rmse / y.mean()


def nmbe(y_true, y_pred, n_params: int = 0) -> float:
    """NMBE en % : biais moyen normalisé. Positif = le modèle sous-estime."""
    y, yhat = _arrays(y_true, y_pred)
    return 100 * (y - yhat).sum() / ((len(y) - n_params) * y.mean())


def report(y_true, y_pred, n_params: int = 0) -> dict:
    return {
        "R2": round(r2(y_true, y_pred), 3),
        "CV(RMSE) %": round(cv_rmse(y_true, y_pred, n_params), 1),
        "NMBE %": round(nmbe(y_true, y_pred, n_params), 2),
    }
