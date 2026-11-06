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
  [g01-01] EV/EBITDA | base constant | terms log_sales -1, ebitda_margin -0.8 | if loss_making x1.4
  [g01-02] EV/EBITDA | base constant | terms rnd_intensity +0.8, sales_growth_1y +0.6, log_assets -0.7 | if no_history x1.5
  [g01-03] EV/EBITDA | base constant | terms roic -0.8, log_sales -0.8 | if ebitda_margin <= p20 x1.4 | if debt_to_assets >= p80 AND ebit_margin <= p30 x1.3
  [g01-04] EV/Sales | base constant | terms ebitda_margin -1, log_sales -0.8 | if negative_ebitda x1.6 | if no_history x1.3
  [g01-05] EV/Sales | base constant | terms gross_margin +0.8, rnd_intensity +0.7, sales_growth_1y +0.7, log_assets -0.6
  [g01-06] EV/Sales | base constant | terms log_sales -1, peer_iqr +0.5, net_margin -0.6 | if loss_making AND log_sales <= p30 x1.5 | if debt_to_assets >= p80 x1.3
  [g02-01] EV/EBITDA | base constant | terms log_sales -0.8, ebitda_margin -0.6, rnd_intensity +0.5, sales_growth_1y +0.4 | if loss_making x1.3
  [g02-02] EV/EBITDA | base constant | terms capex_intensity +0.5, ebit_margin -0.7, log_sales -0.7 | if net_debt_to_ebitda >= p85 x1.25
  [g02-03] EV/EBITDA | base constant | terms log_sales -0.8, net_margin -0.5 | if sales_growth_1y >= p85 x1.3 | if sales_growth_1y <= p10 x1.3
  [g02-04] EV/Sales | base constant | terms n_peers -0.6, log_sales -0.4, peer_range +0.3 | if negative_ebitda x1.3
  [g02-05] EV/Sales | base constant | terms gross_margin +0.6, ebitda_margin -0.6, log_sales -0.3
  [g02-06] EV/Sales | base constant | terms log_assets -0.3 | if sales_growth_1y >= p85 x1.35 | if sales_growth_1y <= p10 x1.3 | if no_history x1.25

PROPOSALS
  (0) ebitda_mismeasures_economic_earnings_both_ways
      rule: EV/EBITDA | base constant | terms log_sales -0.7, ebitda_margin -0.6, rnd_intensity +0.5, capex_intensity +0.4 | if loss_making x1.3
      mechanism: EBITDA is a poor proxy for economic earnings in two opposite directions. In R&D-heavy firms it is understated because investment is expensed, so EV rests on growth options trailing EBITDA cannot see. In capital-intensive firms it is overstated because it comes before the reinvestment needed to sustain it, so the same EBITDA supports very different EVs depending on each firm's maintenance capex. Both channels add to the thin-margin and small-size noise found earlier, and loss-making firms carry below-EBITDA charges the multiple ignores.
      prediction: EV/EBITDA interval score below 2.540 (best earlier rule); coverage of highest_rnd_20pct stays near 80% and capital-intensive firms are no longer over-covered by a constant band.

  (1) opex_headroom_with_leverage_damping_ebitda
      rule: EV/EBITDA | base constant | terms gross_margin +0.6, ebitda_margin -0.7, log_sales -0.8, debt_to_assets -0.3 | if loss_making x1.3
      mechanism: A firm with a high gross margin but a low EBITDA margin has EBITDA depressed by discretionary opex (selling, marketing, R&D) that may later be cut, so the market values a normalized margin far above current EBITDA, and investors disagree on how much. A firm whose thin EBITDA comes from a thin gross margin has no such headroom and its multiple is pinned by its peers. Separately, in heavily indebted firms most of EV is debt carried near face value, so the uncertain equity is a smaller share of EV and log EV errors shrink.
      prediction: EV/EBITDA interval score below the constant band's 2.735 and below 2.60; firms with debt_to_assets above the 80th percentile get narrower ranges and still reach about 80% coverage.

  (2) transition_firms_ushape_plus_scalability_ebitda
      rule: EV/EBITDA | base constant | terms log_sales -0.8, ebitda_margin -0.6, rnd_intensity +0.4 | if sales_growth_1y >= p85 x1.3 | if sales_growth_1y <= p10 x1.3 | if loss_making x1.25 | if no_history x1.2
      mechanism: Trailing EBITDA is a poor run-rate when the firm is in transition: after an acquisition or explosive ramp (top growth tail), or after a demand collapse or divestiture (bottom tail), and in newly listed firms with no history, the market prices forward earnings that differ sharply from the trailing number in either direction. A linear growth term misses the collapse tail, so both tails get their own condition, on top of the thin-margin, small-size and R&D-expensing channels.
      prediction: EV/EBITDA interval score below 2.540; fastest_growing_20pct and loss_making coverage both within 77-82%.

  (3) weak_anchor_plus_runrate_break_sales
      rule: EV/Sales | base constant | terms n_peers -0.6, peer_range +0.3, log_assets -0.3 | if sales_growth_1y >= p85 x1.3 | if sales_growth_1y <= p10 x1.3 | if no_history x1.2 | if negative_ebitda x1.25
      mechanism: EV/Sales comps fail for two independent reasons. The anchor is weak when the 2-digit SIC sector is thin or its peers disagree, because the nearest peers come from different business models. And trailing sales are not the revenue run-rate after a big acquisition, divestiture, demand collapse or ramp, or for new listings, so the multiple departs from peers in both directions. Earlier rules each fixed one channel; combining them should cover both under-covered groups without heavy size weights that over-cover small firms.
      prediction: EV/Sales interval score below 4.079 (best earlier rule); fallback_or_few_peers and fastest_growing_20pct coverage both at least 78%.

  (4) opex_headroom_in_thin_sectors_sales
      rule: EV/Sales | base constant | terms gross_margin +0.5, ebitda_margin -0.4, n_peers -0.5, log_sales -0.3 | if negative_ebitda x1.25
      mechanism: A high-gross-margin, low-EBITDA-margin firm is valued on whether its discretionary opex will scale down into mature margins, a judgment that varies widely, while a low-gross-margin firm's revenue multiple is pinned by structurally thin margins. This headroom effect matters most where the peer anchor is already weak because the sector is thin, so it is combined with the peer-count channel, and firms with negative EBITDA have no current margin anchor at all.
      prediction: EV/Sales interval score below the constant band's 4.233 and below 4.10; highest_rnd_20pct coverage no higher than 83% (less over-coverage than g02-05).

  (5) leverage_damps_ev_intangibles_widen_sales
      rule: EV/Sales | base constant | terms debt_to_assets -0.5, rnd_intensity +0.4, n_peers -0.5, log_sales -0.3 | if negative_ebitda x1.3
      mechanism: EV is equity plus net debt, and debt is close to a fixed claim, so in heavily indebted firms the uncertain equity is a smaller share of EV and the log error of an EV-based comp shrinks; earlier rules that widened ranges for high leverage scored worse, which fits this. R&D-intensive firms are the opposite: almost all their EV is equity priced on intangible growth options that revenue barely measures. Thin sectors weaken the peer anchor for everyone.
      prediction: EV/Sales interval score below the constant band's 4.233; firms with debt_to_assets above the 80th percentile get ranges at least 15% narrower than the median firm and still reach about 80% coverage.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}
