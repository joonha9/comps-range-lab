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
  [g02-01] EV/EBITDA | base constant | terms capex_intensity +0.7, ebitda_margin -0.7 | if loss_making x1.3
  [g02-02] EV/EBITDA | base constant | terms log_assets -0.7 | if sales_growth_1y >= p80 x1.4 | if sales_growth_1y <= p10 x1.3 | if no_history x1.3
  [g02-03] EV/EBITDA | base constant | terms debt_to_assets -0.7, log_sales -0.7 | if loss_making AND debt_to_assets <= p50 x1.4
  [g02-04] EV/Sales | base constant | terms debt_to_assets -0.6, ebitda_margin -0.5 | if negative_ebitda x1.3
  [g02-05] EV/Sales | base constant | terms gross_margin +0.5 | if sales_growth_1y >= p80 x1.5 | if sales_growth_1y <= p15 x1.3 | if no_history x1.3
  [g02-06] EV/Sales | base constant | terms peer_range +0.4, n_peers -0.6, log_sales -0.5
  [g03-01] EV/EBITDA | base constant | terms net_debt_to_ebitda -0.8, log_sales -0.6 | if net_debt_to_ebitda <= p10 x1.3 | if loss_making x1.3
  [g03-02] EV/EBITDA | base constant | terms ebitda_margin -0.7, log_assets -0.6 | if sales_growth_1y >= p85 x1.3 | if sales_growth_1y <= p10 x1.3
  [g03-03] EV/EBITDA | base constant | terms gross_margin +0.5, ebitda_margin -0.6, log_sales -0.5 | if gross_margin >= p70 AND ebitda_margin <= p30 x1.3
  [g03-04] EV/Sales | base constant | terms debt_to_assets -0.6, log_sales -0.4 | if debt_to_assets <= p25 AND rnd_intensity >= p70 x1.3 | if negative_ebitda x1.3
  [g03-05] EV/Sales | base constant | terms n_peers -0.5, log_sales -0.5 | if ebitda_margin <= p10 x1.4 | if ebitda_margin >= p90 x1.2
  [g03-06] EV/Sales | base constant | terms log_sales -0.5 | if loss_making AND sales_growth_1y >= p70 x1.5 | if negative_ebitda x1.2
  [g04-01] EV/EBITDA | base constant | terms net_debt_to_ebitda -0.7 | if roic >= p85 x1.3 | if roic <= p15 x1.4
  [g04-02] EV/EBITDA | base constant | terms asset_turnover +0.6, debt_to_assets -0.5 | if gross_margin >= p70 AND asset_turnover >= p70 x1.3
  [g04-03] EV/EBITDA | base constant | terms ebit_margin -0.6 | if net_debt_to_ebitda <= p15 AND log_sales <= p40 x1.6 | if net_debt_to_ebitda >= p75 x0.75
  [g04-04] EV/Sales | base constant | terms gross_margin +0.6, ebitda_margin -0.5 | if gross_margin >= p70 AND ebitda_margin <= p30 x1.3 | if negative_ebitda x1.3
  [g04-05] EV/Sales | base constant | terms debt_to_assets -0.5 | if asset_turnover <= p15 x1.4 | if asset_turnover >= p85 x1.25
  [g04-06] EV/Sales | base constant | terms sales_growth_1y +0.4 | if sales_growth_1y >= p70 AND roic >= p70 x1.4 | if roic <= p10 x1.3

PROPOSALS
  (0) ebitda_yield_on_assets
      rule: EV/EBITDA | base constant | terms ebitda_margin -0.6, asset_turnover -0.5, log_sales -0.4 | if ebitda_margin <= p30 AND asset_turnover <= p30 x1.3
      mechanism: EBITDA divided by total assets equals EBITDA margin times asset turnover. When EBITDA is only a small yield on a large asset base, the market values the firm on what its assets are worth (replacement, liquidation or sum-of-parts value of land, reserves, plants or real estate) rather than on capitalized EBITDA. That makes EV/EBITDA high and dependent on asset values that peers matched on size and EBITDA margin cannot reveal. Smaller firms add idiosyncratic risk on top, because their asset values and earnings are less diversified.
      prediction: Interval score below the constant band's 2.735 and below g01-01's 2.590 (which has margin and size but no turnover); firms in the bottom 30% on both EBITDA margin and asset turnover get wider ranges, and constant-band under-coverage of the smallest 20% shrinks toward 80%.

  (1) debt_funded_acquisition_year
      rule: EV/EBITDA | base constant | terms net_debt_to_ebitda -0.7, log_sales -0.5 | if sales_growth_1y >= p85 AND net_debt_to_ebitda >= p60 x1.5
      mechanism: Net debt is carried at book value, so it is the known part of EV, and more net debt relative to EBITDA usually narrows the error. The exception is the year of a debt-funded acquisition: the year-end balance sheet holds all of the acquisition debt and the June EV reflects the whole combined firm, while trailing EBITDA includes the target for only part of the year. A large sales jump together with high net debt/EBITDA marks this case. Here the trailing multiple is distorted by a firm-specific amount that depends on deal timing and synergies, which peers cannot reveal.
      prediction: Interval score below the constant band's 2.735 and at or below g03-01's 2.535; coverage of fastest_growing_20pct rises toward 80%, and firms that are both high-growth and high-leverage show larger |e| than other high-leverage firms.

  (2) depreciation_amortization_wedge
      rule: EV/EBITDA | base constant | terms ebit_margin -0.6 | if ebitda_margin >= p50 AND ebit_margin <= p30 x1.4 | if loss_making x1.3
      mechanism: The market capitalizes something between EBITDA and EBIT. When D&A takes a large share of EBITDA (EBITDA margin above median but EBIT margin in the bottom 30%), it matters a great deal whether that D&A is real economic depreciation needing reinvestment or non-cash amortization of acquired intangibles, and the answer is firm-specific. Peers matched on EBITDA margin can carry very different D&A burdens, so the peer EV/EBITDA is a weak anchor. A thin EBIT margin and a net loss despite positive EBITDA are further signs that below-EBITDA charges absorb the earnings base.
      prediction: Interval score below the constant band's 2.735; firms with a high EBITDA margin but a low EBIT margin have larger |e| than firms with a similar EBITDA margin and a normal EBIT margin, and loss_making coverage rises from 68% toward 80%.

  (3) pre_commercial_revenue
      rule: EV/Sales | base constant | terms debt_to_assets -0.5, log_sales -0.4 | if negative_ebitda AND log_sales <= p25 x1.6 | if negative_ebitda AND rnd_intensity >= p80 x1.3
      mechanism: When a firm's sales are both tiny and loss-generating, current revenue is not what drives its value. EV reflects a pipeline, licence or technology whose worth is unrelated to this year's sales, so a revenue multiple applied to them can be off by an order of magnitude in either direction. R&D-heavy loss-makers are the clearest case. In contrast, debt is carried at book value and anchors part of EV, so debt-financed firms have damped EV/Sales errors.
      prediction: Interval score below the constant band's 4.233; small negative-EBITDA firms get the widest ranges and have the largest |e|, and coverage of smallest_20pct and loss_making approaches 80% without the over-coverage (92%) that g01-04's blanket size term produced.

  (4) sustained_growth_unproven_margin
      rule: EV/Sales | base constant | terms debt_to_assets -0.5, sales_growth_3y +0.5 | if sales_growth_3y >= p80 AND ebitda_margin <= p40 x1.5
      mechanism: A firm that has grown fast for three years and still has a thin margin is valued on how long the growth runway lasts and what margin it will eventually reach. Both beliefs vary widely across firms, and peers matched on current size and margin do not reveal them. Multi-year growth separates a durable growth franchise from a one-year blip that the market looks through. Debt is carried at book value and damps EV errors.
      prediction: Interval score below the constant band's 4.233 and below g02-05's 4.250 (which used only 1-year growth); in FY2018-2019, firms in the top 20% on 3-year growth with an EBITDA margin in the bottom 40% have clearly larger |e| than firms in the top 20% on 1-year growth alone.

  (5) capacity_build_out
      rule: EV/Sales | base constant | terms debt_to_assets -0.6 | if capex_intensity >= p85 AND ebitda_margin <= p40 x1.5 | if capex_intensity >= p85 AND sales_growth_1y >= p70 x1.3
      mechanism: A firm spending far more on capital expenditure than its current sales or EBITDA support is building capacity, such as plants, networks, wells or fleets. The market values it on the sales that capacity will produce, so trailing sales understate the revenue base by a firm-specific amount that depends on project timing and execution. Peers at a steady state cannot reveal this. Rapid sales growth alongside heavy capex marks capacity already coming online, and debt carried at book value anchors part of EV.
      prediction: Interval score below the constant band's 4.233; firms in the top 15% on capex intensity with an EBITDA margin in the bottom 40% have larger |e| than other firms, while asset-heavy high-margin firms such as utilities keep narrow ranges.

Reply with ONLY this JSON, no other text:
{"verdicts": [{"index": 0, "verdict": "approve" or "reject", "reason": "..."}]}
