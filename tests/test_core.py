"""Unit tests on synthetic data (no FactSet needed): rule validator, scores, calibration, grading."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rangelab import grader  # noqa: E402
from rangelab.base import FLAG_VARS, RULE_VARS  # noqa: E402
from rangelab.rules import RuleError, validate  # noqa: E402


def table(n_per_year=2000, years=(2016, 2017, 2018, 2019), seed=0):
    rng = np.random.default_rng(seed)
    rows = []
    for y in years:
        d = pd.DataFrame({v: rng.normal(size=n_per_year) for v in RULE_VARS})
        d["peer_iqr"] = rng.uniform(0.1, 1.0, n_per_year)
        for f in FLAG_VARS:
            d[f] = rng.random(n_per_year) < 0.2
        # true uncertainty rises with log_sales being small
        sd = np.exp(-0.5 * d["log_sales"])
        d["e"] = 0.1 + sd * rng.normal(size=n_per_year)
        d["fiscal_year"] = y
        d["id"] = np.arange(n_per_year)
        rows.append(d)
    t = pd.concat(rows, ignore_index=True)
    for v in RULE_VARS:
        t[f"pct_{v}"] = t.groupby("fiscal_year")[v].rank(pct=True)
    return t


def test_validator_rejects_bad_rules():
    with pytest.raises(RuleError):
        validate({"name": "x", "multiple": "EV/EBITDA"})  # constant band is not a rule
    with pytest.raises(RuleError):
        validate({"name": "x", "multiple": "EV/EBITDA", "terms": {"mkt_cap": 1.0}})
    with pytest.raises(RuleError):
        validate({"name": "x", "multiple": "EV/EBITDA", "terms": {"log_sales": 5}})
    with pytest.raises(RuleError):
        validate({"name": "x", "multiple": "EV/EBITDA",
                  "conditions": [{"if": [{"var": "log_sales", "below_pct": 20, "above_pct": 80}], "times": 2}]})
    with pytest.raises(RuleError):
        validate({"name": "x", "multiple": "EV/EBITDA", "conditions": [{"if": [{"var": "loss_making"}], "times": 1}]})


def test_score_formula():
    t = table(n_per_year=100, years=(2016,))
    r = validate({"name": "x", "multiple": "EV/EBITDA", "base": "peer_iqr", "terms": {"log_sales": -1.0},
                  "conditions": [{"if": [{"var": "loss_making"}], "times": 2.0}]})
    s = r.score(t)
    expect = np.maximum(t["peer_iqr"], 0.05) * np.exp(-1.0 * (t["pct_log_sales"] - 0.5)) \
        * np.where(t["loss_making"], 2.0, 1.0)
    assert np.allclose(s, expect)


def test_threshold_clause_and_missing():
    t = table(n_per_year=100, years=(2016,))
    t.loc[0, "pct_roe"] = np.nan
    r = validate({"name": "x", "multiple": "EV/EBITDA",
                  "conditions": [{"if": [{"var": "roe", "above_pct": 80}], "times": 3.0}]})
    s = r.score(t)
    assert s[0] == 1.0  # missing input: clause false
    assert np.all((s == 3.0) == (t["pct_roe"].fillna(0) * 100 >= 80))


def test_conformal_coverage_and_informative_rule_wins():
    t = table()
    years = [2016, 2017, 2018, 2019]
    const = grader.score_loyo(t, lambda fy: np.ones(len(t)), years)
    good = validate({"name": "g", "multiple": "EV/EBITDA", "terms": {"log_sales": -2.5}})
    gs = grader.score_loyo(t, lambda fy: good.score(t), years)
    assert abs(const["coverage"] - 0.8) < 0.02 and abs(gs["coverage"] - 0.8) < 0.02
    assert gs["interval_score"] < const["interval_score"]
    assert abs(const["by_year"][2016]["coverage"] - 0.8) < 0.04


def test_interval_score():
    e = np.array([0.0, 1.0, -1.0])
    lo, hi = np.full(3, -0.5), np.full(3, 0.5)
    assert np.allclose(grader.interval_score(e, lo, hi), [1.0, 1.0 + 10 * 0.5, 1.0 + 10 * 0.5])


def test_scores_must_be_positive():
    t = table(n_per_year=50, years=(2016, 2017))
    with pytest.raises(ValueError):
        grader.score(t, np.zeros(len(t)), [2016], [2017])
