import streamlit as st

from utils.config import METRICS, SOURCES
from utils.prep import overall, summarize, yearly_table
from utils.viz import bar_chart, map_chart, phrase, scatter_chart, show, small_multiples


def render(tables, geojson, f):
    col, unit, _ = METRICS[f["metric"]]
    monthly = tables["monthly"]
    summary = summarize(monthly, f["regions"], f["start"], f["end"])
    period = f"{f['start']:%Y-%m} to {f['end']:%Y-%m}"

    st.header("3. Deep dive: comparing regions")
    ranked = summary.sort_values(col, ascending=False)
    top, bottom = ranked.iloc[0], ranked.iloc[-1]
    st.markdown(
        f"**Headline:** for {phrase(f['metric'])} over {period}, **{top['region']}** ranks first "
        f"({top[col]:,.1f} {unit}) and **{bottom['region']}** last ({bottom[col]:,.1f} {unit})."
    )
    left, right = st.columns(2)
    with left:
        show(map_chart(summary, geojson, f["metric"]),
             f"Map of French regions coloured by {phrase(f['metric'])} over {period}.")
    with right:
        show(bar_chart(summary, f["metric"], overall(summary)[col]),
             f"Horizontal bars ranking the selected regions by {phrase(f['metric'])}; "
             "a dashed line marks the value for all selected regions together.")

    exporters = summary[summary["autonomy"] > 100].assign(main=lambda d: d[SOURCES].idxmax(axis=1))
    st.markdown(
        f"**Headline:** {len(exporters)} of {len(summary)} selected regions produce more than they consume. "
        + (", ".join(f"{r.region} ({r.main})" for r in exporters.itertuples()) + "." if len(exporters) else "")
    )
    show(
        scatter_chart(summary),
        "Scatter plot of self-sufficiency (x) against CO2 intensity (y), one bubble per region, sized by "
        "production and coloured by its main source.",
    )

    st.subheader("Production mix of each region over time")
    mode = st.radio("Display", ["Absolute (TWh)", "Share (%)"], horizontal=True,
                    help="Absolute shows the size of each region, share shows the structure of its mix.")
    yearly = yearly_table(monthly, f["regions"], f["start"], f["end"])
    if yearly.empty:
        st.info("Select a period that includes at least one full calendar year to see the yearly mix.")
        return
    show(
        small_multiples(yearly, share=mode.startswith("Share")),
        "One small area chart per region showing the yearly production mix by source.",
    )
    st.caption("Only complete calendar years inside the selected period are shown.")
