"""Access to the ValuationLab panel, comps engine and baselines.

ValuationLab (https://github.com/joonha9/Valuation_Lab) is a sibling checkout. Its location is
read from the VALUATION_LAB environment variable, or defaults to ../valuation-lab next to this
repository. The licensed FactSet data stays inside that checkout and is never copied here.
Results in this repository were produced against ValuationLab commit VL_COMMIT; scripts record
the commit they actually ran against.
"""

from __future__ import annotations

import os
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VL_ROOT = Path(os.environ.get("VALUATION_LAB", ROOT.parent / "valuation-lab")).resolve()
VL_COMMIT = "7830673"

if not (VL_ROOT / "valuationlab").is_dir():
    raise ImportError(f"ValuationLab not found at {VL_ROOT}; set VALUATION_LAB to its checkout")
sys.path.insert(0, str(VL_ROOT))

from valuationlab.baselines import baselines_for  # noqa: E402
from valuationlab.data import load_panel  # noqa: E402
from valuationlab.engine import apply_recipe  # noqa: E402
from valuationlab.grader import Protocol  # noqa: E402
from valuationlab.panel import FEATURES, MULTIPLES  # noqa: E402
from valuationlab.recipe import validate  # noqa: E402

# Same split as ValuationLab. FY2024-2025 were opened once for ValuationLab's peer recipes
# (2026-11-05); they are used here only under this repository's own frozen protocol.
PROTOCOL = Protocol(explore=(2016, 2017, 2018, 2019), validate=(2020, 2021, 2022, 2023),
                    holdout=(2024, 2025))


def vl_commit() -> str:
    try:
        return subprocess.check_output(["git", "-C", str(VL_ROOT), "rev-parse", "--short", "HEAD"],
                                       text=True).strip()
    except Exception:
        return "unknown"


@lru_cache(maxsize=1)
def panel():
    return load_panel(VL_ROOT)


def panel_with_holdout():
    """FY2015-2025. Only the one-time holdout evaluation under docs/protocol.md may call this."""
    return load_panel(VL_ROOT, include_holdout=True)


__all__ = ["FEATURES", "MULTIPLES", "PROTOCOL", "VL_COMMIT", "VL_ROOT", "apply_recipe",
           "baselines_for", "panel", "panel_with_holdout", "validate", "vl_commit"]
