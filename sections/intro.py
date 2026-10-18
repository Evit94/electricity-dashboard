import streamlit as st


def render():
    st.header("1. Why this matters")
    st.markdown(
        "France is often described as an electricity exporter with a low-carbon mix. "
        "But electricity is produced and consumed **locally**, and regions are very different: "
        "some host power plants that supply the rest of the country, others import most of what they use. "
        "Understanding this map matters for grid investment, for regional energy plans and for the "
        "debate on where new wind, solar or nuclear capacity should go."
    )
    left, right = st.columns(2)
    with left:
        st.markdown("**Context**")
        st.markdown(
            "- Data: RTE *eCO2mix* regional data, 12 metropolitan regions, half-hourly, 2013 to 2026.\n"
            "- We aggregate it to monthly values (GWh) and compute shares, self-sufficiency and an "
            "estimated CO2 intensity.\n"
            "- Audience: citizens, students and regional decision makers who want a quick, visual "
            "answer without reading energy reports."
        )
    with right:
        st.markdown("**Questions this dashboard answers**")
        st.markdown(
            "1. Which regions produce more electricity than they consume?\n"
            "2. How green is each regional mix, and how did it change?\n"
            "3. What would change if a region built more solar or wind?"
        )
    st.info("Use the sidebar to filter regions, the period and the indicator. All figures update together.")
