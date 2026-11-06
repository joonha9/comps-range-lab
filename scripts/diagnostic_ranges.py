"""Diagnostic 0: how often do practitioner comps ranges contain the market value?

Uses exploration years only (FY2016-2019). For each target firm-year and each peer method,
the peer multiples are applied to the target's driver, and we check whether the target's actual
enterprise value falls inside
  - the interquartile range (25th-75th percentile) of peer multiples   (nominal 50%)
  - the full peer range (min-max)                                      (no stated level)
We also report where the actual multiple falls in the peer distribution: if peers were drawn from
the same distribution as the target, the target's percentile would be uniform (25% per quartile).

Writes results/diagnostic/ranges.json and results/diagnostic/ranges.md.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rangelab import vl  # noqa: E402

OUT = ROOT / "results/diagnostic"

# Peer methods: the ValuationLab industry-median baseline, a practitioner default, and the
# ValuationLab hand-written recipe for each multiple. No agent recipe is used here.
METHODS = {
    "EV/EBITDA": {
        "industry_sic3": "industry_median",
        "size_margin_k10": {
            "name": "Size and margin peers", "multiple": "EV/EBITDA",
            "filters": [{"same": "industry_l2"}], "rank": {"log_sales": 0.5, "ebitda_margin": 0.5},
            "k": 10, "agg": "median", "min_peers": 3},
        "growth_roic_k8": {
            "name": "Growth and ROIC peers", "multiple": "EV/EBITDA",
            "filters": [{"same": "industry_l3"}], "rank": {"sales_growth_3y": 0.5, "roic": 0.5},
            "k": 8, "agg": "median", "min_peers": 3, "fallback": [[{"same": "industry_l2"}]]},
    },
    "EV/Sales": {
        "industry_sic3": "industry_median",
        "size_margin_k10": {
            "name": "Size and margin peers (sales)", "multiple": "EV/Sales",
            "filters": [{"same": "industry_l2"}], "rank": {"log_sales": 0.5, "ebitda_margin": 0.5},
            "k": 10, "agg": "median", "min_peers": 3},
        "margin_growth_k8": {
            "name": "Margin-matched sales peers", "multiple": "EV/Sales",
            "filters": [{"same": "industry_l3"}], "rank": {"ebitda_margin": 0.6, "sales_growth_3y": 0.4},
            "k": 8, "agg": "median", "min_peers": 3, "fallback": [[{"same": "industry_l2"}]]},
    },
}


def recipe_for(multiple: str, spec):
    if spec == "industry_median":
        return vl.baselines_for(multiple)["industry_median"]
    return vl.validate(spec)


def peer_table(panel: pd.DataFrame, multiple: str, recipe, years: list[int]) -> pd.DataFrame:
    value_col, driver_col = vl.MULTIPLES[multiple]
    est = vl.apply_recipe(panel, recipe, years, keep_peers=True)
    est = est[est["n_peers"] > 0].copy()
    data = panel[panel["fiscal_year"].isin(years)]
    data = data[(data[value_col] > 0) & (data[driver_col] > 0)]
    mult = {(fy, i): v / d for fy, i, v, d in
            zip(data["fiscal_year"], data["id"], data[value_col], data[driver_col])}
    rows = []
    for r in est.itertuples(index=False):
        pm = np.array([mult[(r.fiscal_year, p)] for p in r.peers])
        actual_m = mult[(r.fiscal_year, r.id)]
        q25, q75 = np.percentile(pm, [25, 75])
        rows.append({
            "id": r.id, "fiscal_year": r.fiscal_year, "n_peers": len(pm),
            "point_error": np.log(r.estimate / r.actual),
            "in_iqr": q25 <= actual_m <= q75,
            "in_minmax": pm.min() <= actual_m <= pm.max(),
            "iqr_width": np.log(q75 / q25),
            "minmax_width": np.log(pm.max() / pm.min()),
            "pctile": (pm < actual_m).mean() + 0.5 * (pm == actual_m).mean(),
        })
    return pd.DataFrame(rows)


def segments(panel: pd.DataFrame, years: list[int]) -> pd.DataFrame:
    """Firm characteristics practitioners would recognise; cut-offs use exploration-year quintiles."""
    d = panel[panel["fiscal_year"].isin(years)][["id", "fiscal_year", "net_income", "log_sales",
                                                 "sales_growth_1y", "rnd_intensity"]].copy()
    q = lambda c, p: d.groupby("fiscal_year")[c].transform(lambda s: s.quantile(p))  # noqa: E731
    d["loss_making"] = d["net_income"] < 0
    d["small_size"] = d["log_sales"] <= q("log_sales", 0.2)
    d["high_growth"] = d["sales_growth_1y"] >= q("sales_growth_1y", 0.8)
    d["high_rnd"] = d["rnd_intensity"] >= q("rnd_intensity", 0.8)
    return d[["id", "fiscal_year", "loss_making", "small_size", "high_growth", "high_rnd"]]


def summarize(t: pd.DataFrame) -> dict:
    return {
        "n": int(len(t)),
        "iqr_coverage": float(t["in_iqr"].mean()),
        "minmax_coverage": float(t["in_minmax"].mean()),
        "median_iqr_width_pct": float(np.expm1(t["iqr_width"].median())),
        "median_abs_point_error": float(t["point_error"].abs().median()),
        # +/- band around the point estimate that would have contained 50% / 80% of actual values
        # factor f such that [point / f, point * f] would have contained 50% / 80% of actual values
        "factor_for_50pct": float(np.exp(t["point_error"].abs().quantile(0.5))),
        "factor_for_80pct": float(np.exp(t["point_error"].abs().quantile(0.8))),
        "pctile_quartile_shares": [float(x) for x in
                                   np.histogram(t["pctile"], bins=[0, .25, .5, .75, 1.0001])[0] / len(t)],
    }


def main() -> None:
    panel = vl.panel()
    years = vl.PROTOCOL.years("explore")
    seg = segments(panel, years)
    out = {"years": years, "valuationlab_commit": vl.vl_commit(), "results": {}}
    for multiple, methods in METHODS.items():
        for mname, spec in methods.items():
            t = peer_table(panel, multiple, recipe_for(multiple, spec), years)
            t = t.merge(seg, on=["id", "fiscal_year"], how="left")
            res = {"all": summarize(t), "by_year": {}, "segments": {}}
            for fy, g in t.groupby("fiscal_year"):
                res["by_year"][int(fy)] = {"n": int(len(g)), "iqr_coverage": float(g["in_iqr"].mean())}
            for s in ("loss_making", "small_size", "high_growth", "high_rnd"):
                g = t[t[s] == True]  # noqa: E712
                res["segments"][s] = {"n": int(len(g)), "iqr_coverage": float(g["in_iqr"].mean()),
                                      "median_abs_point_error": float(g["point_error"].abs().median())}
            out["results"][f"{multiple} · {mname}"] = res
            a = res["all"]
            print(f"{multiple:9s} {mname:17s} n={a['n']:5d}  IQR cover={a['iqr_coverage']:.1%}  "
                  f"min-max cover={a['minmax_coverage']:.1%}  IQR width={a['median_iqr_width_pct']:.0%}  "
                  f"80% factor=x/{a['factor_for_80pct']:.2f}  quartiles={[round(x, 2) for x in a['pctile_quartile_shares']]}")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "ranges.json").write_text(json.dumps(out, indent=1))
    write_md(out)


def write_md(out: dict) -> None:
    L = ["# Diagnostic 0: do practitioner comps ranges contain the market value?", "",
         f"Exploration years FY{out['years'][0]}–{out['years'][-1]} only. ValuationLab commit "
         f"`{out['valuationlab_commit']}`. Produced by `scripts/diagnostic_ranges.py`.", "",
         "| Multiple · peer method | n | Inside peer IQR (nominal 50%) | Inside peer min–max | "
         "Median IQR width (q75/q25 − 1) | ×/÷ factor needed for 80% | Actual's quartile in peer distribution (25% each if calibrated) |",
         "|---|---|---|---|---|---|---|"]
    for k, r in out["results"].items():
        a = r["all"]
        qs = " / ".join(f"{x:.0%}" for x in a["pctile_quartile_shares"])
        L.append(f"| {k} | {a['n']:,} | {a['iqr_coverage']:.1%} | {a['minmax_coverage']:.1%} | "
                 f"{a['median_iqr_width_pct']:.0%} | ×/÷ {a['factor_for_80pct']:.2f} | {qs} |")
    L += ["", "## IQR coverage by firm type", "",
          "| Multiple · peer method | All | Loss-making | Smallest 20% | Fastest-growing 20% | Highest R&D 20% |",
          "|---|---|---|---|---|---|"]
    for k, r in out["results"].items():
        s = r["segments"]
        L.append(f"| {k} | {r['all']['iqr_coverage']:.1%} | " + " | ".join(
            f"{s[x]['iqr_coverage']:.1%} (n={s[x]['n']:,})"
            for x in ("loss_making", "small_size", "high_growth", "high_rnd")) + " |")
    L += ["", "Factor for 80%: the f such that [point / f, point × f] around the point estimate "
          "(aggregated peer multiple × driver) would have contained 80% of actual enterprise values."]
    (OUT / "ranges.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
