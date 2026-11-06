You are a valuation researcher. Comparable-company valuations ("comps") are reported as ranges,
and practitioners' ranges are badly calibrated. Your job is to discover short, interpretable rules
that say HOW UNCERTAIN a comps valuation is for each US non-financial firm, so its range can be
wide where comps are unreliable and narrow where they are reliable.

TASK
Propose exactly 6 NEW range rules (generation 5): 3 for EV/EBITDA and 3 for EV/Sales.
Rules are scored only on exploration years FY2016-2019. The best rule per multiple will later be
tested ONCE on later years you will never see, so prefer rules with a clear economic reason over
fragile tweaks. A practitioner should be able to read your rule and apply it by hand.

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

BENCHMARKS (exploration years)
  EV/EBITDA:
    peer 25-75% range as practitioners report it (not calibrated): interval score 3.258, coverage 40.9%, median range x/1.29
    constant band (same width for every firm): interval score 2.735, coverage 79.6%, median range x/2.10
    width proportional to peer_iqr: interval score 2.732, coverage 80.0%, median range x/2.11
    linear regression on ALL inputs (no limit on terms): interval score 2.448, coverage 79.9%, median range x/1.94
    gradient-boosted trees on all inputs (black box): interval score 2.219, coverage 79.9%, median range x/1.90
    coverage of the constant band by firm type: loss_making 68%, smallest_20pct 63%, fastest_growing_20pct 70%, highest_rnd_20pct 66%, fallback_or_few_peers 83%
  EV/Sales:
    peer 25-75% range as practitioners report it (not calibrated): interval score 5.226, coverage 41.1%, median range x/1.59
    constant band (same width for every firm): interval score 4.233, coverage 80.0%, median range x/3.38
    width proportional to peer_iqr: interval score 4.340, coverage 80.0%, median range x/3.56
    linear regression on ALL inputs (no limit on terms): interval score 3.970, coverage 80.0%, median range x/3.23
    gradient-boosted trees on all inputs (black box): interval score 3.483, coverage 80.1%, median range x/2.86
    coverage of the constant band by firm type: loss_making 72%, smallest_20pct 68%, fastest_growing_20pct 75%, highest_rnd_20pct 72%, fallback_or_few_peers 71%

ARCHIVE: your earlier graded attempts, exploration scores only (18 graded)
  [g04-01] EV/EBITDA interval score 2.550 | coverage 79.8% | median range x/2.02
      EV/EBITDA | base constant | terms log_sales -0.8, ebitda_margin -0.7, debt_to_assets -0.6 | if loss_making x1.3
      by firm type: loss_making 79%, smallest_20pct 79%, fastest_growing_20pct 72%, highest_rnd_20pct 73%, fallback_or_few_peers 75%
      mechanism: Enterprise value is debt plus equity, and the debt part is close to book value and moves little, while the equity part carries all the market's disagreement about the firm. The larger the debt share of the capital structure, the smaller the proportional error in EV when equity is mispriced relative to peers; an all-equity firm's EV moves one-for-one with equity sentiment. So, holding size and margin fixed, highly levered firms should get narrower EV/EBITDA ranges, not wider ones (consistent with g01-03, where a positive leverage weight did worse than the constant band).
  [g02-01] EV/EBITDA interval score 2.559 | coverage 79.8% | median range x/2.03
      EV/EBITDA | base constant | terms log_sales -0.9, ebitda_margin -0.7 | if sales_growth_1y <= p10 x1.35 | if sales_growth_1y >= p90 x1.35 | if loss_making x1.3
      by firm type: loss_making 83%, smallest_20pct 78%, fastest_growing_20pct 75%, highest_rnd_20pct 71%, fallback_or_few_peers 76%
      mechanism: Reported EBITDA is a poor proxy for normalized earnings in a year when sales collapsed or surged, because operating leverage pushes EBITDA temporarily below or above its sustainable level; the market capitalizes normalized EBITDA, so applying a peer multiple to that year's EBITDA misses in either direction. This adds to the thin-margin and small-size effects, where small absolute EBITDA errors move the ratio a lot and idiosyncratic risk is high.
  [g04-03] EV/EBITDA interval score 2.575 | coverage 79.8% | median range x/2.04
      EV/EBITDA | base constant | terms log_sales -0.8, ebitda_margin -0.7 | if sales_growth_1y <= p20 AND sales_growth_3y >= p50 x1.5 | if sales_growth_1y >= p80 AND sales_growth_3y <= p50 x1.4 | if loss_making x1.25
      by firm type: loss_making 80%, smallest_20pct 75%, fastest_growing_20pct 71%, highest_rnd_20pct 70%, fallback_or_few_peers 76%
      mechanism: The market capitalizes a firm's sustainable earnings run rate, not one year's EBITDA. When last year's sales growth breaks sharply from the firm's own 3-year trend (a sudden drop after steady growth, or a spike after stagnation), investors disagree on whether the new level is permanent or transitory, so the reported EBITDA is a noisy base for the peer multiple. A firm growing in line with its own history gives a reliable run rate, so its range can be narrow.
  [g01-01] EV/EBITDA interval score 2.581 | coverage 79.8% | median range x/2.04
      EV/EBITDA | base constant | terms log_sales -1, ebitda_margin -1 | if loss_making x1.4
      by firm type: loss_making 84%, smallest_20pct 78%, fastest_growing_20pct 71%, highest_rnd_20pct 71%, fallback_or_few_peers 76%
      mechanism: When EBITDA is a thin slice of sales, small absolute errors or transitory swings in EBITDA move the EV/EBITDA ratio a lot, and the market prices such firms on normalized rather than reported EBITDA, so peer medians transfer poorly. Small firms add idiosyncratic business risk, illiquidity and sparse analyst coverage, so their values deviate more from sector medians; loss-making firms have reported EBITDA that is unlikely to persist.
  [g02-02] EV/EBITDA interval score 2.607 | coverage 79.7% | median range x/2.04
      EV/EBITDA | base constant | terms ebitda_margin -0.9, capex_intensity +0.6, log_assets -0.8 | if net_margin <= p10 x1.4
      by firm type: loss_making 78%, smallest_20pct 73%, fastest_growing_20pct 70%, highest_rnd_20pct 68%, fallback_or_few_peers 78%
      mechanism: EBITDA ignores capital expenditure, so for capital-hungry firms the share of EBITDA that becomes free cash flow differs a lot between companies, and investors value them on EBIT or FCF rather than EBITDA; a peer median EV/EBITDA therefore transfers poorly when capex intensity is high and margins are thin. Deeply unprofitable firms (very negative net margin despite positive EBITDA) have large below-the-line charges such as depreciation, interest or impairments, which signal EBITDA that will not persist.
  [g03-01] EV/EBITDA interval score 2.614 | coverage 80.0% | median range x/2.03
      EV/EBITDA | base constant | terms log_sales -0.8, ebit_margin -0.6 | if ebitda_margin >= p40 AND ebit_margin <= p25 x1.4 | if net_margin <= p10 x1.25
      by firm type: loss_making 79%, smallest_20pct 75%, fastest_growing_20pct 72%, highest_rnd_20pct 70%, fallback_or_few_peers 78%
      mechanism: When EBITDA is healthy but EBIT is thin, a large share of EBITDA is consumed by depreciation and amortization (heavy maintenance capex or amortization of acquired intangibles), and investors disagree on how much of that D&A is a real recurring cost; some value such firms on EBITDA, others on EBIT or free cash flow, so the peer median EV/EBITDA transfers poorly. Small firms add idiosyncratic risk and thin coverage on top of this accounting wedge.
  [g03-03] EV/EBITDA interval score 2.631 | coverage 79.9% | median range x/2.07
      EV/EBITDA | base constant | terms log_sales -0.8, capex_intensity +0.4 | if sales_growth_1y <= p20 AND capex_intensity >= p60 x1.5 | if ebitda_margin <= p15 x1.4
      by firm type: loss_making 76%, smallest_20pct 76%, fastest_growing_20pct 72%, highest_rnd_20pct 70%, fallback_or_few_peers 81%
      mechanism: Capital-intensive cyclical firms (energy, materials, industrial equipment) whose sales just fell are reporting trough EBITDA, and the market capitalizes mid-cycle earnings, so their EV/EBITDA spikes by an amount that depends on how deep and temporary each firm's trough is; peers in the same SIC code are at different points of recovery. The same operating leverage that makes their EBITDA swing also makes thin-margin firms' ratios unstable.
  [g01-02] EV/EBITDA interval score 2.645 | coverage 79.9% | median range x/2.01
      EV/EBITDA | base constant | terms rnd_intensity +0.8, sales_growth_1y +0.6, gross_margin +0.5, log_assets -0.6 | if no_history x1.3
      by firm type: loss_making 68%, smallest_20pct 77%, fastest_growing_20pct 83%, highest_rnd_20pct 87%, fallback_or_few_peers 74%
      mechanism: Firms with heavy R&D, high gross margins and fast sales growth derive much of their value from growth options and intangible assets that current EBITDA does not capture, so investors' valuations of them diverge widely from the peer median multiple. Firms with no sales history (recent listings) have the least information for the market and the analyst to anchor on.
  [g01-03] EV/EBITDA interval score 2.742 | coverage 79.8% | median range x/2.06
      EV/EBITDA | base constant | terms net_debt_to_ebitda +0.6, log_sales -0.8 | if debt_to_assets >= p80 AND loss_making x1.5 | if peer_iqr >= p80 x1.3
      by firm type: loss_making 77%, smallest_20pct 74%, fastest_growing_20pct 73%, highest_rnd_20pct 68%, fallback_or_few_peers 81%
      mechanism: For highly levered, distressed firms the enterprise value is driven by the option-like value of equity and by debt trading below book, so EV relative to EBITDA departs from healthy peers' multiples in either direction. Where the peers themselves disagree strongly on the multiple, the sector has no single valuation anchor and the median estimate is less reliable.
  [g02-05] EV/Sales interval score 4.096 | coverage 79.9% | median range x/3.15
      EV/Sales | base constant | terms peer_range +0.6, log_sales -0.5 | if n_peers <= p10 x1.5 | if ebitda_margin <= p15 x1.5
      by firm type: loss_making 80%, smallest_20pct 83%, fastest_growing_20pct 79%, highest_rnd_20pct 84%, fallback_or_few_peers 86%
      mechanism: When a sector has few listed firms, the peer set is small and less similar to the target in business mix, so the median peer sales multiple is a weak anchor; every earlier rule under-covered these firms (69-73%). Firms with depressed EBITDA margins have no earnings base tying value to revenue, and wide peer dispersion means the sector itself prices sales inconsistently.
  [g04-06] EV/Sales interval score 4.110 | coverage 79.9% | median range x/3.14
      EV/Sales | base constant | terms peer_range +0.5, log_sales -0.6 | if sales_growth_1y <= p20 AND sales_growth_3y >= p60 x1.5 | if sales_growth_1y >= p80 AND sales_growth_3y <= p40 x1.4 | if ebitda_margin <= p15 x1.5
      by firm type: loss_making 81%, smallest_20pct 84%, fastest_growing_20pct 79%, highest_rnd_20pct 85%, fallback_or_few_peers 70%
      mechanism: EV/Sales capitalizes expected future revenue, so the multiple depends on what investors take as the firm's revenue trajectory. When the latest year's growth breaks sharply from the 3-year trend, investors split on whether the break is a new run rate or a one-off, and the same current sales are worth very different amounts; a firm growing in line with its own history has a clear trajectory that peers' multiples price consistently. This differs from g03-04's one-sided low-growth flag because it conditions on the firm's own history, not on growth level alone.
  [g04-05] EV/Sales interval score 4.125 | coverage 80.0% | median range x/3.23
      EV/Sales | base constant | terms peer_range +0.5, log_sales -0.6 | if ebitda_margin <= p10 x1.6 | if ebitda_margin >= p90 x1.35 | if n_peers <= p10 x1.4
      by firm type: loss_making 79%, smallest_20pct 84%, fastest_growing_20pct 78%, highest_rnd_20pct 83%, fallback_or_few_peers 83%
      mechanism: Peers are chosen as the nearest firms on size and EBITDA margin, but a target with an extreme margin has nearly all its candidate peers on one side, so the median peer's margin is systematically different from the target's and the peer EV/Sales is biased by an amount that varies firm to firm. This boundary effect hits both tails: very-low-margin firms (where value has no earnings base) and very-high-margin firms (where EV/Sales is high and sensitive to how long the margin lasts). Earlier rules widened only the low tail; this tests whether the high tail is also undercovered.
  [g02-04] EV/Sales interval score 4.139 | coverage 79.9% | median range x/3.09
      EV/Sales | base constant | terms gross_margin +0.6, ebitda_margin -0.6, peer_range +0.4, log_sales -0.5 | if no_history x1.3
      by firm type: loss_making 81%, smallest_20pct 83%, fastest_growing_20pct 79%, highest_rnd_20pct 88%, fallback_or_few_peers 69%
      mechanism: A firm with high gross margin but low EBITDA margin is spending heavily on operating investment (sales, marketing, R&D), so its value depends on how much operating leverage it eventually achieves, not on current revenue economics; investors disagree widely on that, so the same sales are worth very different amounts. When the peers' sales multiples also span a wide range, the sector has no stable revenue-to-value mapping.
  [g01-06] EV/Sales interval score 4.143 | coverage 80.0% | median range x/3.07
      EV/Sales | base constant | terms peer_range +0.6, log_sales -0.7 | if ebitda_margin <= p15 x1.6 | if no_history x1.3
      by firm type: loss_making 83%, smallest_20pct 88%, fastest_growing_20pct 79%, highest_rnd_20pct 86%, fallback_or_few_peers 73%
      mechanism: When the peers' EV/Sales multiples span a wide range the sector contains firms with very different margin structures, so the median peer is a weak anchor; using peer spread as a moderating term rather than the full base avoids letting noisy peer statistics dominate. Firms with depressed EBITDA margins or no sales history lack a stable earnings base that would tie their value to their revenue.
  [g03-04] EV/Sales interval score 4.154 | coverage 80.0% | median range x/3.20
      EV/Sales | base constant | terms log_sales -0.6, peer_range +0.5 | if loss_making AND sales_growth_1y >= p70 x1.5 | if sales_growth_1y <= p10 x1.3
      by firm type: loss_making 81%, smallest_20pct 81%, fastest_growing_20pct 82%, highest_rnd_20pct 83%, fallback_or_few_peers 69%
      mechanism: A loss-making firm that is growing fast is valued on the eventual margin of a business it has not yet built, so the same revenue can be worth wildly different amounts depending on investors' belief in its path to profitability; a shrinking firm is valued on how fast and how far the decline goes, which revenue alone does not reveal. Small size and wide peer dispersion add to both.
  [g04-04] EV/Sales interval score 4.188 | coverage 79.8% | median range x/3.12
      EV/Sales | base constant | terms debt_to_assets -0.7, log_sales -0.6, peer_range +0.5 | if ebitda_margin <= p15 x1.5
      by firm type: loss_making 80%, smallest_20pct 86%, fastest_growing_20pct 81%, highest_rnd_20pct 87%, fallback_or_few_peers 69%
      mechanism: EV is book-like debt plus volatile equity, so the share of EV that comes from debt dampens the proportional error of any EV-based multiple; this matters even more for EV/Sales, where errors are large and driven by equity investors' views of future margins. Highly levered firms (utilities, pipelines, telecom, LBO-style capital structures) have EVs pinned partly by contractual claims, so the same peer sales multiple misses them by less in logs than it misses all-equity firms. Wide peer dispersion and depressed EBITDA margins still widen the range, as in earlier rules.
  [g01-05] EV/Sales interval score 4.528 | coverage 79.8% | median range x/3.29
      EV/Sales | base constant | terms gross_margin +0.8, sales_growth_1y +0.6, log_assets -0.8 | if loss_making AND rnd_intensity >= p80 x1.5
      by firm type: loss_making 78%, smallest_20pct 82%, fastest_growing_20pct 89%, highest_rnd_20pct 91%, fallback_or_few_peers 69%
      mechanism: EV/Sales implicitly assumes the target converts sales to cash like its peers; high-gross-margin, fast-growing firms have scalable economics whose eventual profitability is uncertain, so their sales multiples spread out much more than those of low-margin, mature firms where sales map tightly to value. Small asset bases mean little tangible value to anchor EV.
  [g01-04] EV/Sales interval score 4.733 | coverage 80.0% | median range x/3.00
      EV/Sales | base constant | terms log_sales -1, rnd_intensity +0.7 | if negative_ebitda x1.8 | if loss_making x1.2
      by firm type: loss_making 88%, smallest_20pct 90%, fastest_growing_20pct 83%, highest_rnd_20pct 94%, fallback_or_few_peers 69%
      mechanism: Firms with non-positive EBITDA are valued on the hope of future profits rather than on current sales economics, so the same revenue can be worth very different amounts and a peer EV/Sales median is a weak anchor. Small size and heavy R&D compound this, since value then rests on unproven products and a few idiosyncratic outcomes.

FAILED OR REJECTED ATTEMPTS (most recent)
  [g02-03] rejected: critic: This is g01-01 and g01-02 merged with lightly changed weights: it adds no new input, condition or economic channel, so a result would only show whether the two tried rules work better together, not test a new ide
  [g02-06] rejected: critic: The premise that high-turnover, thin-margin firms have tightly clustered EV/Sales does not hold in logs, since small differences between thin margins cause large proportional differences in EV/Sales, and peers al
  [g03-02] rejected: critic: The mechanism is about asset-light firms with very high returns, but the rule treats turnover and ROIC separately and adds a roic <= p10 condition the mechanism never justifies; to test the idea, put the conjunct
  [g03-05] rejected: critic: The mechanism is about a capital-intensity mismatch between the target and its own SIC peers, but the rule uses the target's turnover percentile across all firms in the year, which mostly flags whole sectors (les
  [g03-06] rejected: critic: This is essentially g01-03's leverage-distress idea (net debt/EBITDA plus high debt_to_assets AND loss_making) moved to EV/Sales, and on EV/Sales net_debt_to_ebitda turns negative or meaningless for negative-EBIT
  [g04-02] rejected: critic: The two-tailed ROIC conditions (<= p10, >= p90) are the economic idea already tested in g03-02, and the terms are g01-01's, so this only splices two tried rules with a slightly changed multiplier and brings no ne

Each proposal needs:
  - "mechanism": the economic reason these firms' market values are harder (or easier) to pin
    down with comps (2-3 sentences)
  - "prediction": a falsifiable expectation, e.g. "interval score below the constant band's"
  - "rule": the rule object
An independent referee, who sees your mechanism but no scores, will reject proposals without a
specific economic reason, or near-copies of earlier rules (e.g. one weight changed slightly).

Reply with ONLY this JSON, no other text:
{"proposals": [{"name": "...", "mechanism": "...", "prediction": "...",
  "rule": {"multiple": "...", "base": "...", "terms": {...}, "conditions": [...]}}]}
