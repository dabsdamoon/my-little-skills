# Education expenditure and income: descriptive investigation

## Questions and available evidence
The original questions ask (1) in what regions increased education spending
positively impacts per capita GDP and (2) what impact increased education
expenditure has on per capita GDP in developing countries. This file cannot
identify causal impacts or answer those questions literally.

The supplied `data.csv` has 12 indicator rows: six series for each of two
**group aggregates**, not individual countries. Its 41 annual columns span
1975–2015. The groups are Sub-Saharan Africa (`SSF`) and Lower middle income
(`LMC`). LMC is an income category, not a geographical region; these categories
can overlap and do not represent all developing countries.

The requested income series `NY.GNP.PCAP.KD` is **GNI per capita in constant
2015 US dollars**, not GDP per capita in 2010 dollars. The education series
`NY.ADJ.AEDU.GN.ZS` is **adjusted savings: education expenditure (% of GNI)**,
not education spending as a percentage of total government expenditure. The
metadata's introductory description uses the latter GDP and government-budget
concepts, inconsistent with the actual series codes and names. Its SSA code
also differs from the actual SSF code. We use the CSV identifiers and labels.
The metadata's phrase “saved for future education expenditures” should not be
read as evidence that this measures a stock of earmarked future savings;
the supplied series is an education-expenditure share in the adjusted-savings
framework. No external indicator documentation was retrieved.

Other available series concern exports growth, gross primary/secondary
enrollment, and labor-force participation. The last is not total labor-force
size, despite the introductory metadata wording. They are not used as controls
in this deliberately small bivariate analysis.

## Method and reproducibility
Run `python3 analyze.py data.csv > results.json` using Python's standard library.
The script reads its argument, selects the two exact series codes, pairs finite
numeric observations by year within each group, and sorts chronologically.
Blank, `..`, nonnumeric, and nonfinite values are excluded without imputation.
Only groups containing both series are included. Duplicate group/series rows
are rejected rather than arbitrarily selected.

For each group we report Pearson correlation and OLS with an intercept,
regressing income Y on education X. The slope is centered cross-product divided
by centered X sum of squares. We also apply the same calculations to annual
first differences, using only consecutive calendar years of complete pairs:
missing years are never bridged. Undefined correlations or slopes are JSON
null (fewer than two observations, constant X, or constant Y for correlation).
Differencing is a descriptive sensitivity analysis to common trends, not a
causal identification strategy. It relates contemporaneous changes and does
not model delayed education effects. No significance tests are claimed.

## Findings
Slopes are constant-2015 US dollars per capita per **one percentage-point**
education share, or dollars of annual income change per percentage-point annual
share change for differences. Values below are rounded; `results.json` retains
full computed precision.

| Group | Level years | Level n | Level r | Level slope | Difference intervals | Difference n | Difference r | Difference slope |
|---|---|---:|---:|---:|---|---:|---:|---:|
| Lower middle income (LMC) | 1975–2015 | 41 | -0.480538 | -635.074242 | 1975→1976 through 2014→2015 | 40 | 0.078761 | 11.063895 |
| Sub-Saharan Africa (SSF) | 2011–2015 | 5 | -0.966421 | -159.131456 | 2011→2012 through 2014→2015 | 4 | -0.455752 | -80.477511 |

Education has 41 finite annual observations in each group, but SSF income has
only five (2011–2015); LMC income has all 41. The apparent 1975–2015 coverage
therefore does not provide 41 usable income/education pairs for Africa.

Both groups show negative level associations. For LMC, the association of
annual changes is weakly positive and close to zero, unlike the negative level
association. For SSF, both are negative, but the change analysis has only four
pairs. Thus the only positive descriptive result is a very small correlation
of annual changes for the lower-middle-income aggregate; it is not evidence
that spending increases positively impact GDP. Neither observed regional
aggregate provides a positive level association, and these two groups cannot
rank regions worldwide.

## Interpretation, limitations, and provenance
These are observational aggregate time series. Reverse causation, omitted
variables, shared trends, serial dependence, spending measured relative to GNI,
changing group composition, and aggregation can all affect the estimates.
A share can change because its income denominator changes without an increase
in real education resources. The groups overlap and have different usable
periods, precluding a clean comparative effect interpretation. First differences
do not resolve confounding or simultaneity and may amplify measurement noise.
No intervention, instrument, comparison design, or individual-country panel is
present. Results support only the associations above, not causal effects,
country-level claims, or a definitive conclusion about developing countries.

Inputs were inspected locally and left unchanged. Supplied metadata attributes
the data to World Development Indicators through DiscoveryBench, repository
`https://github.com/allenai/discoverybench`, revision
`c31fcf011e070f021a5f5b906896d0821f6880e8`, path
`discoverybench/real/test/worldbank_education_gdp`, license ODC-By; the supplied
`SOURCE-LICENSE.txt` is retained. This is supplied provenance, not an independent
verification of source accuracy or aggregation methodology.

A local subprocess/temporary-CSV check passed: reordered year columns yield
exact r=1 and slope=2, a missing middle year is not bridged, blank/`..`/NaN/inf
are excluded, and constant series yield null statistics. A rerun of the real
CSV reproduced `results.json` byte for byte.
