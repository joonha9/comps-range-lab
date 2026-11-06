"""Score frozen finalists and benchmarks once on validation (or, later, holdout) years: tests T1-T4.

    python3 scripts/evaluate.py --period validate --runs a1 a2 a3 a4 a5
    python3 scripts/evaluate.py --period holdout  --runs a1 a2 a3 a4 a5 --open-holdout

Everything is fitted and calibrated on FY2016-2019 (docs/protocol.md). Writes
results/<period>/report.json and REPORT.md.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rangelab import agents as ag  # noqa: E402
from rangelab import baselines, grader, vl  # noqa: E402
from rangelab.base import base_table  # noqa: E402
from rangelab.rules import validate  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--period", choices=["validate", "holdout"], required=True)
ap.add_argument("--runs", nargs="+", required=True)
ap.add_argument("--open-holdout", action="store_true")
ap.add_argument("--sims", type=int, default=20000)
a = ap.parse_args()
if a.period == "holdout" and not a.open_holdout:
    sys.exit("the holdout is sealed: pass --open-holdout only for the single evaluation in docs/protocol.md")

FIT = vl.PROTOCOL.years("explore")
EVAL = vl.PROTOCOL.years(a.period, allow_holdout=a.open_holdout)
VAL = vl.PROTOCOL.years("validate")
OUT = ROOT / "results" / a.period
runs = [ag.Run(n) for n in a.runs]
finals = [json.loads((r.dir / "final.json").read_text()) for r in runs]
rng = np.random.default_rng(20261106)


def mad80(card: dict) -> float:
    cov = [v["coverage"] for v in card["segments"].values() if v["coverage"] is not None]
    return float(np.mean(np.abs(np.array(cov) - 0.8)))


def rolling(t, s_fn) -> dict:
    """Secondary: calibrate (and refit) each evaluation year on all earlier years."""
    per = []
    for y in EVAL:
        fit = [x for x in sorted(set(t["fiscal_year"])) if x < y]
        per.append(grader.score(t, s_fn(fit), fit, [y]))
    return {"interval_score": float(np.mean([p["interval_score"] for p in per])),
            "coverage": float(np.mean([p["coverage"] for p in per]))}


report = {"period": a.period, "fit_years": FIT, "eval_years": EVAL, "runs": a.runs,
          "valuationlab_commit": vl.vl_commit(), "multiples": {}}
for m in ag.MULTIPLES:
    t = base_table(m, include_holdout=a.period == "holdout")
    R = {"benchmarks": {}, "finalists": {}, "tests": {}}
    if a.period == "holdout":
        # Reproducibility: rebuilding with holdout rows must leave every FY2016-2023 row unchanged.
        old = base_table(m)
        cols = ["id", "fiscal_year", "e", "peer_iqr"] + [c for c in old.columns if c.startswith("pct_")]
        new = t[t["fiscal_year"] <= max(VAL)][cols].reset_index(drop=True)
        same = old[cols].reset_index(drop=True).equals(new)
        R["reproducibility_fy2016_2023"] = bool(same)
        if not same:
            sys.exit(f"{m}: FY2016-2023 rows changed when holdout rows were added; stopping before scoring")
    t = t[t["fiscal_year"].isin(FIT + VAL + EVAL)].reset_index(drop=True)
    te = t[t["fiscal_year"].isin(EVAL)].reset_index(drop=True)
    for k, v in baselines.practice(te).items():
        R["benchmarks"][k] = v
    for k, fn in baselines.calibrated_methods(t, m).items():
        R["benchmarks"][k] = grader.score(t, fn(FIT), FIT, EVAL) | {"rolling": rolling(t, fn)}
    for f in finals:
        fin = f["finalists"][m]
        rule = validate(fin["spec"])
        s = rule.score(t)
        R["finalists"][f["run"]] = (grader.score(t, s, FIT, EVAL)
                                    | {"rolling": rolling(t, baselines.fixed_fn(s)), "id": fin["id"],
                                       "compact": fin["compact"], "explore_is": fin["explore"]["interval_score"]})
    if a.period == "holdout":  # secondary: fit and calibrate on FY2016-2023
        fit2 = FIT + VAL
        R["secondary_fit_2016_2023"] = {
            "benchmarks": {k: grader.score(t, fn(fit2), fit2, EVAL)["interval_score"]
                           for k, fn in baselines.calibrated_methods(t, m).items()},
            "finalists": {f["run"]: grader.score(t, validate(f["finalists"][m]["spec"]).score(t), fit2, EVAL)["interval_score"]
                          for f in finals}}
    A = float(np.mean([v["interval_score"] for v in R["finalists"].values()]))
    const, lin, gbm = (R["benchmarks"][k]["interval_score"] for k in ("constant", "linear_all", "gbm"))

    # T2: random search with the same budget
    pool = [rec for r in runs for rec in r.archive("random") if rec["multiple"] == m]
    pool_val = np.array([grader.score(t, validate(p["spec"]).score(t), FIT, EVAL)["interval_score"] for p in pool])
    sims = np.zeros(a.sims)
    for f in finals:
        n = f["graded_per_multiple"][m]
        idx = ag.best_of_random(pool, m, n, a.sims, rng)
        sims += pool_val[idx]
    sims /= len(finals)
    p_t2 = float((sims <= A).mean())

    n_beat = sum(v["interval_score"] < const for v in R["finalists"].values())
    R["tests"] = {
        "agents_mean_interval_score": A,
        "T1_vs_constant": {"constant": const, "runs_below": n_beat, "pass": bool(A < const and n_beat >= 4)},
        "T2_vs_random": {"random_median_of_means": float(np.median(sims)), "p_one_sided": p_t2},
        "T3_vs_linear_all": {"linear_all": lin, "pass": bool(A <= lin)},
        "T4_share_of_gbm_gain": {"gbm": gbm, "G": float((const - A) / (const - gbm)),
                                 "close_to_black_box": bool((const - A) / (const - gbm) >= 0.75)},
        "secondary_segment_mad80": {"agents_mean": float(np.mean([mad80(v) for v in R["finalists"].values()])),
                                    **{k: mad80(R["benchmarks"][k]) for k in ("constant", "linear_all", "gbm")}},
    }
    report["multiples"][m] = R

# Holm across the two multiples for T2
ps = sorted((report["multiples"][m]["tests"]["T2_vs_random"]["p_one_sided"], m) for m in ag.MULTIPLES)
for i, (p, m) in enumerate(ps):
    adj = min(1.0, max(p * (len(ps) - j) for j, _ in enumerate(ps[: i + 1])))
    report["multiples"][m]["tests"]["T2_vs_random"].update(p_holm=adj, **{"pass": bool(adj < 0.05)})

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "report.json").write_text(json.dumps(report, indent=1, default=float))

L = [f"# {a.period.capitalize()} report: FY{EVAL[0]}–{EVAL[-1]}", "",
     f"Produced by `scripts/evaluate.py` under [`docs/protocol.md`](../../docs/protocol.md). Fitted and calibrated "
     f"on FY{FIT[0]}–{FIT[-1]}. Runs: {', '.join(a.runs)}. ValuationLab commit `{report['valuationlab_commit']}`.", ""]
for m, R in report["multiples"].items():
    T = R["tests"]
    L += [f"## {m}", "", "| Method | Interval score | Coverage | Median range (×/÷) | Segment coverage MAD from 80% | Rolling recalibration IS |",
          "|---|---|---|---|---|---|"]
    rows = [(f"Agent finalist {k} ({v['id']})", v) for k, v in R["finalists"].items()] + list(R["benchmarks"].items())
    for k, v in rows:
        roll = f"{v['rolling']['interval_score']:.3f}" if "rolling" in v else "—"
        L.append(f"| {k} | {v['interval_score']:.3f} | {v['coverage']:.1%} | {v['median_factor']:.2f} | {mad80(v):.3f} | {roll} |")
    L += ["", f"- Agents' mean interval score: **{T['agents_mean_interval_score']:.3f}**",
          f"- T1 vs constant band ({T['T1_vs_constant']['constant']:.3f}): {T['T1_vs_constant']['runs_below']}/5 runs below → "
          f"**{'pass' if T['T1_vs_constant']['pass'] else 'fail'}**",
          f"- T2 vs random search, same budget (median {T['T2_vs_random']['random_median_of_means']:.3f}): p = "
          f"{T['T2_vs_random']['p_one_sided']:.4f}, Holm {T['T2_vs_random']['p_holm']:.4f} → "
          f"**{'pass' if T['T2_vs_random']['pass'] else 'fail'}**",
          f"- T3 vs linear_all ({T['T3_vs_linear_all']['linear_all']:.3f}): **{'pass' if T['T3_vs_linear_all']['pass'] else 'fail'}**",
          f"- T4 share of the black-box gain (gbm {T['T4_share_of_gbm_gain']['gbm']:.3f}): G = {T['T4_share_of_gbm_gain']['G']:.2f} → "
          f"{'close to the black box' if T['T4_share_of_gbm_gain']['close_to_black_box'] else 'not close to the black box'}", ""]
    L += ["Finalist rules:", ""] + [f"- {k}: `{v['compact']}`" for k, v in R["finalists"].items()] + [""]
(OUT / "REPORT.md").write_text("\n".join(L))
print("\n".join(L))
