# Education spending and income: what these data support

## Questions
1. In what regions does increased education spending positively impact per capita GDP?
2. What is the impact of increased education expenditure on per capita GDP in developing countries?

## Data actually available
`data.csv` has two aggregate groups, not countries: Sub-Saharan Africa (`SSF`) and Lower middle income (`LMC`). Annual columns run 1975–2015 for six WDI series. I used:
- Income (Y): `NY.GNP.PCAP.KD`, GNI per capita, constant 2015 US$. This is GNI, not GDP.
- Education (X): `NY.ADJ.AEDU.GN.ZS`, adjusted savings: education expenditure, % of GNI.

The education series is nearly complete. Income is blank for SSF before 2011 (only 5 years, 2011–2015) but complete for LMC (41 years). Missing cells are blank here (no `..` in this file; the script also treats `..` as missing). Pairs use calendar years where both are finite. Differences use only consecutive years, with no bridging of gaps. OLS includes an intercept.

## Results (`results.json`, from `python3 analyze.py data.csv`)
| Group | Analysis | n | Pearson r | OLS slope (US$ per percentage point of GNI) |
|---|---|---|---|---|
| SSF | level | 5 | -0.966 | -159.1 |
| SSF | first difference | 4 | -0.456 | -80.5 |
| LMC | level | 41 | -0.481 | -635.1 |
| LMC | first difference | 40 | 0.079 | 11.1 |

## Analytical choice
Level correlations of two trending series are likely spurious: income trends upward while the education share drifts or falls, so level slopes mostly reflect time trends. The first-difference analysis removes slowly moving trends and is the more defensible one. With it, LMC shows essentially no association (r = 0.08, slope 11 with n = 40; no uncertainty is computed, but this is small and near zero). SSF's difference estimate rests on 4 pairs and is not informative.

## Conclusions warranted
- The data do **not** show that higher education spending is positively associated with income in either group. Level associations are negative; the LMC difference association is ~0.
- A region-by-region answer to question 1 is impossible beyond two aggregates; no positive association was found in either.
- Question 2 (impact) is a causal question. These data cannot answer it: only two aggregate series, no controls, no lags, no identification, reverse causality possible (education spending is a share of GNI, so GNI is in the denominator, which mechanically links the two), and education effects on income plausibly take years or decades.
- The "developing countries" are only two World Bank groups; findings are not country-level.

## Limitations and provenance
- SSF level/difference rest on 5 and 4 points; r = -0.97 at n = 5 is fragile and driven by 2011–2015 co-movement.
- No significance tests, lags, or other covariates (exports, enrollment, labor force were provided but not used).
- Metadata/data inconsistencies: metadata describes education spending as "% of total expenditure" and income as "per capita GDP (2010 US$)", while the data are % of GNI and GNI per capita in 2015 US$. Metadata names the Sub-Saharan code `SSA`; the file uses `SSF`. Metadata implies both groups span 1975–2015, but SSF income exists only for 2011–2015. I trusted the CSV series codes and names.
- Source: DiscoveryBench World Bank WDI extract supplied in `data.csv` and `metadata.json` (unchanged); see SOURCE-LICENSE.txt.
