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
  [g02-01] EV/EBITDA | base constant | terms log_sales -0.8, rnd_intensity +0.5, sales_growth_1y +0.4 | if loss_making x1.4
  [g02-02] EV/EBITDA | base constant | terms ebitda_margin -0.8, net_debt_to_ebitda +0.5, log_assets -0.6 | if no_history x1.3
  [g02-03] EV/EBITDA | base constant | terms log_sales -0.7, gross_margin +0.5 | if sales_growth_1y >= p85 x1.4 | if sales_growth_1y <= p10 x1.3
  [g02-04] EV/Sales | base constant | terms ebitda_margin -1, log_sales -0.6, rnd_intensity +0.5 | if negative_ebitda x1.5
  [g02-05] EV/Sales | base constant | terms gross_margin +0.8, sales_growth_1y +0.6, log_assets -0.6 | if loss_making x1.3
  [g02-06] EV/Sales | base constant | terms peer_iqr +0.4, log_sales -0.8 | if negative_ebitda x1.4 | if n_peers <= p10 x1.3 | if no_history x1.3
  [g03-01] EV/EBITDA | base constant | terms log_assets -0.8, debt_to_assets -0.5, capex_intensity -0.3 | if loss_making x1.4 | if sales_growth_1y >= p85 x1.3
  [g03-02] EV/EBITDA | base constant | terms log_sales -0.8, rnd_intensity +0.4 | if roic <= p10 x1.4 | if net_margin <= p10 x1.3 | if sales_growth_1y >= p85 x1.3
  [g03-03] EV/EBITDA | base constant | terms peer_iqr +0.5, log_sales -0.8, gross_margin +0.4 | if loss_making x1.4
  [g03-04] EV/Sales | base constant | terms log_sales -0.8, rnd_intensity +0.5, peer_iqr +0.4 | if negative_ebitda x1.5 | if sales_growth_1y >= p90 x1.3
  [g03-05] EV/Sales | base constant | terms log_sales -0.7, debt_to_assets -0.6, peer_iqr +0.4 | if negative_ebitda x1.5 | if no_history x1.3
  [g03-06] EV/Sales | base constant | terms log_sales -0.9, sales_growth_1y +0.3 | if negative_ebitda x1.6 | if net_margin <= p10 x1.3 | if no_history x1.3
  [g04-01] EV/EBITDA | base constant | terms gross_margin +0.6, ebitda_margin -0.6, log_sales -0.7 | if rnd_intensity >= p80 x1.2
  [g04-02] EV/EBITDA | base constant | terms log_sales -0.8, gross_margin +0.3 | if sales_growth_1y >= p80 AND ebit_margin <= p30 x1.5 | if sales_growth_1y <= p15 AND ebit_margin <= p30 x1.3 | if loss_making x1.2
  [g04-03] EV/EBITDA | base constant | terms log_assets -0.8, asset_turnover +0.3 | if roic <= p10 x1.4 | if roic >= p90 x1.3 | if roe >= p95 x1.2
  [g04-04] EV/Sales | base constant | terms log_sales -0.8 | if ebitda_margin <= p10 x1.5 | if ebitda_margin >= p90 x1.3 | if gross_margin >= p85 x1.2 | if n_peers <= p10 x1.2
  [g04-05] EV/Sales | base constant | terms log_sales -0.8, gross_margin +0.3 | if rnd_intensity >= p80 AND loss_making x1.6 | if sales_growth_1y >= p85 AND negative_ebitda x1.4 | if no_history x1.3
  [g04-06] EV/Sales | base constant | terms log_sales -0.7, peer_iqr +0.3 | if roic >= p50 AND sales_growth_1y <= p60 x0.7 | if loss_making x1.4

PROPOSALS
  (0) g05-ebitda-da-wedge
      rule: EV/EBITDA | base constant | terms ebit_margin -0.6, ebitda_margin +0.4, log_sales -0.8 | if loss_making x1.3
      mechanism: EBITDA adds back depreciation and amortization, so when D&A is a large slice of EBITDA (high EBITDA margin but low EBIT margin) the multiple depends on whether that D&A is real maintenance capex (the market then capitalizes the much smaller EBIT) or non-cash amortization of acquired intangibles (the market capitalizes EBITDA). Peers matched on size and EBITDA margin do not share the target's D&A burden, so these firms' EV/EBITDA floats away from the peer median; loss-makers are the extreme case where costs below EBITDA swamp it.
      prediction: Interval score below the constant band's (2.735) and below 2.60; firms in the top quintile of EBITDA margin minus EBIT margin get wider ranges and coverage for loss_making firms rises above 75%.

  (1) g05-ebitda-capital-cycle-trough
      rule: EV/EBITDA | base constant | terms log_assets -0.8, rnd_intensity +0.3 | if capex_intensity >= p80 AND roic <= p25 x1.5 | if capex_intensity >= p80 AND sales_growth_1y <= p20 x1.3 | if net_debt_to_ebitda >= p90 x1.2
      mechanism: Capital-intensive cyclical firms (energy, materials, heavy industry) are priced on mid-cycle earnings, so in a year when heavy capex coincides with low returns or falling sales the current EBITDA is a trough figure and the EV/EBITDA multiple spikes by an amount that depends on how far the firm is from its own normal earnings, which peers at different cycle points cannot reveal. Very high net leverage in such firms adds a distress component to EV that is not a going-concern multiple.
      prediction: Interval score below the constant band's (2.735); firms with capex_intensity >= p80 and roic <= p25 have constant-band coverage below 70% and are covered near 80% under this rule.

  (2) g05-ebitda-cash-residual-ev
      rule: EV/EBITDA | base constant | terms log_sales -0.8, net_debt_to_ebitda -0.4 | if net_debt_to_ebitda <= p10 x1.3 | if net_debt_to_ebitda >= p95 x1.3 | if loss_making x1.3
      mechanism: Enterprise value is market capitalization minus net cash, so for a firm sitting on cash that is large relative to its EBITDA, EV is a small residual of a volatile equity value and any mispricing of the equity is magnified in log EV; such cash-rich firms are also typically growth or intangible businesses whose equity carries option value. At the other end, net debt far above EBITDA puts EV in a distress regime, while firms with moderate leverage have much of EV pinned to debt at face value and trade near peers.
      prediction: Interval score below the constant band's (2.735); the bottom decile of net_debt_to_ebitda (largest net cash) shows constant-band coverage below 75% and is covered near 80% here.

  (3) g05-sales-unit-economics-without-scale
      rule: EV/Sales | base constant | terms log_sales -0.8, peer_iqr +0.3 | if gross_margin >= p70 AND ebit_margin <= p20 x1.5 | if negative_ebitda x1.3 | if no_history x1.2
      mechanism: A high gross margin with a low operating margin means the firm has proven unit economics but has not yet reached the scale at which fixed operating costs are covered, so the market prices a terminal operating margin that could lie anywhere between today's EBIT margin and the gross margin. Each dollar of sales can therefore be worth very different amounts across such firms, and the peer median sales multiple is an arbitrary anchor; firms whose gross and operating margins are both settled have a known conversion of sales into value.
      prediction: Interval score below the constant band's (4.233) and below 4.15; firms with gross_margin >= p70 and ebit_margin <= p20 are covered near 80% rather than well below.

  (4) g05-sales-asset-base-mismatch
      rule: EV/Sales | base constant | terms log_sales -0.7, asset_turnover -0.4 | if asset_turnover >= p90 x1.3 | if negative_ebitda x1.5 | if n_peers <= p10 x1.2
      mechanism: EV per dollar of sales scales with the capital needed to produce that dollar, but peers are matched on size and EBITDA margin, not on capital intensity. When assets are large relative to sales (low asset turnover: reserves, networks, real estate, licenses) value is driven by how the market prices that asset base rather than the revenue stream, so the sales multiple varies widely; at very high turnover, sales are largely pass-through and tiny margin differences move value per sales a lot, so both tails are poorly anchored by the peer median.
      prediction: Interval score below the constant band's (4.233); the bottom decile of asset_turnover receives ranges at least 1.3x the median width and its coverage is near 80%.

  (5) g05-sales-investment-phase
      rule: EV/Sales | base constant | terms log_sales -0.8, peer_iqr +0.3 | if capex_intensity >= p90 x1.4 | if capex_intensity >= p75 AND sales_growth_1y <= p20 x1.3 | if negative_ebitda x1.3
      mechanism: A firm spending heavily on capex relative to sales is building capacity whose output is not yet in current revenue (mines, wells, plants, network build-outs), so EV prices future production and current sales understate the value base by an amount specific to the project; when such heavy investment coincides with falling sales the firm may instead hold stranded, overbuilt capacity priced on impairment risk. In both cases current sales are a poor value driver and the peer median sales multiple misses widely, while firms with ordinary capex are priced on the revenue they already generate.
      prediction: Interval score below the constant band's (4.233); firms with capex_intensity >= p90 have constant-band coverage below 75% and are covered near 80% under this rule.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}
