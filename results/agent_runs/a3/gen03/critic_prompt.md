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

PROPOSALS
  (0) g03-01 D&A wedge (EBITDA far above EBIT)
      rule: EV/EBITDA | base constant | terms log_sales -0.8, ebit_margin -0.6 | if ebitda_margin >= p40 AND ebit_margin <= p25 x1.4 | if net_margin <= p10 x1.25
      mechanism: When EBITDA is healthy but EBIT is thin, a large share of EBITDA is consumed by depreciation and amortization (heavy maintenance capex or amortization of acquired intangibles), and investors disagree on how much of that D&A is a real recurring cost; some value such firms on EBITDA, others on EBIT or free cash flow, so the peer median EV/EBITDA transfers poorly. Small firms add idiosyncratic risk and thin coverage on top of this accounting wedge.
      prediction: Interval score below the constant band's 2.735 and at or below 2.60; firms meeting the wedge condition (ebitda_margin >= p40 and ebit_margin <= p25) have larger |e| than other firms of similar size.

  (1) g03-02 Asset-light value without a tangible anchor
      rule: EV/EBITDA | base constant | terms asset_turnover +0.7, log_assets -0.9 | if roic >= p90 x1.3 | if roic <= p10 x1.3
      mechanism: For asset-heavy firms (low sales/assets, e.g. utilities, pipelines, lessors) enterprise value is anchored by the replacement cost and regulated or contracted returns of a large tangible asset base, so EV/EBITDA clusters tightly within the sector. Asset-light firms with very high returns on capital are valued on the length of their reinvestment runway and franchise durability, which current EBITDA does not reveal, so their multiples scatter widely around the peer median.
      prediction: Interval score below the constant band's 2.735; coverage of the lowest-asset-turnover quintile above 85% (they get narrow ranges and still are covered) and interval score improvement concentrated in high-turnover firms.

  (2) g03-03 Cyclical trough in capital-intensive firms
      rule: EV/EBITDA | base constant | terms log_sales -0.8, capex_intensity +0.4 | if sales_growth_1y <= p20 AND capex_intensity >= p60 x1.5 | if ebitda_margin <= p15 x1.4
      mechanism: Capital-intensive cyclical firms (energy, materials, industrial equipment) whose sales just fell are reporting trough EBITDA, and the market capitalizes mid-cycle earnings, so their EV/EBITDA spikes by an amount that depends on how deep and temporary each firm's trough is; peers in the same SIC code are at different points of recovery. The same operating leverage that makes their EBITDA swing also makes thin-margin firms' ratios unstable.
      prediction: Interval score below the constant band's 2.735; firms meeting the trough condition (sales_growth_1y <= p20 and capex_intensity >= p60) have constant-band coverage below 70% and coverage near 80% under this rule.

  (3) g03-04 Cash-burning growth and shrinking businesses
      rule: EV/Sales | base constant | terms log_sales -0.6, peer_range +0.5 | if loss_making AND sales_growth_1y >= p70 x1.5 | if sales_growth_1y <= p10 x1.3
      mechanism: A loss-making firm that is growing fast is valued on the eventual margin of a business it has not yet built, so the same revenue can be worth wildly different amounts depending on investors' belief in its path to profitability; a shrinking firm is valued on how fast and how far the decline goes, which revenue alone does not reveal. Small size and wide peer dispersion add to both.
      prediction: Interval score below the constant band's 4.233 and below 4.15; coverage of loss-making fast growers (loss_making and sales_growth_1y >= p70) near 80% versus below 72% under the constant band.

  (4) g03-05 Capital-intensity mismatch at turnover extremes
      rule: EV/Sales | base constant | terms log_assets -0.6, peer_range +0.5 | if asset_turnover <= p10 x1.4 | if asset_turnover >= p90 x1.25 | if ebitda_margin <= p15 x1.4
      mechanism: An EV/Sales multiple implicitly assumes the target needs as much capital per dollar of sales as its peers; at extreme asset turnover (lessors and asset owners at the bottom, distributors and services at the top) small differences in business mix within the same SIC code (owner vs operator, wholesale vs retail) translate into large proportional differences in value per dollar of sales. Firms with small asset bases also have little tangible value to anchor EV.
      prediction: Interval score below the constant band's 4.233; firms in the bottom and top deciles of asset_turnover have larger |e| than mid-turnover firms, and their coverage under this rule is within 3 points of 80%.

  (5) g03-06 Debt-heavy enterprise value
      rule: EV/Sales | base constant | terms log_sales -0.6, peer_range +0.5, ebitda_margin -0.4 | if net_debt_to_ebitda >= p85 x1.35 | if debt_to_assets >= p90 AND loss_making x1.3
      mechanism: When net debt is large relative to EBITDA, debt is a big share of enterprise value and is measured at book while it may trade well below par, and the equity of a stressed firm behaves like an option; both make EV per dollar of sales depart from healthy peers in either direction. Highly levered loss-makers are closest to distress, where restructuring outcomes dominate value.
      prediction: Interval score below the constant band's 4.233; firms with net_debt_to_ebitda >= p85 have larger |e| than the rest, and coverage of the loss_making group rises from 72% toward 80%.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}
