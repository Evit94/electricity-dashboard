import streamlit as st

from utils.config import METRICS, SOURCES
from utils.prep import selection_series, yearly_table
from utils.viz import line_chart, mix_by_year_chart, phrase, show


def render(tables, f):
    col, unit, _ = METRICS[f["metric"]]
    rolling, monthly = tables["rolling"], tables["monthly"]
    total = selection_series(rolling, f["regions"], f["start"], f["end"])

    st.header("2. Overview: how did the system change?")
    if total.empty:
        st.info("Trends use 12-month rolling values, so the selected period must end at least 12 months "
                "after January 2013. Extend the period in the sidebar.")
        return
    first, last = total.iloc[0], total.iloc[-1]
    st.markdown(
        f"**Headline:** {phrase(f['metric'])} of the selected regions went from "
        f"**{first[col]:,.1f} {unit}** ({first['month']:%b %Y}) to **{last[col]:,.1f} {unit}** "
        f"({last['month']:%b %Y})."
    )
    by_region = rolling[rolling["region"].isin(f["regions"]) & rolling["month"].between(f["start"], f["end"])]
    show(
        line_chart(by_region, total, f["metric"]),
        f"Line chart of {phrase(f['metric'])} from {first['month']:%Y-%m} to {last['month']:%Y-%m}. "
        "Each grey line is a region, the thick blue line is the total of the selected regions.",
    )

    yearly = yearly_table(monthly, f["regions"], f["start"], f["end"])
    if yearly.empty:
        st.info("Select a period that includes at least one full calendar year to see the yearly mix.")
        return
    year = yearly["year"].max()
    mix = yearly[yearly["year"] == year][SOURCES].sum()
    st.markdown(
        f"**Headline:** in {year}, nuclear provided **{100 * mix['nuclear'] / mix.sum():.0f} %** and "
        f"renewables **{100 * mix[['hydro', 'wind', 'solar', 'bioenergy']].sum() / mix.sum():.0f} %** "
        "of the production of the selected regions."
    )
    show(
        mix_by_year_chart(yearly),
        "Stacked bars of yearly electricity production by source for the selected regions.",
    )
    st.caption("Only complete calendar years inside the selected period are shown.")
