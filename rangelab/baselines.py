"""Benchmarks every range rule is compared with.

Uncalibrated practice (scored as reported, no fitting):
  practice_iqr      peer 25th-75th percentile multiples x driver (football-field default)
  practice_minmax   lowest-highest peer multiple x driver
Calibrated to the same 80% target by the grader:
  constant          one width for every firm ("x/÷ f" band)
  peer_iqr_scaled   width proportional to the peers' interquartile spread
  linear_all        regression of ln|e - c| on all inputs' percentile ranks and flags (no limit on terms)
  gbm               gradient-boosted trees on all raw inputs (black box)
  hand_rule         a rule written by the author before any agent search (HAND_RULES)
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

from . import grader
from .base import FLAG_VARS, RULE_VARS
from .rules import validate

FLOOR = 0.02

HAND_RULES = {
    m: {
        "name": f"hand rule ({m})", "multiple": m, "base": "peer_iqr",
        "mechanism": "Wider ranges for firms whose value rests on expectations rather than current "
                     "profits: small, research-heavy and loss-making firms.",
        "terms": {"log_sales": -1.0, "rnd_intensity": 0.5},
        "conditions": [{"if": [{"var": "loss_making"}], "times": 1.3}],
    }
    for m in ("EV/EBITDA", "EV/Sales")
}


def _target(t: pd.DataFrame, fit: np.ndarray) -> np.ndarray:
    e = t["e"].to_numpy()
    return np.abs(e - np.median(e[fit]))


def cross_fitted(t: pd.DataFrame, fit_predict):
    """Wrap a learned method so calibration never sees in-sample predictions.

    fit_predict(train_mask) trains on those rows and returns predictions for every row. On the fit
    years, each year's scores come from a model trained on the other fit years (out of fold);
    every other row is scored by the model trained on all fit years.
    """
    fy = t["fiscal_year"].to_numpy()

    def s_fn(fit_years):
        fit = np.isin(fy, fit_years)
        s = fit_predict(fit)
        for y in fit_years:
            oof = fit_predict(fit & (fy != y))
            s = np.where(fy == y, oof, s)
        return s
    return s_fn


def gbm_fn(t: pd.DataFrame):
    X = t[RULE_VARS + FLAG_VARS].astype(float).to_numpy()

    def fit_predict(train):
        # drop inputs with no variation in the training rows (sales_growth_3y is empty before FY2018)
        keep = [j for j in range(X.shape[1]) if len(np.unique(X[train, j][~np.isnan(X[train, j])])) > 1]
        m = HistGradientBoostingRegressor(loss="absolute_error", max_iter=300, learning_rate=0.05,
                                          max_leaf_nodes=31, min_samples_leaf=50, random_state=0)
        m.fit(X[train][:, keep], _target(t, train)[train])
        return np.maximum(m.predict(X[:, keep]), FLOOR)
    return cross_fitted(t, fit_predict)


def linear_fn(t: pd.DataFrame):
    cols = [f"pct_{v}" for v in RULE_VARS]
    X = np.column_stack([np.nan_to_num(t[cols].to_numpy(dtype=float), nan=0.5) - 0.5,
                         t[FLAG_VARS].fillna(False).to_numpy(dtype=float), np.ones(len(t))])

    def fit_predict(train):
        y = np.log(np.maximum(_target(t, train), 1e-3))
        beta, *_ = np.linalg.lstsq(X[train], y[train], rcond=None)
        return np.maximum(np.exp(X @ beta), FLOOR)
    return cross_fitted(t, fit_predict)


def fixed_fn(s: np.ndarray):
    return lambda fit_years: s


def calibrated_methods(t: pd.DataFrame, multiple: str) -> dict:
    """name -> s_fn(fit_years) for every calibrated benchmark."""
    return {
        "constant": fixed_fn(np.ones(len(t))),
        "peer_iqr_scaled": fixed_fn(np.maximum(t["peer_iqr"].to_numpy(dtype=float), 0.05)),
        "linear_all": linear_fn(t),
        "gbm": gbm_fn(t),
        "hand_rule": fixed_fn(validate(HAND_RULES[multiple]).score(t)),
    }


def practice(t: pd.DataFrame) -> dict:
    """Scorecards for the uncalibrated practitioner ranges (no fitting, any years in t)."""
    return {
        "practice_iqr": grader.score_fixed(t, t["peer_q25"].to_numpy(), t["peer_q75"].to_numpy()),
        "practice_minmax": grader.score_fixed(t, t["peer_min"].to_numpy(), t["peer_max"].to_numpy()),
    }
