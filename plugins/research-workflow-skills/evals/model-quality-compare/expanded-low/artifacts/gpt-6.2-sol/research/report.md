# Education expenditure and income in the supplied World Bank extract

## What the questions become with these data

The original questions ask where increased education spending **positively impacts per capita GDP**, and what its **impact on per capita GDP in developing countries** is. The extract can answer a narrower descriptive question: within each of two World Bank aggregates, how do an education expenditure share and real GNI per capita move together, in levels and in year-to-year changes? It cannot identify an impact on GDP.

- **Income (Y):** `NY.GNP.PCAP.KD`, GNI per capita in constant 2015 US dollars, not GDP per capita in 2010 dollars as the metadata overview suggests. GNI includes net primary income from abroad, unlike GDP.
- **Education (X):** `NY.ADJ.AEDU.GN.ZS`, “Adjusted savings: education expenditure,” measured in percent of GNI, not percent of total government expenditure. The adjusted-savings label is an accounting classification, not evidence of money set aside for future education as the metadata's series description suggests. An increase in this ratio is not necessarily an increase in the amount spent: the denominator can change too.
- **Groups:** the CSV labels Sub-Saharan Africa as **SSF**, whereas the metadata says **SSA**. Lower middle income (**LMC**) is an income classification, not a geographic region or a proxy for all developing countries. The groups are not necessarily disjoint. The CSV contains aggregate series, not individual country observations.
- **Coverage:** the CSV has columns for 1975–2015, but only five years of Sub-Saharan African GNI per capita. Both education series and the LMC income series cover all 41 years. Exports growth, gross primary and secondary enrollment, and labor force participation (a rate, not a headcount) are also present but not used as controls.

## Method and findings

Within each group, pair finite numeric values in the same calendar year and discard missing pairs without imputation. Report Pearson's correlation and the OLS slope with an intercept, regressing income on the education share. Repeat using same-year changes from the previous calendar year, only where both endpoints have valid pairs. Differencing reduces the influence of persistent levels and some trends that can dominate a levels comparison. It addresses short-run co-movement, not long-run or lagged relationships, and does not by itself remove confounding.

| Group | Analysis | Years (ending year for changes) | n | Pearson r | OLS slope |
|---|---|---|---:|---:|---:|
| Sub-Saharan Africa (SSF) | Levels | 2011–2015 | 5 | −0.966 | −159.13 |
| Sub-Saharan Africa (SSF) | First differences | 2012–2015 | 4 | −0.456 | −80.48 |
| Lower middle income (LMC) | Levels | 1975–2015 | 41 | −0.481 | −635.07 |
| Lower middle income (LMC) | First differences | 1976–2015 | 40 | +0.079 | +11.06 |

Slopes are in constant 2015 US dollars of GNI per capita per percentage point of the education share. In first differences, the slope compares changes in those quantities: in LMC, a one-percentage-point larger annual change in the share is associated with an approximately $11 larger annual change in GNI per capita in the fitted line.

Neither aggregate shows a positive association in levels. The LMC association changes sign after differencing, but the positive correlation is close to zero. SSF remains negative after differencing, but four changes are too few to draw a reliable regional conclusion. The two groups are observed over very different periods, so the slope contrast cannot be attributed to region or income classification.

## What is warranted

No geographic region in this extract shows a positive association under either specification, and the weak positive association in LMC annual changes does not establish a positive impact in developing countries. Nor do the negative slopes establish harm. Economic shocks, reverse causality, a changing GNI denominator, differences in aggregate membership or composition, omitted variables and serial dependence can all complicate interpretation. These are contemporaneous, unadjusted descriptive estimates; there is no causal design, country-level evidence, or inference about delayed returns to education.

## Provenance and reproduction

The supplied files come from Allen Institute for AI's [DiscoveryBench](https://github.com/allenai/discoverybench), revision `c31fcf011e070f021a5f5b906896d0821f6880e8`, path `discoverybench/real/test/worldbank_education_gdp`. The metadata names the original extract `worldbank_education_gdp.csv`, attributes the underlying data to the World Bank's World Development Indicators, and lists ODC-By (see `SOURCE-LICENSE.txt`). This analysis uses the supplied snapshot, not a fresh WDI download. Run `python3 analyze.py data.csv > results.json` to reproduce the estimates.
