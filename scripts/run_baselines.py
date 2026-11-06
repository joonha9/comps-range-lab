"""Exploration-year scorecards (leave-one-year-out, FY2016-2019) for every benchmark.

Validation years are not scored here. Writes results/baselines/explore.json and explore.md.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rangelab import baselines, grader, vl  # noqa: E402
from rangelab.base import base_table  # noqa: E402

OUT = ROOT / "results/baselines"


def main() -> None:
    years = vl.PROTOCOL.years("explore")
    out = {"years": years, "valuationlab_commit": vl.vl_commit(), "multiples": {}}
    for m in ("EV/EBITDA", "EV/Sales"):
        t = base_table(m)
        tx = t[t["fiscal_year"].isin(years)].reset_index(drop=True)
        res = {k: v for k, v in baselines.practice(tx).items()}
        for name, fn in baselines.calibrated_methods(tx, m).items():
            res[name] = grader.score_loyo(tx, fn, years)
        out["multiples"][m] = res
        for k, r in res.items():
            print(f"{m:9s} {k:16s} IS={r['interval_score']:.3f} cover={r['coverage']:.1%} "
                  f"width={r['mean_width']:.3f} factor=x/{r['median_factor']:.2f}  "
                  + " ".join(f"{s[:6]}={v['coverage']:.0%}" for s, v in r["segments"].items()))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "explore.json").write_text(json.dumps(out, indent=1))
    L = ["# Benchmarks on exploration years (leave-one-year-out, FY2016–2019)", "",
         f"ValuationLab commit `{out['valuationlab_commit']}`. Interval score at 80% in logs (lower is better). "
         "Practice ranges are scored as reported, without calibration.", ""]
    seg = list(grader.SEGMENTS)
    L += ["| Multiple | Method | Interval score | Coverage | Median range (×/÷) | "
          + " | ".join(f"Coverage: {s}" for s in seg) + " |", "|" + "---|" * (5 + len(seg))]
    for m, res in out["multiples"].items():
        for k, r in res.items():
            L.append(f"| {m} | {k} | {r['interval_score']:.3f} | {r['coverage']:.1%} | {r['median_factor']:.2f} | "
                     + " | ".join(f"{r['segments'][s]['coverage']:.0%}" for s in seg) + " |")
    (OUT / "explore.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
