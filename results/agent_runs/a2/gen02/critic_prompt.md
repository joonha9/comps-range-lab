You are an independent referee for a valuation research project. A proposer has submitted
rules that say how uncertain a comparable-company valuation is for each firm. You decide which may
be tested. You do NOT see any results, and you must not try to find any: judge only the logic.

RULE LANGUAGE
A range rule gives every target firm-year a positive UNCERTAINTY SCORE s. Only the relative
ranking of s across firms matters: the grader converts scores into ranges by calibration.

  s = BASE x exp( sum_j w_j * (pct_j - 0.5) ) x (product of `times` for every condition that holds)

  base:        one of ['constant', 'peer_iqr', 'peer_range']
               "constant" = 1; "peer_iqr" = the peers' log interquartile spread (floored at 0.05);
               "peer_range" = the peers' log max/min spread (floored at 0.10)
  terms:       up to 4 {INPUT: weight}, weight a non-zero number in [-3.0, 3.0].
               pct_j is the firm's percentile rank (0-1) on that input WITHIN its fiscal year, so
               weight +1.0 makes the top firm's score e^1 = 2.7x the bottom firm's. Missing = median.
  conditions:  up to 4 {"if": [clause, clause?], "times": t}, t in [0.25, 4.0], t != 1.
               All clauses (1 or 2) must hold. A clause is a FLAG {"var": "loss_making"} or a
               continuous input with exactly one threshold {"var": X, "below_pct": P} or
               {"var": X, "above_pct": P}, P an integer 5-95 (within-year percentile).
               A missing input makes the clause false.
  The constant band alone (base "constant", no terms, no conditions) is not a valid proposal.

INPUTS (accounting characteristics of the target, statistics of its peers, and flags; the
target's own market value, price or multiple is never available)
  - log_sales: log of sales (size)
  - log_assets: log of total assets (size)
  - sales_growth_1y: 1-year sales growth
  - sales_growth_3y: 3-year annualized sales growth (missing for FY2016-2017: not enough history)
  - gross_margin: gross profit / sales
  - ebitda_margin: EBITDA / sales
  - ebit_margin: EBIT / sales
  - net_margin: net income / sales
  - roic: EBIT x (1 - 25%) / (equity + debt - cash)
  - roe: net income / book equity
  - asset_turnover: sales / total assets
  - net_debt_to_ebitda: (debt - cash) / EBITDA
  - debt_to_assets: total debt / total assets
  - rnd_intensity: R&D / sales
  - capex_intensity: capital expenditure / sales
  - peer_iqr: log(75th / 25th percentile) of the 10 peers' multiples: how much the peers disagree
  - peer_range: log(max / min) of the peers' multiples
  - n_peers: number of peers found (10 unless the sector is thin)
  - loss_making: FLAG: net income < 0
  - negative_ebitda: FLAG: EBITDA <= 0 (only possible for EV/Sales; EV/EBITDA needs positive EBITDA)
  - no_history: FLAG: no prior-year sales in the data (recent listing or new to the sample)

HOW RANGES ARE SCORED
  Point estimate: the median EV multiple of the target's 10 nearest peers (same 2-digit SIC;
  nearest on size and EBITDA margin) times the target's EBITDA or sales. e = ln(actual EV /
  point estimate), actual EV on June 30 after the fiscal year.
  Calibration on the other years: centre c = median e; q = 80% conformal quantile of |e - c| / s.
  Range: point x exp(c - q s) to point x exp(c + q s). So every rule covers ~80% overall; a good
  rule puts wide ranges on firms that are truly hard to value and narrow ranges on easy ones.
  Interval score (lower is better) = width + 10 x distance outside the range, in logs.
  Exploration score: leave-one-year-out over FY2016-2019 (calibrate on 3 years, score the 4th).

Approve a proposal only if ALL hold:
  1. The mechanism is a specific, economically sensible reason why comps should be less (or
     more) reliable for the firms the rule singles out.
  2. The rule actually implements that mechanism (inputs, signs and conditions match it).
  3. It is not a trivial variant of a rule already tried (listed below): changing only one weight
     or one threshold slightly is trivial; a new input, condition or economic idea is not.
  4. The prediction is falsifiable.
Reject otherwise, with a one-sentence reason the proposer can learn from.

RULES ALREADY TRIED (no scores shown)
  [g01-01] EV/EBITDA | base constant | terms log_sales -1, ebitda_margin -1 | if loss_making x1.5
  [g01-02] EV/EBITDA | base constant | terms rnd_intensity +0.8, sales_growth_1y +0.6, log_assets -0.8 | if gross_margin >= p70 AND sales_growth_1y >= p70 x1.3
  [g01-03] EV/EBITDA | base constant | terms net_debt_to_ebitda +0.6, capex_intensity +0.5, log_sales -0.8, peer_range +0.4 | if net_debt_to_ebitda >= p90 x1.4
  [g01-04] EV/Sales | base constant | terms log_sales -1, ebitda_margin -0.8 | if negative_ebitda x1.6 | if no_history x1.3
  [g01-05] EV/Sales | base constant | terms rnd_intensity +1, gross_margin +0.6, sales_growth_1y +0.6, log_assets -0.8
  [g01-06] EV/Sales | base constant | terms asset_turnover -0.7, log_sales -0.9, net_margin -0.5 | if loss_making AND sales_growth_1y >= p80 x1.5

PROPOSALS
  (0) ebitda_cash_gap
      rule: EV/EBITDA | base constant | terms capex_intensity +0.7, ebitda_margin -0.7 | if loss_making x1.3
      mechanism: EBITDA ignores capital expenditure and every cost below the EBITDA line, so it is a weak stand-in for distributable cash flow when reinvestment needs are heavy relative to sales and margins are thin. How much of such a firm's EBITDA the market capitalizes depends on firm-specific capex and maintenance needs that a peer-median multiple does not capture. A net loss despite positive EBITDA is direct evidence that depreciation, interest and other below-EBITDA items absorb the EBITDA, which is the same gap.
      prediction: Interval score below the constant band's (2.735); coverage of loss_making firms rises above the constant band's 68% while median range width stays near x/2.0.

  (1) ebitda_forward_drift
      rule: EV/EBITDA | base constant | terms log_assets -0.7 | if sales_growth_1y >= p80 x1.4 | if sales_growth_1y <= p10 x1.3 | if no_history x1.3
      mechanism: The market prices forward EBITDA, not trailing EBITDA. When sales are moving fast in either direction, or the firm has no sales history, trailing EBITDA is a stale anchor and the gap between current and forward earnings is large and firm-specific. Small asset bases mean the year-to-year EBITDA itself is volatile, so trailing EBITDA tells less about the earnings level the market is capitalizing.
      prediction: Interval score below the constant band's (2.735); coverage of fastest_growing_20pct firms rises from about 70% to at least 76%.

  (2) ebitda_leverage_dampening
      rule: EV/EBITDA | base constant | terms debt_to_assets -0.7, log_sales -0.7 | if loss_making AND debt_to_assets <= p50 x1.4
      mechanism: Enterprise value is net debt plus equity, and debt is valued close to its book amount while equity carries the sentiment and growth beliefs that make comps errors large. When debt funds a large share of assets, the uncertain equity slice is a small part of EV, so the log error of EV is dampened; small firms' equity also carries more idiosyncratic risk. Loss-making firms that are mostly equity-financed are valued on a growth or turnaround story with almost no debt anchor, so their EV is hardest to pin down.
      prediction: Interval score below the constant band's (2.735) and below the size-only effect, with ranges for high debt_to_assets firms narrower than the median range.

  (3) sales_leverage_dampening
      rule: EV/Sales | base constant | terms debt_to_assets -0.6, ebitda_margin -0.5 | if negative_ebitda x1.3
      mechanism: EV is net debt plus equity, and debt claims are priced near their book value while equity absorbs the market's divergent views about how sales will turn into profit. For heavily debt-financed firms EV is largely the stable debt claim, so EV/Sales errors are compressed; for equity-financed firms with thin EBITDA margins EV is almost entirely an equity bet on future margin expansion that peer revenue multiples cannot price. Negative EBITDA is the extreme case where the value rests entirely on that bet.
      prediction: Interval score below the constant band's (4.233); coverage of loss_making firms between 76% and 86%, avoiding the over-widening of g01-04.

  (4) sales_forward_drift
      rule: EV/Sales | base constant | terms gross_margin +0.5 | if sales_growth_1y >= p80 x1.5 | if sales_growth_1y <= p15 x1.3 | if no_history x1.3
      mechanism: Revenue multiples are applied to trailing sales, but the market values the firm on the sales it will have. When sales are growing or shrinking sharply, or there is no sales history, trailing sales misstate the forward base by a large, firm-specific amount. High gross margins amplify that error because each dollar of forward sales converts to profit at a high rate, so disagreement about future sales becomes larger disagreement about value.
      prediction: Interval score below the constant band's (4.233); coverage of fastest_growing_20pct firms of at least 80% with median range no wider than x/3.4.

  (5) sales_anchor_reliability
      rule: EV/Sales | base constant | terms peer_range +0.4, n_peers -0.6, log_sales -0.5
      mechanism: The point estimate is only as good as the peer set: when few same-SIC peers exist, or the peers' revenue multiples disagree widely, the peer median is a noisy anchor. Because peers are chosen as nearest neighbours on size, the smallest targets sit at the edge of the size distribution and their peers are systematically larger and different, so the median peer multiple is a biased anchor for them.
      prediction: Interval score below the constant band's (4.233); coverage of fallback_or_few_peers rises from 71% to at least 77% and of smallest_20pct from 68% to at least 75%.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}
