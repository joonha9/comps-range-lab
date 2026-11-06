"""Build the Comps Range Lab site (index.html at the repository root) from the results.

    python3 scripts/build_site.py

Every number on the site comes from results/ (or is computed here from the frozen rules and the
FactSet base tables); nothing is typed by hand. The data are written to site/site_data.json and
injected into site/template.html. GitHub Pages serves the root index.html.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rangelab import agents as ag  # noqa: E402
from rangelab import grader, vl  # noqa: E402
from rangelab.base import FLAG_VARS, base_table  # noqa: E402
from rangelab.rules import validate  # noqa: E402

RUNS = ["a1", "a2", "a3", "a4", "a5"]
MULT = list(ag.MULTIPLES)
FIT = vl.PROTOCOL.years("explore")
VAL = vl.PROTOCOL.years("validate")
HOLD = vl.PROTOCOL.years("holdout", allow_holdout=True)


def r(x, n=4):
    return None if x is None or not np.isfinite(float(x)) else round(float(x), n)


def load(p):
    return json.loads((ROOT / p).read_text())


def size_split(finals) -> dict:
    """Coverage and median width for the largest and smallest 20% of firms: constant band vs agent rules."""
    out = {}
    for m in MULT:
        t = base_table(m, include_holdout=True)
        fy, e = t["fiscal_year"].to_numpy(), t["e"].to_numpy()
        fit = np.isin(fy, FIT)
        groups = {"largest": (t["pct_log_sales"] >= 0.8).to_numpy(), "smallest": (t["pct_log_sales"] <= 0.2).to_numpy()}
        scores = {"constant": [np.ones(len(t))], "agents": [validate(finals[x][m]["spec"]).score(t) for x in RUNS]}
        res = {}
        for per, years in (("validate", VAL), ("holdout", HOLD)):
            ev = np.isin(fy, years)
            res[per] = {}
            for name, ss in scores.items():
                g = {}
                for gname, mask in groups.items():
                    cov, fac = [], []
                    for s in ss:
                        c, q = grader.calibrate(e[fit], s[fit])
                        hw = q * s
                        sel = ev & mask
                        cov.append(np.mean(np.abs(e[sel] - c) <= hw[sel]))
                        fac.append(np.exp(np.median(hw[sel])))
                    g[gname] = {"coverage": r(np.mean(cov), 3), "factor": r(np.mean(fac), 2)}
                res[per][name] = g
        out[m] = res
    return out


def main() -> None:
    diag = load("results/diagnostic/ranges.json")
    explore = load("results/baselines/explore.json")["multiples"]
    rep = {"validate": load("results/validate/report.json"), "holdout": load("results/holdout/report.json")}
    rob = load("results/robustness/peers.json")["multiples"]
    card = load("results/card/card.json")["multiples"]
    finals = {x: load(f"results/agent_runs/{x}/final.json") for x in RUNS}
    ffin = {x: f["finalists"] for x, f in finals.items()}

    methods = ["practice_iqr", "practice_minmax", "constant", "agents", "linear_all", "gbm"]
    scores, tests = {}, {}
    for m in MULT:
        scores[m], tests[m] = {}, {}
        for per in ("validate", "holdout"):
            R = rep[per]["multiples"][m]
            d = {}
            for k in methods:
                if k == "agents":
                    vals = list(R["finalists"].values())
                    d[k] = {"is": r(np.mean([v["interval_score"] for v in vals]), 3),
                            "coverage": r(np.mean([v["coverage"] for v in vals]), 3),
                            "factor": r(np.mean([v["median_factor"] for v in vals]), 2),
                            "runs": [r(v["interval_score"], 3) for v in vals]}
                else:
                    b = R["benchmarks"][k]
                    d[k] = {"is": r(b["interval_score"], 3), "coverage": r(b["coverage"], 3), "factor": r(b["median_factor"], 2)}
            scores[m][per] = d
            T = R["tests"]
            tests[m][per] = {"T1_runs": T["T1_vs_constant"]["runs_below"], "T1": T["T1_vs_constant"]["pass"],
                             "T2_p": r(T["T2_vs_random"]["p_holm"], 4), "T2": T["T2_vs_random"]["pass"],
                             "T3": T["T3_vs_linear_all"]["pass"], "G": r(T["T4_share_of_gbm_gain"]["G"], 2),
                             "T4": T["T4_share_of_gbm_gain"]["close_to_black_box"],
                             "random_median": r(T["T2_vs_random"]["random_median_of_means"], 3)}
        scores[m]["explore"] = {k: {"is": r(explore[m][k]["interval_score"], 3), "coverage": r(explore[m][k]["coverage"], 3)}
                                for k in ("practice_iqr", "practice_minmax", "constant", "linear_all", "gbm")}

    # what the five finalists use
    consensus = {}
    for m in MULT:
        cnt = Counter()
        for x in RUNS:
            sp = ffin[x][m]["spec"]
            used = set(sp["terms"]) | {cl["var"] for c in sp["conditions"] for cl in c["if"]}
            if sp["base"] != "constant":
                used.add(sp["base"])
            cnt.update(used)
        consensus[m] = sorted(([k, v] for k, v in cnt.items()), key=lambda kv: (-kv[1], kv[0]))

    funnel = {k: sum(f["funnel"][k] for f in finals.values()) for k in ("proposed", "graded", "rejected", "invalid", "duplicate")}
    trajectories = {}
    for x in RUNS:
        arch = ag.Run(x).archive()
        trajectories[x] = {}
        for m in MULT:
            best, tr = np.inf, []
            for g in range(1, 6):
                s = [a["explore"]["interval_score"] for a in arch if a["status"] == "graded" and a["multiple"] == m and a["generation"] == g]
                best = min([best] + s)
                tr.append(r(best, 3) if np.isfinite(best) else None)
            trajectories[x][m] = tr

    robustness = {m: [{"method": k, **{p: {"constant": r(v["recalibrated"][p]["constant"], 3), "agents": r(v["recalibrated"][p]["agents_mean"], 3),
                                           "gbm": r(v["recalibrated"][p]["gbm"], 3), "below": v["recalibrated"][p]["agents_runs_below_constant"],
                                           "transferred_cov": r(v["transferred"][p]["agents_coverage"], 3)} for p in ("validate", "holdout")}}
                      for k, v in rob[m].items()] for m in MULT}

    cardd = {m: {"flags": c["flags"], "centre": r(c["published"]["centre_factor"], 3),
                 "factor": {k: r(v, 3) for k, v in c["published"]["factor"].items()},
                 "share": {k: r(v, 3) for k, v in c["published"]["tier_share_all"].items()},
                 "oos": {p: {"is": r(o["card"], 3), "coverage": r(o["card_coverage"], 3), "agents": r(o["agents_mean"], 3),
                             "constant": r(o["constant"], 3), "tiers": {k: r(v, 3) for k, v in o["card_tier_coverage"].items()}}
                         for p, o in c["oos"].items()}} for m, c in card.items()}

    n_firm_years = {m: int(len(base_table(m, include_holdout=True))) for m in MULT}
    data = {
        "counts": {"firm_years": n_firm_years, "runs": len(RUNS), "funnel": funnel,
                   "random_rules": sum(len(ag.Run(x).archive("random")) for x in RUNS)},
        "diagnostic": {k: {"iqr_coverage": r(v["all"]["iqr_coverage"], 3), "minmax_coverage": r(v["all"]["minmax_coverage"], 3),
                           "quartiles": [r(q, 3) for q in v["all"]["pctile_quartile_shares"]],
                           "iqr_width": r(v["all"]["median_iqr_width_pct"], 3)} for k, v in diag["results"].items()},
        "scores": scores, "tests": tests, "consensus": consensus,
        "finalists": {x: {m: {"compact": ffin[x][m]["compact"], "mechanism": ffin[x][m]["mechanism"],
                              "explore": r(ffin[x][m]["explore"]["interval_score"], 3),
                              "validate": r(rep["validate"]["multiples"][m]["finalists"][x]["interval_score"], 3),
                              "holdout": r(rep["holdout"]["multiples"][m]["finalists"][x]["interval_score"], 3)} for m in MULT} for x in RUNS},
        "trajectories": trajectories, "size_split": size_split(ffin), "robustness": robustness, "card": cardd,
        "flags_vars": FLAG_VARS, "commits": {"valuationlab": vl.vl_commit()},
    }
    (ROOT / "site" / "site_data.json").write_text(json.dumps(data, indent=1, ensure_ascii=False))
    tpl = (ROOT / "site" / "template.html").read_text()
    out = tpl.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    (ROOT / "index.html").write_text(out)
    print(f"wrote index.html ({len(out) // 1024} KB) and site/site_data.json")


if __name__ == "__main__":
    main()
