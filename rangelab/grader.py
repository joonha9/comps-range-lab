"""Deterministic grader: turn uncertainty scores into 80% ranges and score them.

Calibration (split conformal, in logs). On the fit years:
  c = median of e                      (centre: corrects the average gap between market and comps)
  q = conformal 80% quantile of |e - c| / s
Range for a scored firm-year:  ln(estimate) + c +/- q * s, i.e. [estimate * e^(c - qs), estimate * e^(c + qs)].
Every method gets the same treatment, so methods differ only in how they spread width across firms.

Score (lower is better): the interval score of Gneiting & Raftery (2007) at alpha = 0.2, in logs,
  IS = width + (2 / alpha) * distance outside the range,
averaged within each year, then across years. Also reported: coverage, mean width, the x/÷ factor
of the median range, and coverage by firm type.

Exploration score: leave-one-year-out over FY2016-2019 (fit on three years, score the fourth).
Validation score: fit on FY2016-2019 once, score FY2020-2023.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

ALPHA = 0.2
SEGMENTS = {
    "loss_making": lambda t: t["loss_making"].fillna(False).astype(bool),
    "smallest_20pct": lambda t: t["pct_log_sales"] <= 0.2,
    "fastest_growing_20pct": lambda t: t["pct_sales_growth_1y"] >= 0.8,
    "highest_rnd_20pct": lambda t: t["pct_rnd_intensity"] >= 0.8,
    "fallback_or_few_peers": lambda t: t["n_peers"] < 10,
}


def calibrate(e: np.ndarray, s: np.ndarray, alpha: float = ALPHA) -> tuple[float, float]:
    c = float(np.median(e))
    r = np.abs(e - c) / s
    n = len(r)
    level = min(1.0, np.ceil((n + 1) * (1 - alpha)) / n)
    return c, float(np.quantile(r, level, method="higher"))


def interval_score(e: np.ndarray, lo: np.ndarray, hi: np.ndarray, alpha: float = ALPHA) -> np.ndarray:
    return (hi - lo) + (2 / alpha) * (np.maximum(lo - e, 0) + np.maximum(e - hi, 0))


def _cards(t: pd.DataFrame, lo: np.ndarray, hi: np.ndarray) -> dict:
    e = t["e"].to_numpy()
    d = pd.DataFrame({"fy": t["fiscal_year"].to_numpy(), "is": interval_score(e, lo, hi),
                      "cov": (e >= lo) & (e <= hi), "w": hi - lo})
    yearly = d.groupby("fy").agg(**{"is": ("is", "mean"), "cov": ("cov", "mean"), "w": ("w", "mean")})
    seg = {}
    for k, f in SEGMENTS.items():
        m = f(t).to_numpy(dtype=bool)
        seg[k] = {"n": int(m.sum()), "coverage": float(d["cov"][m].mean()) if m.any() else None}
    return {
        "interval_score": float(yearly["is"].mean()),
        "coverage": float(yearly["cov"].mean()),
        "mean_width": float(yearly["w"].mean()),
        "median_factor": float(np.exp(np.median(hi - lo) / 2)),
        "by_year": {int(y): {"interval_score": float(r["is"]), "coverage": float(r["cov"])}
                    for y, r in yearly.iterrows()},
        "segments": seg,
        "n": int(len(t)),
    }


def score_fixed(t: pd.DataFrame, lo: np.ndarray, hi: np.ndarray) -> dict:
    """Score ranges that need no calibration (e.g. the raw peer interquartile range)."""
    return _cards(t, lo, hi)


def score(t: pd.DataFrame, s: np.ndarray, fit_years: list[int], eval_years: list[int]) -> dict:
    """Calibrate scores s on fit_years and evaluate on eval_years (both subsets of t)."""
    s = np.asarray(s, dtype=float)
    if not np.all(np.isfinite(s)) or np.any(s <= 0):
        raise ValueError("uncertainty scores must be finite and positive")
    fy = t["fiscal_year"].to_numpy()
    fit, ev = np.isin(fy, fit_years), np.isin(fy, eval_years)
    c, q = calibrate(t["e"].to_numpy()[fit], s[fit])
    te = t[ev]
    centre = c
    lo, hi = centre - q * s[ev], centre + q * s[ev]
    card = _cards(te, lo, hi)
    card.update(centre=c, q=q)
    return card


def score_loyo(t: pd.DataFrame, s_fn, years: list[int]) -> dict:
    """Leave-one-year-out over `years`. s_fn(fit_years) returns scores for all rows of t, so
    learned methods can refit without the held-out year; a fixed rule ignores its argument."""
    per = []
    for y in years:
        fit = [x for x in years if x != y]
        per.append(score(t, s_fn(fit), fit, [y]))
    agg = {k: float(np.mean([p[k] for p in per])) for k in ("interval_score", "coverage", "mean_width")}
    agg["median_factor"] = float(np.mean([p["median_factor"] for p in per]))
    agg["by_year"] = {y: p["by_year"][y] for y, p in zip(years, per)}
    agg["segments"] = {k: {"n": sum(p["segments"][k]["n"] for p in per),
                           "coverage": float(np.average([p["segments"][k]["coverage"] or 0 for p in per],
                                                        weights=[p["segments"][k]["n"] for p in per]))
                           if sum(p["segments"][k]["n"] for p in per) else None}
                       for k in SEGMENTS}
    agg["n"] = int(sum(p["n"] for p in per))
    return agg
