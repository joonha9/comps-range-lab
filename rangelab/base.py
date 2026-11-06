"""Base table: one row per target firm-year with the comps point estimate and the inputs rules may use.

The point estimate comes from one fixed peer method per multiple (POINT_METHODS). Each row holds
  e            ln(actual EV / point estimate): positive means the market values the firm above comps
  peer_q25/q75 peer multiple quartiles relative to the aggregated peer multiple, in logs
  rule inputs  the target's accounting features plus peer statistics (never the target's own value)
and, for every rule input, its within-year percentile rank (0-1) among that year's targets.

Rows are cached under data/ (gitignored: derived from licensed FactSet data).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from . import vl

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data/cache"

# Practitioner default: same 2-digit SIC sector, the 10 firms closest in size and EBITDA margin.
POINT_METHODS = {
    m: {"name": f"Size and margin peers ({m})", "multiple": m,
        "filters": [{"same": "industry_l2"}], "rank": {"log_sales": 0.5, "ebitda_margin": 0.5},
        "k": 10, "agg": "median", "min_peers": 3}
    for m in ("EV/EBITDA", "EV/Sales")
}

PEER_VARS = ["peer_iqr", "peer_range", "n_peers"]
FLAG_VARS = ["loss_making", "negative_ebitda", "no_history"]
RULE_VARS = list(vl.FEATURES) + PEER_VARS  # continuous inputs (percentile ranks available)


def _build(panel: pd.DataFrame, multiple: str, years: list[int]) -> pd.DataFrame:
    value_col, driver_col = vl.MULTIPLES[multiple]
    recipe = vl.validate(POINT_METHODS[multiple])
    est = vl.apply_recipe(panel, recipe, years, keep_peers=True)
    est = est[est["n_peers"] > 0]
    data = panel[panel["fiscal_year"].isin(years)]
    elig = data[(data[value_col] > 0) & (data[driver_col] > 0)]
    mult = {(fy, i): v / d for fy, i, v, d in
            zip(elig["fiscal_year"], elig["id"], elig[value_col], elig[driver_col])}
    rows = []
    for r in est.itertuples(index=False):
        pm = np.array([mult[(r.fiscal_year, p)] for p in r.peers])
        q25, q75 = np.percentile(pm, [25, 75])
        rows.append({"id": r.id, "fiscal_year": int(r.fiscal_year), "actual": r.actual,
                     "estimate": r.estimate, "e": np.log(r.actual / r.estimate),
                     "peer_q25": np.log(q25 / r.peer_multiple), "peer_q75": np.log(q75 / r.peer_multiple),
                     "peer_min": np.log(pm.min() / r.peer_multiple), "peer_max": np.log(pm.max() / r.peer_multiple),
                     "peer_iqr": np.log(q75 / q25), "peer_range": np.log(pm.max() / pm.min()),
                     "n_peers": len(pm)})
    t = pd.DataFrame(rows)
    feats = data[["id", "fiscal_year", "net_income", "ebitda"] + list(vl.FEATURES)]
    t = t.merge(feats, on=["id", "fiscal_year"], how="left")
    t["loss_making"] = t["net_income"] < 0
    t["negative_ebitda"] = t["ebitda"] <= 0
    t["no_history"] = t["sales_growth_1y"].isna()  # no prior-year sales: new listing or new to the data
    t = t.drop(columns=["net_income", "ebitda"])
    for v in RULE_VARS:
        t[f"pct_{v}"] = t.groupby("fiscal_year")[v].rank(pct=True)
    return t.sort_values(["fiscal_year", "id"]).reset_index(drop=True)


def base_table(multiple: str, include_holdout: bool = False) -> pd.DataFrame:
    """Base table for FY2016-2023 (plus FY2024-2025 only when include_holdout is True)."""
    years = vl.PROTOCOL.years("explore") + vl.PROTOCOL.years("validate")
    if include_holdout:
        years += vl.PROTOCOL.years("holdout", allow_holdout=True)
    panel = vl.panel_with_holdout() if include_holdout else vl.panel()
    key = json.dumps([multiple, years, POINT_METHODS[multiple], len(panel), vl.vl_commit()])
    h = hashlib.sha1(key.encode()).hexdigest()[:10]
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / f"base_{multiple.replace('/', '_')}_{h}.pkl"
    if f.exists():
        return pd.read_pickle(f)
    t = _build(panel, multiple, years)
    t.to_pickle(f)
    return t
