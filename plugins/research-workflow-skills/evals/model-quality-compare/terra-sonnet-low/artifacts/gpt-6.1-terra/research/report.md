# Education expenditure and income in the supplied World Bank data

## Questions and available evidence

The original questions ask in which regions increased education spending positively impacts GDP per capita, and what impact increased education expenditure has on GDP per capita in developing countries. The supplied data cannot identify those causal impacts or provide a comprehensive regional comparison. They contain two aggregate groups, Sub-Saharan Africa (SSF) and lower middle income (LMC), the latter an income classification rather than a geographic region or all developing countries. These are group-level observations, not a country-level panel; group membership may overlap.

The analysis uses the actual series codes and labels: X is adjusted savings: education expenditure (% of GNI), `NY.ADJ.AEDU.GN.ZS`; Y is GNI per capita (constant 2015 US dollars), `NY.GNP.PCAP.KD`. Education is a share of GNI, not spending per person or a share of total government expenditure. A change in that ratio need not represent a change in absolute education spending. GNI is not GDP. The metadata's general description instead claims government education expenditure as a percentage of total expenditure and GDP per capita in constant 2010 dollars; its detailed series descriptions and the CSV identify the different measures above. It also names the African code SSA, whereas the CSV uses SSF. Its description of education expenditure as money “saved for future education expenditures” should not be taken as establishing such a mechanism. Other indicators are present but are not used here.

## Method and results

Run `python3 analyze.py data.csv > results.json`. Within each group, pair finite observations of the two series for the same calendar year. For levels, calculate Pearson's r and the OLS slope with an intercept, treating education as X and income as Y. For differences, calculate those statistics on changes between consecutive paired calendar years only; missing years are not bridged. The slope is in constant 2015 US dollars of GNI per person per percentage-point difference in the education-to-GNI measure; the differenced slope relates annual changes in those quantities. These are descriptive contemporaneous associations, not adjusted effects. Results are rounded below; `results.json` retains computed precision.

| Group | Levels: years, n | Level r | Level slope | Consecutive annual changes: n | Change r | Change slope |
|---|---:|---:|---:|---:|---:|---:|
| Lower middle income (LMC) | 1975–2015, 41 | -0.481 | -635.07 | 40 | 0.079 | 11.06 |
| Sub-Saharan Africa (SSF) | 2011–2015, 5 | -0.966 | -159.13 | 4 | -0.456 | -80.48 |

Both level associations are negative. LMC annual changes show a very weak positive association; SSF changes show a negative association based on only four changes. Thus even the descriptive sign depends on the group and whether levels or changes are examined. Neither provides evidence that increased education spending causes a rise or fall in income, and these data cannot answer which regions experience a positive causal impact.

Differencing is a complementary choice to reduce the influence of persistent levels and common trends, not a causal design: it can amplify measurement noise and removes long-run information, while contemporaneous changes can miss delayed effects. Levels can reflect shared trends and serial dependence. Neither analysis controls for confounding, reverse causality, economic shocks, changing group composition, or other indicators, and no uncertainty estimates are supplied. The short SSF overlap is particularly fragile. The groups and aggregate series cannot reveal within-country relationships or identify all developing countries.

## Provenance

The supplied `metadata.json` attributes the data to World Development Indicators and identifies DiscoveryBench repository revision `c31fcf011e070f021a5f5b906896d0821f6880e8`, path `discoverybench/real/test/worldbank_education_gdp`, licensed ODC-By (see `SOURCE-LICENSE.txt`). This investigation uses the supplied snapshot without external validation; metadata describe 1975–2015, but usable overlap varies by series and group as shown above.
