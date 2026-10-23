# Who powers France? Electricity mix and self-sufficiency of the regions

Individual project - Data Visualisation (EFREI, #EFREIDataStories2026). Streamlit data-storytelling dashboard.

- **Live app**: https://electricity-dashboard-yukqqxyxdw8j8yzbctgpat.streamlit.app/
- **Repository**: https://github.com/Evit94/electricity-dashboard
- **Storyboard**: [STORYBOARD.pdf](STORYBOARD.pdf)
- **Demo video**: https://youtu.be/yWWaE07H9is

## Story

- **Hook**: electricity is produced and consumed locally, and French regions are very different.
- **Questions**: which regions produce more than they consume? How green is each regional mix, and how did it change? What would change if a region built more solar or wind?
- **Audience**: citizens, students and regional decision makers.
- **Arc**: hook and context -> KPIs -> trends over time -> regional comparison (map, ranking, scatter, small multiples) -> what-if -> data quality -> insights and next steps.

## Data

- **Dataset**: [eCO2mix regional data, consolidated and final](https://www.data.gouv.fr/datasets/donnees-eco2mix-regionales-consolidees-et-definitives) (RTE), published on data.gouv.fr. Data is downloaded from the ODRE (Open Data Reseaux Energies) export of the same dataset.
- **Licence**: Licence Ouverte v2.0 (Etalab).
- **Content**: half-hourly consumption and production by source for the 12 metropolitan regions (without Corsica), January 2013 to the latest consolidated month (about 2.9 million rows).
- **Region boundaries**: [Contours des communes de France simplifie, avec regions et DROM rapproches](https://www.data.gouv.fr/datasets/contours-des-communes-de-france-simplifie-avec-regions-et-departement-doutre-mer-rapproches) (data.gouv.fr, Licence Ouverte v2.0). Only the metropolitan regions are kept.
- **No sampling**: the full dataset is aggregated, so no seed is needed. Constants (sources, emission factors, indicators) are in `utils/config.py`.

## Data work

1. Download one CSV per region (4 parallel requests, 3 retries). The row count is checked against the source, because a truncated download was observed once.
2. Convert to numbers (text such as `-` or `ND` becomes missing and is counted), remove the duplicated timestamps found around the March daylight-saving change (28 per region, 26 timestamps are missing around October).
3. Convert timestamps from UTC to Paris time, then aggregate to months. MW per half-hour is converted to GWh (x 0.5 / 1000).
4. Compute indicators: production, renewable share, low-carbon share, self-sufficiency (production / consumption), estimated CO2 intensity, and a rolling 12-month version of each to remove seasonality.
5. Quality statistics (rows, duplicates, missing, negative values) are computed on the raw rows and saved in `data/quality.csv`.

Assumptions:

- Missing source values are treated as 0 in the sums (for example nuclear in a region without reactors).
- CO2 intensity uses fixed life-cycle factors in gCO2eq/kWh (IPCC AR5, medians): nuclear 12, hydro 24, wind 11, solar 41, bioenergy 230, thermal 490. It is an estimate for **local production**, not for the electricity consumed.
- Self-sufficiency compares production and consumption over a period; it ignores the real flows between regions.

## Run

Python 3.10+ is recommended.

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt
python download_data.py         # optional, the processed files are already in data/
streamlit run app.py
```

`python download_data.py --force` rebuilds `data/` from the source (about 10 minutes). If `data/` is missing, the app calls the same code on first launch.

## Project structure

```
app.py                  page layout, sidebar filters, KPI header
download_data.py        data download script (with caching)
sections/
  intro.py              hook, context, questions
  overview.py           trends over time, mix by year
  deep_dives.py         map, ranking, scatter, small multiples
  whatif.py             scenario sliders
  quality.py            validation checks, missing values, limitations
  conclusions.py        insights, implications, next steps
utils/
  config.py             paths, URLs, constants, indicator definitions
  io.py                 fetch_and_cache(), load_data()
  prep.py               cleaning, aggregation, indicators
  viz.py                chart functions with a common style
data/                   processed monthly data, quality stats, region boundaries
```

## Features checklist

- Sidebar: regions, period, indicator.
- KPI header tied to the filters (with change vs the first 12 months of the selection).
- Interactive Plotly charts with hover: line, stacked bars, map, ranking, scatter, small multiples, scenario bars.
- Data quality section: missing values, duplicates, validation checks.
- `st.cache_data` on data loading and on aggregations, pre-aggregation to monthly data.
- Accessibility: each chart has a text description, axes have labels and units, colour-blind-safe palette for sources.

## Limitations

See the "Data quality and limitations" section of the app. Main ones: Corsica not covered, recent months are consolidated and not final, CO2 intensity is an estimate, results are descriptive and do not prove causes.

## Credits

Data: RTE (eCO2mix) and data.gouv.fr, Licence Ouverte v2.0. Emission factors: IPCC AR5 WG3 Annex III. Code: individual student project.
