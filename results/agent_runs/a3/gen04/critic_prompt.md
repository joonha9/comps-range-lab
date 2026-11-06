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
  [g01-01] EV/EBITDA | base constant | terms log_sales -1, ebitda_margin -1 | if loss_making x1.4
  [g01-02] EV/EBITDA | base constant | terms rnd_intensity +0.8, sales_growth_1y +0.6, gross_margin +0.5, log_assets -0.6 | if no_history x1.3
  [g01-03] EV/EBITDA | base constant | terms net_debt_to_ebitda +0.6, log_sales -0.8 | if debt_to_assets >= p80 AND loss_making x1.5 | if peer_iqr >= p80 x1.3
  [g01-04] EV/Sales | base constant | terms log_sales -1, rnd_intensity +0.7 | if negative_ebitda x1.8 | if loss_making x1.2
  [g01-05] EV/Sales | base constant | terms gross_margin +0.8, sales_growth_1y +0.6, log_assets -0.8 | if loss_making AND rnd_intensity >= p80 x1.5
  [g01-06] EV/Sales | base constant | terms peer_range +0.6, log_sales -0.7 | if ebitda_margin <= p15 x1.6 | if no_history x1.3
  [g02-01] EV/EBITDA | base constant | terms log_sales -0.9, ebitda_margin -0.7 | if sales_growth_1y <= p10 x1.35 | if sales_growth_1y >= p90 x1.35 | if loss_making x1.3
  [g02-02] EV/EBITDA | base constant | terms ebitda_margin -0.9, capex_intensity +0.6, log_assets -0.8 | if net_margin <= p10 x1.4
  [g02-03] EV/EBITDA | base constant | terms log_sales -0.8, ebitda_margin -0.8, rnd_intensity +0.5, sales_growth_1y +0.4 | if loss_making x1.3
  [g02-04] EV/Sales | base constant | terms gross_margin +0.6, ebitda_margin -0.6, peer_range +0.4, log_sales -0.5 | if no_history x1.3
  [g02-05] EV/Sales | base constant | terms peer_range +0.6, log_sales -0.5 | if n_peers <= p10 x1.5 | if ebitda_margin <= p15 x1.5
  [g02-06] EV/Sales | base constant | terms asset_turnover -0.7, log_sales -0.6, sales_growth_1y +0.3 | if negative_ebitda x1.4 | if no_history x1.3
  [g03-01] EV/EBITDA | base constant | terms log_sales -0.8, ebit_margin -0.6 | if ebitda_margin >= p40 AND ebit_margin <= p25 x1.4 | if net_margin <= p10 x1.25
  [g03-02] EV/EBITDA | base constant | terms asset_turnover +0.7, log_assets -0.9 | if roic >= p90 x1.3 | if roic <= p10 x1.3
  [g03-03] EV/EBITDA | base constant | terms log_sales -0.8, capex_intensity +0.4 | if sales_growth_1y <= p20 AND capex_intensity >= p60 x1.5 | if ebitda_margin <= p15 x1.4
  [g03-04] EV/Sales | base constant | terms log_sales -0.6, peer_range +0.5 | if loss_making AND sales_growth_1y >= p70 x1.5 | if sales_growth_1y <= p10 x1.3
  [g03-05] EV/Sales | base constant | terms log_assets -0.6, peer_range +0.5 | if asset_turnover <= p10 x1.4 | if asset_turnover >= p90 x1.25 | if ebitda_margin <= p15 x1.4
  [g03-06] EV/Sales | base constant | terms log_sales -0.6, peer_range +0.5, ebitda_margin -0.4 | if net_debt_to_ebitda >= p85 x1.35 | if debt_to_assets >= p90 AND loss_making x1.3

PROPOSALS
  (0) g04-ebitda-debt-anchor
      rule: EV/EBITDA | base constant | terms log_sales -0.8, ebitda_margin -0.7, debt_to_assets -0.6 | if loss_making x1.3
      mechanism: Enterprise value is debt plus equity, and the debt part is close to book value and moves little, while the equity part carries all the market's disagreement about the firm. The larger the debt share of the capital structure, the smaller the proportional error in EV when equity is mispriced relative to peers; an all-equity firm's EV moves one-for-one with equity sentiment. So, holding size and margin fixed, highly levered firms should get narrower EV/EBITDA ranges, not wider ones (consistent with g01-03, where a positive leverage weight did worse than the constant band).
      prediction: Interval score below g01-01 (2.581) and the constant band (2.735); the fitted direction holds, i.e. flipping debt_to_assets to a positive weight would score worse; coverage of the top debt_to_assets quintile stays near 80% despite its narrower ranges.

  (1) g04-ebitda-return-fade
      rule: EV/EBITDA | base constant | terms log_sales -0.8, ebitda_margin -0.6 | if roic <= p10 x1.4 | if roic >= p90 x1.3
      mechanism: A sector's peer multiple embeds the sector's typical return on invested capital and the typical speed at which that return fades. A firm earning far above the norm has a value that depends on how long its competitive advantage lasts, which investors disagree on, and a firm earning far below its cost of capital is valued on restructuring, asset sales or takeover prospects rather than on its EBITDA. Both tails of ROIC therefore transfer the peer median EV/EBITDA poorly, while firms with ordinary returns are priced close to it.
      prediction: Interval score below the constant band (2.735) and below g01-01 (2.581); constant-band coverage of the top and bottom ROIC deciles is below 75%, and under this rule both are within 5 points of 80%.

  (2) g04-ebitda-trend-break
      rule: EV/EBITDA | base constant | terms log_sales -0.8, ebitda_margin -0.7 | if sales_growth_1y <= p20 AND sales_growth_3y >= p50 x1.5 | if sales_growth_1y >= p80 AND sales_growth_3y <= p50 x1.4 | if loss_making x1.25
      mechanism: The market capitalizes a firm's sustainable earnings run rate, not one year's EBITDA. When last year's sales growth breaks sharply from the firm's own 3-year trend (a sudden drop after steady growth, or a spike after stagnation), investors disagree on whether the new level is permanent or transitory, so the reported EBITDA is a noisy base for the peer multiple. A firm growing in line with its own history gives a reliable run rate, so its range can be narrow.
      prediction: Interval score below the constant band (2.735) and at least as good as g01-01 (2.581); the gain is concentrated in FY2018-2019, the years when sales_growth_3y is available, and the flagged firm-years have constant-band coverage below 72%.

  (3) g04-sales-debt-anchor
      rule: EV/Sales | base constant | terms debt_to_assets -0.7, log_sales -0.6, peer_range +0.5 | if ebitda_margin <= p15 x1.5
      mechanism: EV is book-like debt plus volatile equity, so the share of EV that comes from debt dampens the proportional error of any EV-based multiple; this matters even more for EV/Sales, where errors are large and driven by equity investors' views of future margins. Highly levered firms (utilities, pipelines, telecom, LBO-style capital structures) have EVs pinned partly by contractual claims, so the same peer sales multiple misses them by less in logs than it misses all-equity firms. Wide peer dispersion and depressed EBITDA margins still widen the range, as in earlier rules.
      prediction: Interval score below the constant band (4.233) and at least as good as g01-06 (4.143); a negative debt_to_assets weight beats a positive one, and the top debt_to_assets quintile keeps coverage near 80% with a median range narrower than the overall median.

  (4) g04-sales-margin-boundary
      rule: EV/Sales | base constant | terms peer_range +0.5, log_sales -0.6 | if ebitda_margin <= p10 x1.6 | if ebitda_margin >= p90 x1.35 | if n_peers <= p10 x1.4
      mechanism: Peers are chosen as the nearest firms on size and EBITDA margin, but a target with an extreme margin has nearly all its candidate peers on one side, so the median peer's margin is systematically different from the target's and the peer EV/Sales is biased by an amount that varies firm to firm. This boundary effect hits both tails: very-low-margin firms (where value has no earnings base) and very-high-margin firms (where EV/Sales is high and sensitive to how long the margin lasts). Earlier rules widened only the low tail; this tests whether the high tail is also undercovered.
      prediction: Interval score below the constant band (4.233) and below g02-05 (4.096); the top EBITDA-margin decile has constant-band coverage below 76% and moves to within 4 points of 80% under this rule.

  (5) g04-sales-trend-break
      rule: EV/Sales | base constant | terms peer_range +0.5, log_sales -0.6 | if sales_growth_1y <= p20 AND sales_growth_3y >= p60 x1.5 | if sales_growth_1y >= p80 AND sales_growth_3y <= p40 x1.4 | if ebitda_margin <= p15 x1.5
      mechanism: EV/Sales capitalizes expected future revenue, so the multiple depends on what investors take as the firm's revenue trajectory. When the latest year's growth breaks sharply from the 3-year trend, investors split on whether the break is a new run rate or a one-off, and the same current sales are worth very different amounts; a firm growing in line with its own history has a clear trajectory that peers' multiples price consistently. This differs from g03-04's one-sided low-growth flag because it conditions on the firm's own history, not on growth level alone.
      prediction: Interval score below the constant band (4.233) and at least as good as g01-06 (4.143); the improvement over g01-06 comes mainly from FY2018-2019, when sales_growth_3y is available, and the flagged firm-years have constant-band coverage below 72%.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}
