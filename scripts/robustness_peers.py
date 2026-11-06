"""Robustness (exploratory): do the frozen agent rules still work when practitioners pick peers differently?

Validation and holdout years were each used once for the pre-registered tests; this check reuses them and
is labelled exploratory. Nothing here selects or changes a rule.

For each alternative peer method (point estimate) and multiple:
  A. Re-calibrated: rules and benchmarks calibrated on FY2016-2019 errors of THAT peer method, scored on
     FY2020-2023 and FY2024-2025. Question: does the rule still beat the constant band?
  B. Transferred: centre and scale calibrated on the PRIMARY peer method (FY2016-2019), applied unchanged to
     the alternative method's errors. Question: can a practitioner reuse one published width table whatever
     peers they pick?

Writes results/robustness/peers.json and peers.md.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rangelab import agents as ag  # noqa: E402
from rangelab import baselines, grader, vl  # noqa: E402
from rangelab.base import POINT_METHODS, base_table  # noqa: E402
from rangelab.rules import validate  # noqa: E402

OUT = ROOT / "results/robustness"
FIT = vl.PROTOCOL.years("explore")
PERIODS = {"validate": vl.PROTOCOL.years("validate"), "holdout": vl.PROTOCOL.years("holdout", allow_holdout=True)}
RUNS = ["a1", "a2", "a3", "a4", "a5"]


def alternatives(m: str) -> dict:
    return {
        "primary: SIC2, 10 nearest on size+margin": POINT_METHODS[m],
        "SIC3 industry, all peers": {"name": "sic3 all", "multiple": m, "filters": [{"same": "industry_l3"}],
                                     "k": "all", "agg": "median", "min_peers": 3,
                                     "fallback": [[{"same": "industry_l2"}]]},
        "SIC4 industry, all peers": {"name": "sic4 all", "multiple": m, "filters": [{"same": "industry_l4"}],
                                     "k": "all", "agg": "median", "min_peers": 3,
                                     "fallback": [[{"same": "industry_l3"}], [{"same": "industry_l2"}]]},
        "SIC3, 5 nearest on size+margin": {"name": "sic3 k5", "multiple": m, "filters": [{"same": "industry_l3"}],
                                           "rank": {"log_sales": 0.5, "ebitda_margin": 0.5}, "k": 5,
                                           "agg": "median", "min_peers": 3, "fallback": [[{"same": "industry_l2"}]]},
        "SIC3, 8 nearest on growth+ROIC": {"name": "sic3 growth roic k8", "multiple": m,
                                           "filters": [{"same": "industry_l3"}],
                                           "rank": {"sales_growth_1y": 0.5, "roic": 0.5}, "k": 8,
                                           "agg": "median", "min_peers": 3, "fallback": [[{"same": "industry_l2"}]]},
    }


def transferred(t, s, c, q, years) -> dict:
    ev = t["fiscal_year"].isin(years).to_numpy()
    te = t[ev]
    lo, hi = c - q * s[ev], c + q * s[ev]
    return grader.score_fixed(te, lo, hi)


def main() -> None:
    finals = {r: json.loads((ag.RUNS / r / "final.json").read_text())["finalists"] for r in RUNS}
    out = {"label": "exploratory robustness; validation and holdout were already used once",
           "valuationlab_commit": vl.vl_commit(), "multiples": {}}
    for m in ag.MULTIPLES:
        prim = base_table(m, include_holdout=True)
        prim_fit = prim[prim["fiscal_year"].isin(FIT)]
        rules = {r: validate(finals[r][m]["spec"]) for r in RUNS}
        # primary-method calibration (centre, scale) for each rule and the constant band
        cal = {"constant": grader.calibrate(prim_fit["e"].to_numpy(), np.ones(len(prim_fit)))}
        for r, rule in rules.items():
            cal[r] = grader.calibrate(prim_fit["e"].to_numpy(), rule.score(prim_fit))
        res = {}
        for label, spec in alternatives(m).items():
            t = base_table(m, include_holdout=True, point=spec)
            row = {"n_explore": int(t["fiscal_year"].isin(FIT).sum()), "recalibrated": {}, "transferred": {}}
            scores = {"constant": np.ones(len(t)), **{r: rule.score(t) for r, rule in rules.items()}}
            for per, years in PERIODS.items():
                rc = {k: grader.score(t, s, FIT, years) for k, s in scores.items()}
                rc_gbm = grader.score(t, baselines.gbm_fn(t)(FIT), FIT, years)
                agents = [rc[r] for r in RUNS]
                row["recalibrated"][per] = {
                    "constant": rc["constant"]["interval_score"],
                    "agents_mean": float(np.mean([a["interval_score"] for a in agents])),
                    "agents_runs_below_constant": int(sum(a["interval_score"] < rc["constant"]["interval_score"]
                                                          for a in agents)),
                    "gbm": rc_gbm["interval_score"],
                    "point_median_abs_error": float(np.median(np.abs(t.loc[t["fiscal_year"].isin(years), "e"]))),
                }
                tr = {k: transferred(t, s, *cal[k], years) for k, s in scores.items()}
                row["transferred"][per] = {
                    "constant_coverage": tr["constant"]["coverage"],
                    "agents_coverage": float(np.mean([tr[r]["coverage"] for r in RUNS])),
                    "constant_is": tr["constant"]["interval_score"],
                    "agents_is": float(np.mean([tr[r]["interval_score"] for r in RUNS])),
                }
            res[label] = row
            v, h = row["recalibrated"]["validate"], row["recalibrated"]["holdout"]
            tv, th = row["transferred"]["validate"], row["transferred"]["holdout"]
            print(f"{m:9s} {label:42s} recal const/agents/gbm val {v['constant']:.3f}/{v['agents_mean']:.3f}/{v['gbm']:.3f} "
                  f"({v['agents_runs_below_constant']}/5) hold {h['constant']:.3f}/{h['agents_mean']:.3f}/{h['gbm']:.3f} "
                  f"({h['agents_runs_below_constant']}/5) | transferred coverage val {tv['agents_coverage']:.0%} hold {th['agents_coverage']:.0%}")
        out["multiples"][m] = res
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "peers.json").write_text(json.dumps(out, indent=1))
    L = ["# Robustness: other ways of picking peers (exploratory)", "",
         "Frozen agent rules, unchanged. Validation (FY2020–2023) and holdout (FY2024–2025) were already used once "
         "for the pre-registered tests, so this check is exploratory. Produced by `scripts/robustness_peers.py`.", "",
         "**A. Re-calibrated** on FY2016–2019 errors of each peer method. Interval score, lower is better; "
         "(k/5) = agent runs below the constant band.", "",
         "| Multiple | Peer method | Point error (median abs, val) | Constant val | Agents val | GBM val | Constant hold | Agents hold | GBM hold |",
         "|---|---|---|---|---|---|---|---|---|"]
    for m, res in out["multiples"].items():
        for label, r in res.items():
            v, h = r["recalibrated"]["validate"], r["recalibrated"]["holdout"]
            L.append(f"| {m} | {label} | {v['point_median_abs_error']:.3f} | {v['constant']:.3f} | "
                     f"{v['agents_mean']:.3f} ({v['agents_runs_below_constant']}/5) | {v['gbm']:.3f} | {h['constant']:.3f} | "
                     f"{h['agents_mean']:.3f} ({h['agents_runs_below_constant']}/5) | {h['gbm']:.3f} |")
    L += ["", "**B. Transferred:** widths calibrated on the primary peer method, applied unchanged. Target coverage 80%.", "",
          "| Multiple | Peer method | Constant coverage val | Agents coverage val | Constant coverage hold | Agents coverage hold |",
          "|---|---|---|---|---|---|"]
    for m, res in out["multiples"].items():
        for label, r in res.items():
            tv, th = r["transferred"]["validate"], r["transferred"]["holdout"]
            L.append(f"| {m} | {label} | {tv['constant_coverage']:.1%} | {tv['agents_coverage']:.1%} | "
                     f"{th['constant_coverage']:.1%} | {th['agents_coverage']:.1%} |")
    (OUT / "peers.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
