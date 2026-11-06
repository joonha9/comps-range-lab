"""Range-rule schema and validator.

A range rule is a firm-agnostic statement of how uncertain a comps valuation is for each firm.
It produces a positive *uncertainty score* s for every target firm-year; the grader turns scores
into ranges by calibration (see grader.py), so a rule only has to rank firms by how far their
market value tends to fall from the comps estimate. Example:

    {
      "name": "small and research-heavy firms are harder to price",
      "multiple": "EV/EBITDA",
      "base": "peer_iqr",
      "terms": {"log_sales": -0.8, "rnd_intensity": 0.6},
      "conditions": [
        {"if": [{"var": "loss_making"}], "times": 1.4},
        {"if": [{"var": "sales_growth_1y", "above_pct": 80}, {"var": "log_sales", "below_pct": 30}],
         "times": 1.3}
      ]
    }

Score:  s = base x exp( sum_j w_j * (pct_j - 0.5) ) x product of `times` for conditions that hold
- base: "constant" (1) or "peer_iqr" (the log interquartile width of the peer multiples, floored at
  0.05) or "peer_range" (log max/min of peer multiples, floored at 0.10).
- terms: up to 4 continuous inputs with weights in [-3, 3]. pct_j is the firm's within-year
  percentile rank (0-1) on that input; a missing input counts as the median (0.5).
- conditions: up to 4. Each `if` is an AND of 1-2 clauses; a clause is a flag (`{"var": "loss_making"}`)
  or a continuous input with exactly one of below_pct / above_pct (an integer 5-95). A missing
  input makes the clause false. `times` must be in [0.25, 4].
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

from .base import FLAG_VARS, RULE_VARS

BASES = {"constant": None, "peer_iqr": 0.05, "peer_range": 0.10}
MAX_TERMS, MAX_CONDITIONS, MAX_CLAUSES = 4, 4, 2
W_RANGE, TIMES_RANGE, PCT_RANGE = (-3.0, 3.0), (0.25, 4.0), (5, 95)
TEXT_KEYS = {"mechanism", "prediction", "rationale", "short"}


class RuleError(ValueError):
    """Raised when a rule violates the schema. The message lists every problem."""


@dataclass(frozen=True)
class Rule:
    name: str
    multiple: str
    base: str = "constant"
    terms: dict[str, float] = field(default_factory=dict)
    conditions: tuple[dict, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "multiple": self.multiple, "base": self.base,
                "terms": dict(self.terms), "conditions": [dict(c) for c in self.conditions]}

    def score(self, t: pd.DataFrame) -> np.ndarray:
        """Uncertainty score for every row of a base table."""
        if self.base == "constant":
            s = np.ones(len(t))
        else:
            s = np.maximum(t[self.base].to_numpy(dtype=float), BASES[self.base])
        lin = np.zeros(len(t))
        for v, w in self.terms.items():
            lin += w * (np.nan_to_num(t[f"pct_{v}"].to_numpy(dtype=float), nan=0.5) - 0.5)
        s = s * np.exp(lin)
        for c in self.conditions:
            hold = np.ones(len(t), dtype=bool)
            for cl in c["if"]:
                hold &= _clause(t, cl)
            s = np.where(hold, s * c["times"], s)
        return s


def _clause(t: pd.DataFrame, cl: dict) -> np.ndarray:
    v = cl["var"]
    if v in FLAG_VARS:
        return t[v].fillna(False).to_numpy(dtype=bool)
    p = t[f"pct_{v}"].to_numpy(dtype=float) * 100
    if "below_pct" in cl:
        return np.nan_to_num(p, nan=np.inf) <= cl["below_pct"]
    return np.nan_to_num(p, nan=-np.inf) >= cl["above_pct"]


def _num(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and np.isfinite(x)


def validate(spec: dict[str, Any], multiples: tuple[str, ...] = ("EV/EBITDA", "EV/Sales")) -> Rule:
    """Return a Rule or raise RuleError listing every violation."""
    p: list[str] = []
    if not isinstance(spec, dict):
        raise RuleError("rule must be a JSON object")
    extra = set(spec) - {"name", "multiple", "base", "terms", "conditions"} - TEXT_KEYS
    if extra:
        p.append(f"unknown keys: {sorted(extra)}")
    name = spec.get("name")
    if not isinstance(name, str) or not name.strip():
        p.append("name: required non-empty string")
    if spec.get("multiple") not in multiples:
        p.append(f"multiple: must be one of {list(multiples)}")
    base = spec.get("base", "constant")
    if base not in BASES:
        p.append(f"base: must be one of {sorted(BASES)}")

    terms = spec.get("terms", {})
    if not isinstance(terms, dict):
        p.append("terms: must be an object {input: weight}")
        terms = {}
    if len(terms) > MAX_TERMS:
        p.append(f"terms: at most {MAX_TERMS}")
    for v, w in terms.items():
        if v not in RULE_VARS:
            p.append(f"terms.{v}: unknown continuous input (flags go in conditions)")
        if not _num(w) or not W_RANGE[0] <= w <= W_RANGE[1] or w == 0:
            p.append(f"terms.{v}: weight must be a non-zero number in {list(W_RANGE)}")

    conds = spec.get("conditions", [])
    if not isinstance(conds, list):
        p.append("conditions: must be a list")
        conds = []
    if len(conds) > MAX_CONDITIONS:
        p.append(f"conditions: at most {MAX_CONDITIONS}")
    for i, c in enumerate(conds):
        tag = f"conditions[{i}]"
        if not isinstance(c, dict) or set(c) != {"if", "times"}:
            p.append(f"{tag}: needs exactly 'if' and 'times'")
            continue
        if not _num(c["times"]) or not TIMES_RANGE[0] <= c["times"] <= TIMES_RANGE[1] or c["times"] == 1:
            p.append(f"{tag}.times: must be a number in {list(TIMES_RANGE)} other than 1")
        cl = c["if"]
        if not isinstance(cl, list) or not 1 <= len(cl) <= MAX_CLAUSES:
            p.append(f"{tag}.if: a list of 1-{MAX_CLAUSES} clauses")
            continue
        for j, x in enumerate(cl):
            ct = f"{tag}.if[{j}]"
            if not isinstance(x, dict) or "var" not in x:
                p.append(f"{ct}: needs 'var'")
                continue
            v, rest = x["var"], set(x) - {"var"}
            if v in FLAG_VARS:
                if rest:
                    p.append(f"{ct}: flag '{v}' takes no threshold")
            elif v in RULE_VARS:
                if len(rest) != 1 or not rest <= {"below_pct", "above_pct"}:
                    p.append(f"{ct}: give exactly one of below_pct / above_pct")
                else:
                    (k,) = rest
                    if not isinstance(x[k], int) or isinstance(x[k], bool) or not PCT_RANGE[0] <= x[k] <= PCT_RANGE[1]:
                        p.append(f"{ct}.{k}: an integer in {list(PCT_RANGE)}")
            else:
                p.append(f"{ct}: unknown input '{v}'")
    if base == "constant" and not terms and not conds:
        p.append("rule is the constant band: add terms, conditions or a peer-based base")
    if p:
        raise RuleError("; ".join(p))
    return Rule(name=name.strip(), multiple=spec["multiple"], base=base,
                terms={k: float(v) for k, v in terms.items()},
                conditions=tuple({"if": [dict(x) for x in c["if"]], "times": float(c["times"])} for c in conds))
