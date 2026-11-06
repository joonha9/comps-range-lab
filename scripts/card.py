"""Comps confidence card: the agents' shared findings as a hand-usable three-tier table.

Built after the pre-registered tests, from what the five frozen finalists have in common, with
absolute cut-offs taken from exploration years (FY2016-2019). So the card is a NEW rule:
its validation and holdout scores below are exploratory, not confirmatory.

  tier = number of warning flags: 0 = high confidence, 1 = medium, 2+ = low
  range = point estimate x exp(c +/- q_tier)       (q_tier: 80% conformal quantile within the tier)

Outputs
  - out-of-sample check: widths fitted on FY2016-2019, scored on FY2020-2023 and FY2024-2025
  - published widths for use today: fitted on all years FY2016-2025
Writes results/card/card.json and card.md.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rangelab import agents as ag  # noqa: E402
from rangelab import grader, vl  # noqa: E402
from rangelab.base import base_table  # noqa: E402
from rangelab.rules import validate  # noqa: E402

OUT = ROOT / "results/card"
FIT = vl.PROTOCOL.years("explore")
VAL = vl.PROTOCOL.years("validate")
HOLD = vl.PROTOCOL.years("holdout", allow_holdout=True)
TIERS = ["high", "medium", "low"]

# Flags: (label, function of the base table). Cut-offs are exploration-year values (see card.md).
FLAGS = {
    "EV/EBITDA": {
        "sales below $400M": lambda t: np.exp(t["log_sales"]) < 400,
        "net loss": lambda t: t["loss_making"].fillna(False).astype(bool),
        "net cash above 2x EBITDA": lambda t: t["net_debt_to_ebitda"] < -2,
        "EBITDA margin below 8%": lambda t: t["ebitda_margin"] < 0.08,
    },
    "EV/Sales": {
        "sales below $150M": lambda t: np.exp(t["log_sales"]) < 150,
        "negative EBITDA": lambda t: t["negative_ebitda"].fillna(False).astype(bool),
        "peer multiples span more than 30x": lambda t: t["peer_range"] > np.log(30),
        "fewer than 10 peers": lambda t: t["n_peers"] < 10,
    },
}


def tiers(t: pd.DataFrame, m: str) -> np.ndarray:
    n = sum(f(t).to_numpy(dtype=bool).astype(int) for f in FLAGS[m].values())
    return np.minimum(n, 2)


def fit_card(t: pd.DataFrame, tier: np.ndarray, fit: np.ndarray) -> tuple[float, np.ndarray]:
    e = t["e"].to_numpy()
    c = float(np.median(e[fit]))  # one global centre; one 80% conformal width per tier
    q = np.zeros(3)
    for k in range(3):
        r = np.abs(e[fit & (tier == k)] - c)
        n = len(r)
        q[k] = float(np.quantile(r, min(1.0, np.ceil((n + 1) * 0.8) / n), method="higher"))
    return c, q


def score_card(t, tier, c, q, years) -> dict:
    ev = t["fiscal_year"].isin(years).to_numpy()
    hw = q[tier[ev]]
    card = grader.score_fixed(t[ev], c - hw, c + hw)
    card["tier_coverage"] = {TIERS[k]: float((np.abs(t["e"].to_numpy()[ev] - c) <= hw)[tier[ev] == k].mean())
                             for k in range(3)}
    return card


def main() -> None:
    out = {"label": "built after the pre-registered tests; out-of-sample scores are exploratory",
           "valuationlab_commit": vl.vl_commit(), "multiples": {}}
    finals = {r: json.loads((ag.RUNS / r / "final.json").read_text())["finalists"] for r in ["a1", "a2", "a3", "a4", "a5"]}
    for m in ag.MULTIPLES:
        t = base_table(m, include_holdout=True)
        tier = tiers(t, m)
        fy = t["fiscal_year"].to_numpy()
        fit = np.isin(fy, FIT)
        c, q = fit_card(t, tier, fit)
        R = {"flags": list(FLAGS[m]), "centre": c, "factor_fit_2016_2019": {TIERS[k]: float(np.exp(q[k])) for k in range(3)},
             "tier_share_explore": {TIERS[k]: float((tier[fit] == k).mean()) for k in range(3)},
             "flag_share_explore": {k: float(f(t[fit]).mean()) for k, f in FLAGS[m].items()}, "oos": {}}
        for per, years in (("validate", VAL), ("holdout", HOLD)):
            cardsc = score_card(t, tier, c, q, years)
            const = grader.score(t, np.ones(len(t)), FIT, years)
            agents = [grader.score(t, validate(finals[r][m]["spec"]).score(t), FIT, years) for r in finals]
            R["oos"][per] = {"card": cardsc["interval_score"], "card_coverage": cardsc["coverage"],
                             "card_tier_coverage": cardsc["tier_coverage"],
                             "constant": const["interval_score"], "constant_coverage": const["coverage"],
                             "agents_mean": float(np.mean([a["interval_score"] for a in agents])),
                             "card_segments": {k: v["coverage"] for k, v in cardsc["segments"].items()},
                             "constant_segments": {k: v["coverage"] for k, v in const["segments"].items()}}
        # published widths: all years FY2016-2025
        allyrs = np.isin(fy, FIT + VAL + HOLD)
        c_all, q_all = fit_card(t, tier, allyrs)
        R["published"] = {"centre": c_all, "centre_factor": float(np.exp(c_all)),
                          "factor": {TIERS[k]: float(np.exp(q_all[k])) for k in range(3)},
                          "tier_share_all": {TIERS[k]: float((tier[allyrs] == k).mean()) for k in range(3)}}
        out["multiples"][m] = R
        o = R["oos"]
        print(f"{m}: published x/ {R['published']['factor']}  centre x{R['published']['centre_factor']:.3f}")
        for per in o:
            print(f"   {per}: card {o[per]['card']:.3f} (cov {o[per]['card_coverage']:.1%}, tiers "
                  f"{ {k: round(v, 2) for k, v in o[per]['card_tier_coverage'].items()} }) | agents {o[per]['agents_mean']:.3f} | "
                  f"constant {o[per]['constant']:.3f} (cov {o[per]['constant_coverage']:.1%})")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "card.json").write_text(json.dumps(out, indent=1))
    write_md(out)


def write_md(out: dict) -> None:
    L = ["# Comps confidence card", "",
         "Built from what the five frozen agent finalists share, after the pre-registered tests. Cut-offs come from "
         "exploration years. Out-of-sample scores are exploratory. Produced by `scripts/card.py`.", ""]
    for m, R in out["multiples"].items():
        p = R["published"]
        L += [f"## {m}", "", "Warning flags: " + "; ".join(R["flags"]) + ".", "",
              "| Confidence | Flags | Share of firms | 80% range (published, FY2016–2025) |", "|---|---|---|---|"]
        for k, lab in enumerate(TIERS):
            fl = ["0", "1", "2 or more"][k]
            f = p["factor"][lab]
            L.append(f"| {lab} | {fl} | {p['tier_share_all'][lab]:.0%} | point × {np.exp(p['centre']) / f:.2f} to × {np.exp(p['centre']) * f:.2f} (×/÷ {f:.2f}) |")
        L += ["", f"Point estimate = median peer multiple × the target's driver. The centre (× {p['centre_factor']:.2f}) "
              "corrects the average gap between market value and the peer median.", "",
              "Out-of-sample check (widths fitted on FY2016–2019):", "",
              "| Period | Card interval score | Card coverage | Coverage high / medium / low | Agent rules (mean of 5) | Constant band | Constant coverage |",
              "|---|---|---|---|---|---|---|"]
        for per, o in R["oos"].items():
            tc = o["card_tier_coverage"]
            L.append(f"| {per} | {o['card']:.3f} | {o['card_coverage']:.1%} | {tc['high']:.0%} / {tc['medium']:.0%} / {tc['low']:.0%} | "
                     f"{o['agents_mean']:.3f} | {o['constant']:.3f} | {o['constant_coverage']:.1%} |")
        L.append("")
    (OUT / "card.md").write_text("\n".join(L))


if __name__ == "__main__":
    main()
