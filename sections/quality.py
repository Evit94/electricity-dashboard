import pandas as pd
import streamlit as st

from utils.viz import missing_heatmap, show


def render(tables, quality):
    monthly = tables["monthly"]
    expected_obs = monthly["month"].dt.days_in_month * 48
    incomplete = int(((monthly["n_obs"] - expected_obs).abs() > 4).sum())
    max_gap = monthly["balance_gap_pct"].max()
    median_gap = monthly["balance_gap_pct"].median()

    st.header("6. Data quality and limitations")
    st.markdown("**Headline:** the data is complete and consistent enough for monthly comparisons; "
                "the glitches below are documented and do not change the monthly picture.")
    checks = pd.DataFrame(
        [
            ("Rows analysed (half-hours, all regions)", f"{quality['rows'].sum():,}", "Info",
             "No sampling: every row is used."),
            ("Duplicated timestamps", f"{quality['duplicates'].sum():,}",
             "OK" if quality["duplicates"].sum() == 0 else "Warning",
             "Found around the March daylight-saving change; duplicates are removed."),
            ("Missing half-hour timestamps", f"{quality['gap_timestamps'].sum():,}",
             "OK" if quality["gap_timestamps"].sum() == 0 else "Warning",
             "Mirror of the duplicates (October change); impact on monthly totals is negligible."),
            ("Non-numeric values in numeric columns", f"{quality['non_numeric'].sum():,}",
             "OK" if quality["non_numeric"].sum() == 0 else "Warning",
             "Text such as '-' or 'ND' in the wind column; treated as missing."),
            ("Negative production values", f"{quality['negative_values'].sum():,}",
             "OK" if quality["negative_values"].sum() == 0 else "Warning",
             "Net values (e.g. solar plants consuming at night); kept as they are."),
            ("Region-months with missing or extra half-hours", f"{incomplete:,}",
             "OK" if incomplete == 0 else "Warning", "Tolerance of 4 half-hours for daylight-saving changes."),
            ("Energy balance gap: consumption vs production + pumping + exchanges",
             f"median {median_gap:.2f} %, worst month {max_gap:.1f} %", "OK" if max_gap < 5 else "Warning",
             "Checks that the columns are consistent with each other."),
        ],
        columns=["Check", "Result", "Status", "How it is handled"],
    )
    st.dataframe(checks, hide_index=True, width="stretch")

    st.markdown("**Missing values per column and region (% of half-hours)**")
    show(missing_heatmap(quality), "Heatmap of the share of missing values for each region and column.")

    st.markdown(
        "**Limitations**\n"
        "- Missing source values are treated as zero in the sums. "
        "For nuclear and pumping, they mostly mean that the region has no reactor or no pumped storage.\n"
        "- Data up to December 2025 is *final*; later months are *consolidated* and can still be revised.\n"
        "- Corsica and overseas regions are not in this dataset.\n"
        "- Self-sufficiency compares production and consumption, not actual flows between regions.\n"
        "- CO2 intensity is estimated with fixed life-cycle emission factors per source (IPCC AR5 medians). "
        "It describes local production, not the electricity actually consumed, and it is not RTE's own CO2 figure.\n"
        "- The dashboard shows patterns in aggregated data, not causes."
    )
