import pandas as pd
import streamlit as st

from utils.config import SOURCES
from utils.prep import add_indicators, kpi_windows, overall, summarize
from utils.viz import scenario_chart, show


def render(tables, f):
    st.header("5. What if a region changed its mix?")
    st.markdown("**Headline:** the same percentage increase brings very different gains depending on the "
                "region's starting point. Compare Île-de-France with Occitanie.")

    left, right = st.columns([1, 2])
    with left:
        scope = st.selectbox("Region", ["All selected regions", *f["regions"]])
        solar = st.slider("Solar production change (%)", -50, 300, 100, step=10)
        wind = st.slider("Wind production change (%)", -50, 300, 50, step=10)
        nuclear = st.slider("Nuclear production change (%)", -100, 100, 0, step=10)
        thermal = st.slider("Thermal production change (%)", -100, 100, -50, step=10)

    regions = f["regions"] if scope == "All selected regions" else (scope,)
    _, (last_start, last_end) = kpi_windows(f["start"], f["end"])
    base = overall(summarize(tables["monthly"], regions, last_start, last_end))

    changes = {"solar": solar, "wind": wind, "nuclear": nuclear, "thermal": thermal}
    scenario = base.copy()
    for source, pct in changes.items():
        scenario[source] = base[source] * (1 + pct / 100)
    scenario = add_indicators(pd.DataFrame([scenario])).iloc[0]

    with right:
        c1, c2, c3 = st.columns(3)
        c1.metric("Self-sufficiency", f"{scenario['autonomy']:.0f} %", f"{scenario['autonomy'] - base['autonomy']:+.0f} pts")
        c2.metric("Renewable share", f"{scenario['renewable_share']:.1f} %",
                  f"{scenario['renewable_share'] - base['renewable_share']:+.1f} pts")
        c3.metric("CO2 intensity", f"{scenario['co2_intensity']:.0f} g/kWh",
                  f"{scenario['co2_intensity'] - base['co2_intensity']:+.0f} g/kWh", delta_color="inverse")
        show(
            scenario_chart(base[SOURCES], scenario[SOURCES], base["consumption_twh"]),
            f"Stacked bars compare yearly production by source for {scope.lower()} today and in the scenario; "
            "a dashed line shows consumption, assumed constant.",
        )

    st.caption(
        "Assumptions: each source is scaled proportionally from the last 12 months of the selected period; "
        "consumption stays constant; hourly balance, storage, grid limits and installed capacity are ignored; "
        "emission factors are fixed. This is an illustration, not a forecast."
    )
