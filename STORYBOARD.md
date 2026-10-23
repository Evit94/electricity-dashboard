# Storyboard: Who powers France?

Individual project - Data Visualisation (EFREI, #EFREIDataStories2026). Streamlit dashboard on regional electricity production and consumption (RTE eCO2mix, 12 metropolitan regions, 2013 to 2026).

## Story in one line

Electricity is produced and consumed locally, and French regions are very different: a few power the others, and a green mix does not mean self-sufficiency.

- **Audience**: citizens, students and regional decision makers who want a quick, visual answer.
- **Narrative pattern**: compare regions (map, ranking, small multiples) + change over time + what-if exploration.
- **Questions**:
  1. Which regions produce more electricity than they consume?
  2. How green is each regional mix, and how did it change?
  3. What would change if a region built more solar or wind?

## Flow of the page

```
 SIDEBAR            MAIN PAGE (top to bottom)
+-----------+      +--------------------------------------------------+
| Regions   |      | Title + source caption                           |
| Period    |      | 1. Why this matters      (hook, context, Q1-Q3)  |
| Indicator |      | KPI header               (4 metrics, deltas)     |
|           |      | 2. Overview              (line, stacked bars)    |
|           |      | 3. Deep dive             (map, bars, scatter,    |
|           |      |                           small multiples)       |
|           |      | 5. What if               (4 sliders, scenario)   |
|           |      | 6. Data quality          (checks, heatmap)       |
|           |      | 7. Insights, next steps  (3 findings)            |
+-----------+      +--------------------------------------------------+
```

The sidebar filters drive the KPIs and sections 2, 3 and 5. Section 7 always compares the first and last complete years, whatever the filters.

## Step by step

| App no. | Section | Role in the story | Message (headline) | Visual | Interaction | Question answered |
|---|---|---|---|---|---|---|
| 1 | 1. Why this matters | **Hook and context** | France is seen as a low-carbon exporter, but regions differ a lot: some supply the country, others import most of what they use. | Text, two columns, info box | Sidebar filters introduced | Why should I care? |
| - | KPI header | **Key numbers** | Where do the selected regions stand today? | 4 metrics: renewable share, CO2 intensity, self-sufficiency, production | Tied to the filters; change vs the first 12 months of the selection | What is the situation now, and is it improving? |
| 2 | 2. Overview | **Change over time** | The selected indicator went from X to Y; nuclear and renewables share the yearly mix. | Line chart (12-month rolling, one grey line per region, bold total); stacked bars by source per year | Hover tooltips, indicator and period from sidebar | Q2: how did it change? |
| 3 | 3. Deep dive: compare regions | **Comparison** | One region ranks first, another last; N regions produce more than they consume. | Choropleth map, ranking bars with reference line, scatter (self-sufficiency vs CO2 intensity, sized by production), small multiples | Hover, radio button (TWh or %) for small multiples | Q1: who produces more than they consume? Q2: how green is each mix? |
| 5 | 5. What if | **Exploration** | The same percentage increase brings very different gains depending on the region's starting point. | 3 metrics with deltas, stacked bars today vs scenario, dashed consumption line | Region select, 4 sliders (solar, wind, nuclear, thermal) | Q3: what if a region built more solar or wind? |
| 6 | 6. Data quality and limitations | **Trust** | The data is consistent enough for monthly comparisons; glitches are documented. | Validation table, missing-values heatmap, limitations list | Hover | Can I trust these numbers? |
| 7 | 7. Key insights and next steps | **Insights and implications** | The mix got cleaner; a few regions power the others; a high renewable share does not mean self-sufficiency. | 3 insight boxes, implications, next steps | None | What should I remember, and what next? |

## Key insights (section 7)

1. **The mix got cleaner**: renewable share up and estimated CO2 intensity of production down between the first and last complete years.
2. **A few regions power the others**: some regions have a self-sufficiency above 100 %, mainly thanks to nuclear.
3. **A high renewable share does not mean self-sufficiency**: a small renewable production gives a high share but little autonomy (Île-de-France as the extreme case).

## Design choices

- One **headline sentence** per section, computed from the filtered data.
- Every chart has a **text description**, labelled axes with units, and a colour-blind-safe palette for the sources.
- Help text on filters and KPIs; every control changes at least one chart.
- Assumptions (fixed emission factors, constant consumption in the what-if, missing values counted as 0) are written next to the results they affect.

## Demo video outline (2 to 4 minutes)

| Time | What to show |
|---|---|
| 0:00 - 0:30 | Hook and questions (section 1), sidebar filters |
| 0:30 - 1:00 | KPI header, change the period to show the deltas |
| 1:00 - 1:45 | Overview: switch the indicator, read the trend and the mix by year |
| 1:45 - 2:30 | Map, ranking, scatter, small multiples (absolute vs share) |
| 2:30 - 3:15 | What-if: add solar in one region, then compare with another region |
| 3:15 - 3:45 | Data quality section and limitations |
| 3:45 - 4:00 | Insights and next steps |
