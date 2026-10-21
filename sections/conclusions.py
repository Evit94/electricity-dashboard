import pandas as pd
import streamlit as st

from utils.config import SOURCES
from utils.prep import overall, summarize


def render(tables, f):
    monthly = tables["monthly"]
    all_regions = tuple(monthly["region"].unique())
    full_years = monthly.groupby("year")["month"].nunique()
    complete = full_years[full_years == 12].index
    first_year, last_year = int(complete.min()), int(complete.max())

    def year_summary(year, by=("region",)):
        return summarize(monthly, all_regions, pd.Timestamp(year, 1, 1), pd.Timestamp(year, 12, 1), by=by)

    before, after = year_summary(first_year), year_summary(last_year)
    total_before, total_after = overall(before), overall(after)
    after = after.assign(main=after[SOURCES].idxmax(axis=1))
    exporters = after[after["autonomy"] > 100].sort_values("autonomy", ascending=False)
    paris = after[after["region"] == "Île-de-France"].iloc[0]
    greenest_small = after[after["autonomy"] < 50].sort_values("renewable_share", ascending=False).iloc[0]

    st.header("7. Key insights and next steps")
    st.caption(f"Figures below use all 12 regions and compare the full years {first_year} and {last_year}, "
               "whatever the sidebar filters.")
    st.success(
        f"**1. The mix got cleaner.** The renewable share went from {total_before['renewable_share']:.0f} % "
        f"to {total_after['renewable_share']:.0f} % and the estimated CO2 intensity of production from "
        f"{total_before['co2_intensity']:.0f} to {total_after['co2_intensity']:.0f} g/kWh "
        f"between {first_year} and {last_year}."
    )
    st.success(
        f"**2. A few regions power the others.** {len(exporters)} regions produce more than they consume in "
        f"{last_year}: " + ", ".join(f"{r.region} ({r.autonomy:.0f} %)" for r in exporters.itertuples())
        + f". Their main source is {', '.join(sorted(set(exporters['main'])))}."
    )
    st.success(
        f"**3. A high renewable share does not mean self-sufficiency.** {greenest_small['region']} gets "
        f"{greenest_small['renewable_share']:.0f} % of its production from renewables but covers only "
        f"{greenest_small['autonomy']:.0f} % of its consumption. Île-de-France consumes "
        f"{paris['consumption_twh']:.0f} TWh and produces {paris['production_twh']:.0f} TWh."
    )

    st.subheader("Implications")
    st.markdown(
        "- Regional energy plans should look at **volumes**, not only shares: a small renewable production "
        "gives a high share but little autonomy.\n"
        "- Regions that import most of their electricity depend on transmission lines and on the exporting "
        "regions, which matters for grid investment and for resilience.\n"
        "- The what-if tool shows that the same percentage increase brings very different gains depending on "
        "the starting point of the region."
    )
    st.subheader("Next steps")
    st.markdown(
        "- Add hourly data to study when imports happen (peaks, winter evenings).\n"
        "- Join installed capacity and population data to compare regions per inhabitant.\n"
        "- Replace the estimated CO2 intensity with RTE's published emission data.\n"
        "- Add Corsica and overseas regions from another dataset."
    )
    st.caption("Source: RTE eCO2mix regional data via data.gouv.fr (Licence Ouverte v2.0). "
               "Results are descriptive and do not prove causes.")
