"""Freeze each completed run's finalists (selection rule in docs/protocol.md) into final.json.

Uses exploration scores only. Run before scripts/evaluate.py; commit the result first.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rangelab import agents as ag  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--runs", nargs="+", required=True)
a = ap.parse_args()

for name in a.runs:
    run = ag.Run(name)
    if run.state["stage"] != "complete":
        sys.exit(f"{name} is not complete: {run.state}")
    f = run.dir / "final.json"
    if f.exists():
        sys.exit(f"{name}: final.json already exists (frozen)")
    arch = run.archive()
    fin = ag.select(arch)
    out = {"run": name, "selection_rule": ag.SELECTION_RULE, "funnel": ag.funnel(arch),
           "graded_per_multiple": {m: sum(r["status"] == "graded" and r["multiple"] == m for r in arch)
                                   for m in ag.MULTIPLES},
           "finalists": {m: {k: r[k] for k in ("id", "name", "mechanism", "spec", "compact")}
                         | {"explore": {k: r["explore"][k] for k in ("interval_score", "coverage", "median_factor")}}
                         for m, r in fin.items()}}
    f.write_text(json.dumps(out, indent=1))
    for m, r in fin.items():
        print(f"{name} {m}: {r['id']} explore IS {r['explore']['interval_score']:.3f}  {r['compact']}")
