"""Agent search loop (SignalLab design): proposer -> blind critic -> deterministic grader -> archive.

Agents run as Claude Code subagents: each reads a prompt file written here and writes its JSON reply
next to it. This module writes prompts, validates and de-duplicates proposals, applies the critic's
verdicts, grades approved rules on exploration years (leave-one-year-out), and keeps an archive of
every attempt, so the search denominator is known.

Run layout: results/agent_runs/<run>/
  config.json  state.json  archive.jsonl  random.jsonl  final.json
  genNN/proposer_prompt.md  proposals.txt  pending.json  critic_prompt.md  verdicts.txt
"""

from __future__ import annotations

import hashlib
import json
import random
from datetime import datetime
from functools import lru_cache
from pathlib import Path

import numpy as np

from . import baselines, grader, vl
from .base import FLAG_VARS, RULE_VARS, base_table
from .rules import BASES, PCT_RANGE, TIMES_RANGE, W_RANGE, RuleError, validate

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "results/agent_runs"
MULTIPLES = ("EV/EBITDA", "EV/Sales")
DEFAULT_CONFIG = {"generations": 5, "proposals_per_generation": 6, "critic": True,
                  "archive_to_proposer": True, "random_rules_per_multiple": 200}

INPUT_NOTES = {
    "log_sales": "log of sales (size)",
    "log_assets": "log of total assets (size)",
    "sales_growth_1y": "1-year sales growth",
    "sales_growth_3y": "3-year annualized sales growth (missing for FY2016-2017: not enough history)",
    "gross_margin": "gross profit / sales",
    "ebitda_margin": "EBITDA / sales",
    "ebit_margin": "EBIT / sales",
    "net_margin": "net income / sales",
    "roic": "EBIT x (1 - 25%) / (equity + debt - cash)",
    "roe": "net income / book equity",
    "asset_turnover": "sales / total assets",
    "net_debt_to_ebitda": "(debt - cash) / EBITDA",
    "debt_to_assets": "total debt / total assets",
    "rnd_intensity": "R&D / sales",
    "capex_intensity": "capital expenditure / sales",
    "peer_iqr": "log(75th / 25th percentile) of the 10 peers' multiples: how much the peers disagree",
    "peer_range": "log(max / min) of the peers' multiples",
    "n_peers": "number of peers found (10 unless the sector is thin)",
    "loss_making": "FLAG: net income < 0",
    "negative_ebitda": "FLAG: EBITDA <= 0 (only possible for EV/Sales; EV/EBITDA needs positive EBITDA)",
    "no_history": "FLAG: no prior-year sales in the data (recent listing or new to the sample)",
}


# ---------------------------------------------------------------- data and grading

@lru_cache(maxsize=None)
def explore_table(multiple: str):
    t = base_table(multiple)
    return t[t["fiscal_year"].isin(vl.PROTOCOL.years("explore"))].reset_index(drop=True)


def grade_explore(rule) -> dict:
    t = explore_table(rule.multiple)
    s = rule.score(t)
    return grader.score_loyo(t, baselines.fixed_fn(s), vl.PROTOCOL.years("explore"))


@lru_cache(maxsize=1)
def benchmark_scores() -> dict:
    """Exploration scorecards of the benchmarks (computed by scripts/run_baselines.py)."""
    return json.loads((ROOT / "results/baselines/explore.json").read_text())["multiples"]


def rule_hash(rule) -> str:
    d = rule.to_dict()
    d.pop("name")
    return hashlib.sha1(json.dumps(d, sort_keys=True).encode()).hexdigest()[:10]


def compact(rule) -> str:
    parts = [rule.multiple, f"base {rule.base}"]
    if rule.terms:
        parts.append("terms " + ", ".join(f"{v} {w:+g}" for v, w in rule.terms.items()))
    for c in rule.conditions:
        cl = " AND ".join(x["var"] if x["var"] in FLAG_VARS else
                          f"{x['var']} {'<=' if 'below_pct' in x else '>='} p{x.get('below_pct', x.get('above_pct'))}"
                          for x in c["if"])
        parts.append(f"if {cl} x{c['times']:g}")
    return " | ".join(parts)


def _segtxt(card: dict) -> str:
    return ", ".join(f"{k} {v['coverage']:.0%}" for k, v in card["segments"].items() if v["coverage"] is not None)


# ---------------------------------------------------------------- run state

class Run:
    def __init__(self, name: str, config: dict | None = None):
        self.dir = RUNS / name
        self.name = name
        if config is not None:
            self.dir.mkdir(parents=True, exist_ok=False)
            (self.dir / "config.json").write_text(json.dumps({**DEFAULT_CONFIG, **config,
                                                              "created": datetime.now().isoformat(timespec="seconds"),
                                                              "valuationlab_commit": vl.vl_commit()}, indent=1))
            self.save_state({"generation": 0, "stage": "new"})
        self.config = json.loads((self.dir / "config.json").read_text())

    @property
    def state(self) -> dict:
        return json.loads((self.dir / "state.json").read_text())

    def save_state(self, s: dict) -> None:
        (self.dir / "state.json").write_text(json.dumps(s))

    def gen_dir(self, g: int) -> Path:
        d = self.dir / f"gen{g:02d}"
        d.mkdir(exist_ok=True)
        return d

    def archive(self, kind: str = "archive") -> list[dict]:
        f = self.dir / f"{kind}.jsonl"
        return [json.loads(x) for x in f.read_text().splitlines()] if f.exists() else []

    def append(self, rec: dict, kind: str = "archive") -> None:
        with open(self.dir / f"{kind}.jsonl", "a") as f:
            f.write(json.dumps(rec, default=float) + "\n")


# ---------------------------------------------------------------- prompts

def dsl_text() -> str:
    inputs = "\n".join(f"  - {k}: {v}" for k, v in INPUT_NOTES.items())
    return f"""RULE LANGUAGE
A range rule gives every target firm-year a positive UNCERTAINTY SCORE s. Only the relative
ranking of s across firms matters: the grader converts scores into ranges by calibration.

  s = BASE x exp( sum_j w_j * (pct_j - 0.5) ) x (product of `times` for every condition that holds)

  base:        one of {sorted(BASES)}
               "constant" = 1; "peer_iqr" = the peers' log interquartile spread (floored at 0.05);
               "peer_range" = the peers' log max/min spread (floored at 0.10)
  terms:       up to 4 {{INPUT: weight}}, weight a non-zero number in {list(W_RANGE)}.
               pct_j is the firm's percentile rank (0-1) on that input WITHIN its fiscal year, so
               weight +1.0 makes the top firm's score e^1 = 2.7x the bottom firm's. Missing = median.
  conditions:  up to 4 {{"if": [clause, clause?], "times": t}}, t in {list(TIMES_RANGE)}, t != 1.
               All clauses (1 or 2) must hold. A clause is a FLAG {{"var": "loss_making"}} or a
               continuous input with exactly one threshold {{"var": X, "below_pct": P}} or
               {{"var": X, "above_pct": P}}, P an integer {PCT_RANGE[0]}-{PCT_RANGE[1]} (within-year percentile).
               A missing input makes the clause false.
  The constant band alone (base "constant", no terms, no conditions) is not a valid proposal.

INPUTS (accounting characteristics of the target, statistics of its peers, and flags; the
target's own market value, price or multiple is never available)
{inputs}

HOW RANGES ARE SCORED
  Point estimate: the median EV multiple of the target's 10 nearest peers (same 2-digit SIC;
  nearest on size and EBITDA margin) times the target's EBITDA or sales. e = ln(actual EV /
  point estimate), actual EV on June 30 after the fiscal year.
  Calibration on the other years: centre c = median e; q = 80% conformal quantile of |e - c| / s.
  Range: point x exp(c - q s) to point x exp(c + q s). So every rule covers ~80% overall; a good
  rule puts wide ranges on firms that are truly hard to value and narrow ranges on easy ones.
  Interval score (lower is better) = width + 10 x distance outside the range, in logs.
  Exploration score: leave-one-year-out over FY2016-2019 (calibrate on 3 years, score the 4th).
"""


def _bench_text() -> str:
    b = benchmark_scores()
    names = {"practice_iqr": "peer 25-75% range as practitioners report it (not calibrated)",
             "constant": "constant band (same width for every firm)",
             "peer_iqr_scaled": "width proportional to peer_iqr",
             "linear_all": "linear regression on ALL inputs (no limit on terms)",
             "gbm": "gradient-boosted trees on all inputs (black box)"}
    out = []
    for m in MULTIPLES:
        out.append(f"  {m}:")
        for k, label in names.items():
            r = b[m][k]
            out.append(f"    {label}: interval score {r['interval_score']:.3f}, coverage {r['coverage']:.1%}, "
                       f"median range x/{r['median_factor']:.2f}")
        out.append(f"    coverage of the constant band by firm type: {_segtxt(b[m]['constant'])}")
    return "\n".join(out)


def proposer_prompt(run: Run, g: int) -> str:
    k = run.config["proposals_per_generation"]
    arch = run.archive() if run.config.get("archive_to_proposer", True) else []
    graded = sorted([a for a in arch if a["status"] == "graded"],
                    key=lambda a: (a["multiple"], a["explore"]["interval_score"]))
    lines = [f"  [{a['id']}] {a['multiple']} interval score {a['explore']['interval_score']:.3f} | coverage "
             f"{a['explore']['coverage']:.1%} | median range x/{a['explore']['median_factor']:.2f}\n"
             f"      {a['compact']}\n      by firm type: {_segtxt(a['explore'])}\n      mechanism: {a['mechanism']}"
             for a in graded]
    failed = [f"  [{a['id']}] {a['status']}: {a.get('reason', '')[:220]}" for a in arch if a["status"] != "graded"][-15:]
    archive_block = "" if not run.config.get("archive_to_proposer", True) else f"""
ARCHIVE: your earlier graded attempts, exploration scores only ({len(graded)} graded)
{chr(10).join(lines) if lines else "  (none yet)"}

FAILED OR REJECTED ATTEMPTS (most recent)
{chr(10).join(failed) if failed else "  (none)"}
"""
    critic_note = ("An independent referee, who sees your mechanism but no scores, will reject proposals without a\n"
                   "specific economic reason, or near-copies of earlier rules (e.g. one weight changed slightly).\n"
                   if run.config.get("critic", True) else "")
    return f"""You are a valuation researcher. Comparable-company valuations ("comps") are reported as ranges,
and practitioners' ranges are badly calibrated. Your job is to discover short, interpretable rules
that say HOW UNCERTAIN a comps valuation is for each US non-financial firm, so its range can be
wide where comps are unreliable and narrow where they are reliable.

TASK
Propose exactly {k} NEW range rules (generation {g}): {k // 2} for EV/EBITDA and {k - k // 2} for EV/Sales.
Rules are scored only on exploration years FY2016-2019. The best rule per multiple will later be
tested ONCE on later years you will never see, so prefer rules with a clear economic reason over
fragile tweaks. A practitioner should be able to read your rule and apply it by hand.

{dsl_text()}
BENCHMARKS (exploration years)
{_bench_text()}
{archive_block}
Each proposal needs:
  - "mechanism": the economic reason these firms' market values are harder (or easier) to pin
    down with comps (2-3 sentences)
  - "prediction": a falsifiable expectation, e.g. "interval score below the constant band's"
  - "rule": the rule object
{critic_note}
Reply with ONLY this JSON, no other text:
{{"proposals": [{{"name": "...", "mechanism": "...", "prediction": "...",
  "rule": {{"multiple": "...", "base": "...", "terms": {{...}}, "conditions": [...]}}}}]}}
"""


def critic_prompt(run: Run, pending: list[dict]) -> str:
    tried = "\n".join(f"  [{a['id']}] {a['compact']}" for a in run.archive()
                      if a["status"] in ("graded", "rejected")) or "  (none)"
    props = "\n\n".join(f"  ({i}) {p['name']}\n      rule: {p['compact']}\n      mechanism: {p['mechanism']}\n"
                        f"      prediction: {p['prediction']}" for i, p in enumerate(pending))
    return f"""You are an independent referee for a valuation research project. A proposer has submitted
rules that say how uncertain a comparable-company valuation is for each firm. You decide which may
be tested. You do NOT see any results, and you must not try to find any: judge only the logic.

{dsl_text()}
Approve a proposal only if ALL hold:
  1. The mechanism is a specific, economically sensible reason why comps should be less (or
     more) reliable for the firms the rule singles out.
  2. The rule actually implements that mechanism (inputs, signs and conditions match it).
  3. It is not a trivial variant of a rule already tried (listed below): changing only one weight
     or one threshold slightly is trivial; a new input, condition or economic idea is not.
  4. The prediction is falsifiable.
Reject otherwise, with a one-sentence reason the proposer can learn from.

RULES ALREADY TRIED (no scores shown)
{tried}

PROPOSALS
{props}

Reply with ONLY this JSON, no other text:
{{"verdicts": [{{"index": 0, "verdict": "approve" or "reject", "reason": "..."}}]}}
"""


# ---------------------------------------------------------------- loop steps

def parse_json_reply(text: str) -> dict:
    s = text.strip()
    if "```" in s:
        s = s.split("```")[1]
        s = s[4:] if s.startswith("json") else s
    i, j = s.find("{"), s.rfind("}")
    return json.loads(s[i:j + 1])


def register_proposals(run: Run, reply: dict, g: int) -> list[dict]:
    known = {a["hash"] for a in run.archive() if a.get("hash")}
    pending = []
    for i, p in enumerate(reply.get("proposals", [])):
        rid = f"g{g:02d}-{i + 1:02d}"
        rec = {"id": rid, "generation": g, "proposer": "claude-code-subagent",
               "time": datetime.now().isoformat(timespec="seconds"),
               "name": p.get("name", ""), "mechanism": p.get("mechanism", ""),
               "prediction": p.get("prediction", ""), "raw": p.get("rule")}
        try:
            spec = dict(p.get("rule") or {})
            spec["name"] = p.get("name") or rid
            r = validate(spec)
        except (RuleError, TypeError, ValueError, AttributeError) as e:
            run.append({**rec, "status": "invalid", "reason": str(e)})
            continue
        h = rule_hash(r)
        rec.update(hash=h, multiple=r.multiple, spec=r.to_dict(), compact=compact(r))
        if h in known:
            run.append({**rec, "status": "duplicate", "reason": "identical to an archived rule"})
            continue
        known.add(h)
        pending.append(rec)
    (run.gen_dir(g) / "pending.json").write_text(json.dumps(pending, indent=1))
    return pending


def apply_verdicts(run: Run, reply: dict | None, g: int) -> list[dict]:
    pending = json.loads((run.gen_dir(g) / "pending.json").read_text())
    if reply is None:
        reply = {"verdicts": [{"index": i, "verdict": "approve", "reason": "(no critic in this condition)"}
                              for i in range(len(pending))]}
    verdicts = {int(v["index"]): v for v in reply.get("verdicts", [])}
    out = []
    for i, rec in enumerate(pending):
        v = verdicts.get(i, {"verdict": "reject", "reason": "no verdict returned"})
        rec = {**rec, "critic": v.get("verdict"), "critic_reason": v.get("reason", "")}
        if str(v.get("verdict", "")).lower() != "approve":
            rec.update(status="rejected", reason="critic: " + v.get("reason", ""))
        else:
            rec.update(status="graded", explore=grade_explore(validate(rec["spec"])))
        run.append(rec)
        out.append(rec)
    return out


# ---------------------------------------------------------------- random-search control

def random_rule(rng: random.Random, multiple: str) -> dict:
    """A rule drawn uniformly from the language, with no economic knowledge (seeded)."""
    while True:
        base = rng.choice(sorted(BASES))
        terms = {v: round(rng.choice([-1, 1]) * rng.uniform(0.2, 2.0), 1)
                 for v in rng.sample(RULE_VARS, rng.randint(0, 4))}
        conds = []
        for _ in range(rng.randint(0, 3)):
            cl = []
            for v in rng.sample(RULE_VARS + FLAG_VARS, rng.randint(1, 2)):
                if v in FLAG_VARS:
                    cl.append({"var": v})
                else:
                    cl.append({"var": v, rng.choice(["below_pct", "above_pct"]): rng.choice(range(10, 91, 10))})
            t = round(rng.uniform(0.5, 2.0), 1)
            conds.append({"if": cl, "times": t if t != 1.0 else 1.5})
        spec = {"name": "random", "multiple": multiple, "base": base, "terms": terms, "conditions": conds}
        try:
            return {**spec, "_rule": validate(spec)}
        except RuleError:
            continue


def run_random(run: Run, seed: int) -> None:
    rng = random.Random(seed)
    n = run.config["random_rules_per_multiple"]
    for m in MULTIPLES:
        for i in range(n):
            spec = random_rule(rng, m)
            r = spec.pop("_rule")
            run.append({"id": f"random-{m.split('/')[1].lower()}-{i + 1:03d}", "status": "graded", "multiple": m,
                        "hash": rule_hash(r), "spec": r.to_dict(), "compact": compact(r),
                        "explore": grade_explore(r)}, kind="random")


# ---------------------------------------------------------------- selection (fixed before the search)

SELECTION_RULE = "per multiple, the graded rule with the lowest exploration interval score"


def select(records: list[dict]) -> dict[str, dict]:
    out = {}
    for m in MULTIPLES:
        g = [r for r in records if r["status"] == "graded" and r["multiple"] == m]
        if g:
            out[m] = min(g, key=lambda r: (r["explore"]["interval_score"], r["id"]))
    return out


def best_of_random(rnd: list[dict], multiple: str, n: int, draws: int, rng: np.random.Generator) -> np.ndarray:
    """Indices of the selected rule in `draws` random searches of size n (same selection rule)."""
    pool = [r for r in rnd if r["multiple"] == multiple]
    s = np.array([r["explore"]["interval_score"] for r in pool])
    picks = np.array([rng.choice(len(pool), size=n, replace=False) for _ in range(draws)])
    return picks[np.arange(draws), np.argmin(s[picks], axis=1)]


def funnel(arch: list[dict]) -> dict:
    keys = ("graded", "rejected", "invalid", "duplicate")
    return {"proposed": len(arch), **{k: sum(a["status"] == k for a in arch) for k in keys}}
