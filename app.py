import pandas as pd
import streamlit as st

from sections import conclusions, deep_dives, intro, overview, quality, whatif
from utils.config import LICENSE, METRICS, SOURCE_PAGE
from utils.io import load_data
from utils.prep import kpi_windows, make_tables, overall, summarize

st.set_page_config(page_title="Regional Electricity Mix", page_icon="⚡", layout="wide")


@st.cache_data(show_spinner="Loading data...")
def get_data():
    monthly, quality_table, geojson = load_data()
    return make_tables(monthly), quality_table, geojson


tables, quality_table, geojson = get_data()
monthly = tables["monthly"]

st.title("Who powers France? Electricity mix and self-sufficiency of the regions")
st.caption(
    f"Source: [eCO2mix regional data (RTE)]({SOURCE_PAGE}) - data.gouv.fr - {LICENSE}. "
    "Individual project - Data Visualisation, EFREI."
)

all_regions = sorted(monthly["region"].unique())
months = list(pd.Index(sorted(monthly["month"].unique())))

with st.sidebar:
    st.header("Filters")
    regions = st.multiselect("Regions", all_regions, default=all_regions,
                             help="Metropolitan regions covered by eCO2mix (Corsica is not in the dataset).")
    start, end = st.select_slider(
        "Period (months)", options=months, value=(months[0], months[-1]),
        format_func=lambda d: pd.Timestamp(d).strftime("%Y-%m"),
        help="Monthly data, from January 2013 to the latest consolidated month.",
    )
    metric = st.selectbox(
        "Indicator", list(METRICS), index=0,
        help="Drives the trend line, the map and the ranking.",
    )
    st.markdown("---")
    st.caption("Production = nuclear + hydro + wind + solar + bioenergy + thermal. "
               "Renewables = hydro + wind + solar + bioenergy.")

if not regions:
    st.warning("Select at least one region in the sidebar.")
    st.stop()

start, end = pd.Timestamp(start), pd.Timestamp(end)
regions = tuple(regions)

intro.render()

st.subheader("The numbers at a glance")
(first_start, first_end), (last_start, last_end) = kpi_windows(start, end)
now = overall(summarize(monthly, regions, last_start, last_end))
before = overall(summarize(monthly, regions, first_start, first_end))
compare = (last_start - first_start).days > 330
caption = (f"Last 12 months of the selection ({last_start:%Y-%m} to {last_end:%Y-%m})"
           + (f", change vs the first 12 months ({first_start:%Y-%m} to {first_end:%Y-%m})." if compare
              else ". Select a period longer than 12 months to see changes."))


def delta(column, unit, fmt):
    return f"{now[column] - before[column]:+{fmt}} {unit}" if compare else None


c1, c2, c3, c4 = st.columns(4)
c1.metric("Renewable share", f"{now['renewable_share']:.1f} %", delta("renewable_share", "pts", ".1f"),
          help="Share of hydro, wind, solar and bioenergy in electricity production.")
c2.metric("CO2 intensity", f"{now['co2_intensity']:.0f} g/kWh", delta("co2_intensity", "g/kWh", ".0f"),
          delta_color="inverse", help="Estimated life-cycle gCO2eq per kWh produced (see Data Quality & Limitations).")
c3.metric("Self-sufficiency", f"{now['autonomy']:.0f} %", delta("autonomy", "pts", ".0f"),
          help="Production divided by consumption. Above 100 %, the regions export more than they import.")
c4.metric("Production", f"{now['production_twh']:.0f} TWh", delta("production_twh", "TWh", ".0f"),
          help="Electricity produced over 12 months.")
st.caption(caption)

filters = dict(regions=regions, start=start, end=end, metric=metric)
overview.render(tables, filters)
deep_dives.render(tables, geojson, filters)
whatif.render(tables, filters)
quality.render(tables, quality_table)
conclusions.render(tables, filters)
