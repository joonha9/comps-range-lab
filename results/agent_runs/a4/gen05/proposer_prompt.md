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

ARCHIVE: your earlier graded attempts, exploration scores only (15 graded)
  [g03-02] EV/EBITDA interval score 2.557 | coverage 79.8% | median range x/1.99
      EV/EBITDA | base constant | terms log_sales -0.8, rnd_intensity +0.4 | if roic <= p10 x1.4 | if net_margin <= p10 x1.3 | if sales_growth_1y >= p85 x1.3
      by firm type: loss_making 78%, smallest_20pct 79%, fastest_growing_20pct 79%, highest_rnd_20pct 78%, fallback_or_few_peers 73%
      mechanism: Investors price normalized rather than current earnings, so when a firm's returns on capital or net margins are far below normal (a cyclical trough, restructuring or write-down year), current EBITDA understates the earnings the market capitalizes and the EV/EBITDA multiple spikes unpredictably relative to peers. Small and R&D-heavy firms add intangible value not in EBITDA; firms earning normal returns trade near the peer median.
  [g04-01] EV/EBITDA interval score 2.560 | coverage 79.9% | median range x/2.00
      EV/EBITDA | base constant | terms gross_margin +0.6, ebitda_margin -0.6, log_sales -0.7 | if rnd_intensity >= p80 x1.2
      by firm type: loss_making 72%, smallest_20pct 76%, fastest_growing_20pct 74%, highest_rnd_20pct 82%, fallback_or_few_peers 76%
      mechanism: EBITDA is what is left of gross profit after a largely fixed operating cost base, so a firm with a high gross margin but a low EBITDA margin has EBITDA that is a thin residual of gross profit: a small change in revenue or opex moves it a lot, and the market prices the gross-profit franchise rather than the depressed residual. Its EV/EBITDA multiple therefore floats far from peers, while firms whose EBITDA captures most of gross profit (low gross, high EBITDA margin) have a stable earnings base that trades near sector norms.
  [g03-03] EV/EBITDA interval score 2.570 | coverage 79.8% | median range x/2.01
      EV/EBITDA | base constant | terms peer_iqr +0.5, log_sales -0.8, gross_margin +0.4 | if loss_making x1.4
      by firm type: loss_making 81%, smallest_20pct 80%, fastest_growing_20pct 75%, highest_rnd_20pct 77%, fallback_or_few_peers 78%
      mechanism: When the ten nearest peers disagree strongly on their EBITDA multiple, the sector has no stable pricing convention and the median is a weak anchor for the target. This is compounded for small and high-gross-margin firms, whose intangible-heavy business models are valued on scalability expectations that differ widely across firms, and for loss-makers whose EBITDA is above what reaches shareholders.
  [g03-01] EV/EBITDA interval score 2.573 | coverage 79.9% | median range x/2.03
      EV/EBITDA | base constant | terms log_assets -0.8, debt_to_assets -0.5, capex_intensity -0.3 | if loss_making x1.4 | if sales_growth_1y >= p85 x1.3
      by firm type: loss_making 78%, smallest_20pct 78%, fastest_growing_20pct 78%, highest_rnd_20pct 74%, fallback_or_few_peers 76%
      mechanism: Enterprise value is the sum of debt and equity, and the debt piece is close to book value and moves little, so in highly levered firms most of EV is pinned down and the log error of a peer-multiple estimate is mechanically smaller. Asset-heavy, capex-intensive firms are also priced off replaceable tangible capital, which keeps their multiples close to sector norms, while small equity-funded firms, loss-makers and hypergrowers carry their value in volatile equity claims on uncertain future earnings.
  [g04-02] EV/EBITDA interval score 2.575 | coverage 79.7% | median range x/2.04
      EV/EBITDA | base constant | terms log_sales -0.8, gross_margin +0.3 | if sales_growth_1y >= p80 AND ebit_margin <= p30 x1.5 | if sales_growth_1y <= p15 AND ebit_margin <= p30 x1.3 | if loss_making x1.2
      by firm type: loss_making 78%, smallest_20pct 77%, fastest_growing_20pct 76%, highest_rnd_20pct 74%, fallback_or_few_peers 76%
      mechanism: A fast-growing firm with a thin operating margin is expensing its growth (sales force, onboarding, R&D), so current EBITDA is a temporarily depressed base and the market capitalizes a much larger future EBITDA whose size peers cannot reveal; the multiple is extreme and unpredictable. A shrinking firm with thin margins is the mirror case, priced on restructuring or liquidation value rather than going-concern EBITDA. Only the combination of growth extremes with weak margins should widen the range; profitable fast growers already show the earnings the market is paying for.
  [g02-01] EV/EBITDA interval score 2.584 | coverage 80.0% | median range x/2.03
      EV/EBITDA | base constant | terms log_sales -0.8, rnd_intensity +0.5, sales_growth_1y +0.4 | if loss_making x1.4
      by firm type: loss_making 80%, smallest_20pct 79%, fastest_growing_20pct 80%, highest_rnd_20pct 80%, fallback_or_few_peers 75%
      mechanism: Small firms, R&D-heavy firms and fast growers carry most of their value in growth options and intangibles that current EBITDA does not capture, so the peer-median EBITDA multiple is a noisy anchor for them; loss-making firms with positive EBITDA have earnings far below normalized levels, making the EBITDA base itself unrepresentative. Large, mature, low-R&D firms trade close to sector multiples.
  [g04-03] EV/EBITDA interval score 2.599 | coverage 79.9% | median range x/2.04
      EV/EBITDA | base constant | terms log_assets -0.8, asset_turnover +0.3 | if roic <= p10 x1.4 | if roic >= p90 x1.3 | if roe >= p95 x1.2
      by firm type: loss_making 71%, smallest_20pct 74%, fastest_growing_20pct 71%, highest_rnd_20pct 70%, fallback_or_few_peers 80%
      mechanism: Return on invested capital is U-shaped in its link to comps error: at very low ROIC, current EBITDA is far below the normalized earnings the market capitalizes, and at very high ROIC the firm's value rests on unmeasured intangible capital (brands, software, network effects) whose durability the market judges firm by firm, so in both tails the multiple departs from the sector median. Firms earning ordinary returns on a measured capital base are priced like their peers.
  [g02-03] EV/EBITDA interval score 2.612 | coverage 79.9% | median range x/2.05
      EV/EBITDA | base constant | terms log_sales -0.7, gross_margin +0.5 | if sales_growth_1y >= p85 x1.4 | if sales_growth_1y <= p10 x1.3
      by firm type: loss_making 71%, smallest_20pct 77%, fastest_growing_20pct 80%, highest_rnd_20pct 77%, fallback_or_few_peers 76%
      mechanism: Firms at either tail of sales growth are in transition: hypergrowth firms are priced on future EBITDA far above current, and sharply shrinking firms are priced on turnaround or liquidation prospects, so both deviate from steady-state peer multiples. High gross margin indicates intangible-heavy business models whose valuations depend on scalability expectations that differ widely across firms.
  [g02-02] EV/EBITDA interval score 2.704 | coverage 79.9% | median range x/2.10
      EV/EBITDA | base constant | terms ebitda_margin -0.8, net_debt_to_ebitda +0.5, log_assets -0.6 | if no_history x1.3
      by firm type: loss_making 74%, smallest_20pct 70%, fastest_growing_20pct 69%, highest_rnd_20pct 65%, fallback_or_few_peers 81%
      mechanism: When EBITDA is a thin slice of sales, small changes in costs move EBITDA a lot proportionally, so EV/EBITDA for low-margin firms is unstable and depends on whether the market sees the margin as temporary. High net debt relative to EBITDA signals distress or restructuring, where EV reflects default and recovery scenarios rather than going-concern peer multiples; newly listed firms lack the track record investors use to price against peers.
  [g02-06] EV/Sales interval score 4.100 | coverage 79.9% | median range x/3.07
      EV/Sales | base constant | terms peer_iqr +0.4, log_sales -0.8 | if negative_ebitda x1.4 | if n_peers <= p10 x1.3 | if no_history x1.3
      by firm type: loss_making 82%, smallest_20pct 86%, fastest_growing_20pct 78%, highest_rnd_20pct 85%, fallback_or_few_peers 82%
      mechanism: Comps are only as informative as the peer set: when peers disagree strongly on the sales multiple, or a firm's sector is thin or it lacks history, the median peer multiple says little about the target, and EV/Sales is especially sensitive because it ignores margin differences. Negative-EBITDA firms are additionally priced on survival odds, which no peer multiple encodes.
  [g04-04] EV/Sales interval score 4.167 | coverage 80.0% | median range x/3.23
      EV/Sales | base constant | terms log_sales -0.8 | if ebitda_margin <= p10 x1.5 | if ebitda_margin >= p90 x1.3 | if gross_margin >= p85 x1.2 | if n_peers <= p10 x1.2
      by firm type: loss_making 79%, smallest_20pct 84%, fastest_growing_20pct 80%, highest_rnd_20pct 84%, fallback_or_few_peers 79%
      mechanism: EV/Sales equals EBITDA margin times an EBITDA multiple, so the peer median sales multiple is only valid if peers share the target's margin; nearest-neighbour peer matching works well in the middle of the margin distribution but at its tails the closest peers are still far away, so the sales multiple is extrapolated. Firms with very low margins are priced on whether margins recover, and firms with very high margins on how durable they are, so both tails should get wide ranges, unlike a monotone margin term that wrongly narrows the high-margin tail.
  [g03-05] EV/Sales interval score 4.177 | coverage 80.0% | median range x/3.05
      EV/Sales | base constant | terms log_sales -0.7, debt_to_assets -0.6, peer_iqr +0.4 | if negative_ebitda x1.5 | if no_history x1.3
      by firm type: loss_making 82%, smallest_20pct 87%, fastest_growing_20pct 80%, highest_rnd_20pct 89%, fallback_or_few_peers 74%
      mechanism: In levered firms a large share of EV is debt carried near face value, so EV is less sensitive to swings in equity sentiment and a peer-median sales multiple misses by less in log terms. Equity-financed small firms, and especially those burning cash with negative EBITDA, have EV that is almost entirely a volatile option-like equity claim, so their sales multiple is far harder to pin down from peers.
  [g04-05] EV/Sales interval score 4.365 | coverage 80.0% | median range x/3.09
      EV/Sales | base constant | terms log_sales -0.8, gross_margin +0.3 | if rnd_intensity >= p80 AND loss_making x1.6 | if sales_growth_1y >= p85 AND negative_ebitda x1.4 | if no_history x1.3
      by firm type: loss_making 82%, smallest_20pct 86%, fastest_growing_20pct 82%, highest_rnd_20pct 90%, fallback_or_few_peers 70%
      mechanism: For R&D-intensive firms that are still losing money, and for hypergrowth firms with negative EBITDA, current sales are not the value driver: the market prices a product pipeline or a future scale whose payoff is binary, so revenue is close to irrelevant and any sales multiple taken from peers is arbitrary. Outside these pipeline-type firms, sales relate to value through ordinary margins and the peer median anchors well.
  [g02-05] EV/Sales interval score 4.375 | coverage 80.0% | median range x/3.31
      EV/Sales | base constant | terms gross_margin +0.8, sales_growth_1y +0.6, log_assets -0.6 | if loss_making x1.3
      by firm type: loss_making 80%, smallest_20pct 79%, fastest_growing_20pct 89%, highest_rnd_20pct 87%, fallback_or_few_peers 69%
      mechanism: High gross margin, fast-growing firms are valued on expected future operating leverage: each dollar of sales could become a large or small amount of future profit, so EV/Sales multiples within a sector fan out widely for them. Small firms and loss-makers add uncertainty about survival and dilution, while low-margin, slow-growth, large firms trade in a tight band of sales multiples.
  [g02-04] EV/Sales interval score 4.518 | coverage 79.9% | median range x/2.94
      EV/Sales | base constant | terms ebitda_margin -1, log_sales -0.6, rnd_intensity +0.5 | if negative_ebitda x1.5
      by firm type: loss_making 86%, smallest_20pct 87%, fastest_growing_20pct 81%, highest_rnd_20pct 91%, fallback_or_few_peers 69%
      mechanism: EV/Sales implicitly assumes the target converts sales to value like its peers, but value per dollar of sales scales with margins, so firms with low or negative EBITDA margins are priced on whether and when they will become profitable, a judgment the peer median cannot supply. Small and R&D-intensive firms add option-like value that sales do not reflect.

FAILED OR REJECTED ATTEMPTS (most recent)
  [g01-01] invalid: multiple: must be one of ['EV/EBITDA', 'EV/Sales']
  [g01-02] invalid: multiple: must be one of ['EV/EBITDA', 'EV/Sales']
  [g01-03] invalid: multiple: must be one of ['EV/EBITDA', 'EV/Sales']
  [g01-04] invalid: multiple: must be one of ['EV/EBITDA', 'EV/Sales']
  [g01-05] invalid: multiple: must be one of ['EV/EBITDA', 'EV/Sales']
  [g01-06] invalid: multiple: must be one of ['EV/EBITDA', 'EV/Sales']
  [g03-04] rejected: critic: This is g02-06's size/peer_iqr/negative_ebitda structure combined with g02-04's R&D term, with the same pre-profit-innovator mechanism as g02-04; swapping in a growth threshold adds no new economic idea, so it is
  [g03-06] rejected: critic: Going-concern doubt is the loss-making/negative-EBITDA idea already tested in g02-05 and g02-06; net_margin <= p10 is just a stricter version of the loss_making flag, and the remaining terms and conditions repeat
  [g04-06] rejected: critic: The mechanism is about steady-state firms with modest growth, but sales_growth_1y <= p60 also takes in sharply shrinking firms (the bottom tail that other mechanisms treat as hard to value) and narrows their rang

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
