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
  [g04-01] EV/EBITDA | base constant | terms log_sales -0.8, ebitda_margin -0.7, debt_to_assets -0.6 | if loss_making x1.3
  [g04-02] EV/EBITDA | base constant | terms log_sales -0.8, ebitda_margin -0.6 | if roic <= p10 x1.4 | if roic >= p90 x1.3
  [g04-03] EV/EBITDA | base constant | terms log_sales -0.8, ebitda_margin -0.7 | if sales_growth_1y <= p20 AND sales_growth_3y >= p50 x1.5 | if sales_growth_1y >= p80 AND sales_growth_3y <= p50 x1.4 | if loss_making x1.25
  [g04-04] EV/Sales | base constant | terms debt_to_assets -0.7, log_sales -0.6, peer_range +0.5 | if ebitda_margin <= p15 x1.5
  [g04-05] EV/Sales | base constant | terms peer_range +0.5, log_sales -0.6 | if ebitda_margin <= p10 x1.6 | if ebitda_margin >= p90 x1.35 | if n_peers <= p10 x1.4
  [g04-06] EV/Sales | base constant | terms peer_range +0.5, log_sales -0.6 | if sales_growth_1y <= p20 AND sales_growth_3y >= p60 x1.5 | if sales_growth_1y >= p80 AND sales_growth_3y <= p40 x1.4 | if ebitda_margin <= p15 x1.5

PROPOSALS
  (0) g05-01 net-cash amplification (EV/EBITDA)
      rule: EV/EBITDA | base constant | terms log_sales -0.8, ebitda_margin -0.7, net_debt_to_ebitda -0.6 | if net_debt_to_ebitda <= p10 x1.3 | if loss_making x1.3
      mechanism: EV is equity plus debt minus cash, so the proportional error in EV equals the equity mispricing scaled by equity/EV. For a net-cash firm equity exceeds EV, so any disagreement about the operating business is amplified in EV; for a net-debt firm it is damped. Netting cash against debt (rather than using gross debt/assets as in g04-01) captures the cash-rich firms where EV is a residual and the peer multiple misses most in logs.
      prediction: Interval score below the constant band's 2.735 and at or below g04-01's 2.550; firms in the bottom decile of net_debt_to_ebitda (largest net cash) get wider ranges and their coverage moves closer to 80% than under the constant band.

  (1) g05-02 expensed-intangible investment (EV/EBITDA)
      rule: EV/EBITDA | base constant | terms log_sales -0.8, ebitda_margin -0.7, debt_to_assets -0.6 | if rnd_intensity >= p80 AND ebitda_margin <= p40 x1.5 | if loss_making x1.3
      mechanism: R&D is expensed, so for R&D-heavy firms reported EBITDA is net of a large discretionary investment rather than a measure of normalized operating earnings; when such a firm also has a modest EBITDA margin, the share of its true earning power hidden in R&D differs widely between firms and the peer EV/EBITDA median transfers poorly. Firms with low R&D have EBITDA close to economic earnings, so the leverage-damped, size- and margin-based band can stay narrow for them.
      prediction: Interval score below g04-01's 2.550, with highest_rnd_20pct coverage rising from 73% toward 78-80% without pushing the overall median range wider than x/2.05.

  (2) g05-03 asset-light rent durability (EV/EBITDA)
      rule: EV/EBITDA | base constant | terms log_sales -0.8, ebitda_margin -0.7, debt_to_assets -0.6 | if asset_turnover >= p70 AND roic >= p80 x1.4 | if loss_making x1.3
      mechanism: A firm that both turns its assets over quickly and earns a very high return on invested capital is earning rents on intangibles (brands, networks, software, licenses) that are not on the balance sheet; its value depends on how long those rents last, a question on which investors disagree far more than on the earnings of asset-backed firms. The conjunction isolates such rent earners, whereas either high turnover or high ROIC alone mostly flags sector membership.
      prediction: Interval score below the constant band's 2.735 and within 0.02 of g04-01's 2.550; firms meeting both the turnover and ROIC thresholds show coverage below 76% under g04-01 and near 80% under this rule.

  (3) g05-04 cash-shell residual EV (EV/Sales)
      rule: EV/Sales | base constant | terms peer_range +0.5, log_sales -0.6 | if debt_to_assets <= p20 AND loss_making x1.6 | if n_peers <= p10 x1.4
      mechanism: A loss-making firm with almost no debt is typically funded by a cash pile (biotech, early-stage tech), so its EV is market capitalization minus cash, a small residual that can approach zero; a modest change in equity value then moves EV by a large proportion and the log error against any peer sales multiple explodes. Levered or profitable firms do not have this residual structure, so their EV tracks sales more tightly.
      prediction: Interval score below g02-05's 4.096; loss-making firms with debt_to_assets in the bottom 20% get the widest ranges and the loss_making coverage stays at 79-82% while the overall median range does not widen beyond x/3.15.

  (4) g05-05 capacity build-out (EV/Sales)
      rule: EV/Sales | base constant | terms peer_range +0.5, log_sales -0.6 | if capex_intensity >= p85 x1.5 | if ebitda_margin <= p15 x1.4 | if n_peers <= p10 x1.4
      mechanism: A firm spending an unusually large share of sales on capital expenditure is building capacity whose revenue has not arrived yet (network buildouts, new plants, drilling programs), so its EV reflects the expected output of assets under construction rather than current sales; how far current sales understate future sales differs firm by firm and is not captured by the peer median sales multiple. Firms with ordinary capex intensity are at steady state, where current sales map stably to value.
      prediction: Interval score below the constant band's 4.233 and at or below 4.10; firms in the top 15% of capex_intensity show coverage near 80% rather than the low 70s.

  (5) g05-06 pass-through thin gross margin (EV/Sales)
      rule: EV/Sales | base constant | terms peer_range +0.5, log_sales -0.6 | if gross_margin <= p15 x1.4 | if ebitda_margin <= p15 x1.4 | if n_peers <= p10 x1.4
      mechanism: Firms with very thin gross margins (distributors, contractors, commodity processors) pass most revenue through to suppliers, so value is a small multiple of a thin spread and EV/Sales is roughly proportional to that spread; small absolute differences in gross margin between the target and its peers become large proportional differences in the right EV/Sales, so the peer median misses more in logs. This differs from the low-EBITDA-margin flag because it targets the revenue pass-through structure itself, not current losses.
      prediction: Interval score below g02-05's 4.096; firms in the bottom 15% of gross_margin show larger absolute log errors than mid-margin firms and their coverage under this rule is 78-82%.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}
