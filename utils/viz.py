import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.config import METRICS, SOURCE_COLORS, SOURCES

GRAY = "#9AA0A6"
BLUE = "#1F4E79"


def short(metric):
    return metric.split(" (")[0]


def phrase(metric):
    text = short(metric)
    return text if text.startswith("CO2") else text[0].lower() + text[1:]


def style(fig, height=450):
    fig.update_layout(
        template="plotly_white",
        font=dict(size=14),
        height=height,
        margin=dict(l=10, r=10, t=40, b=10),
        legend_title_text="",
    )
    return fig


def show(fig, alt):
    st.plotly_chart(fig, width="stretch")
    st.caption(f"Text description: {alt}")


def long_mix(df, index_cols):
    long = df.melt(id_vars=index_cols, value_vars=SOURCES, var_name="source", value_name="GWh")
    long["TWh"] = long["GWh"] / 1000
    return long


def line_chart(by_region, total, metric):
    col, unit, _ = METRICS[metric]
    fig = go.Figure()
    for region, g in by_region.groupby("region"):
        fig.add_trace(
            go.Scatter(
                x=g["month"], y=g[col], mode="lines", showlegend=False,
                line=dict(color=GRAY, width=1),
                hovertemplate=f"{region}<br>%{{x|%b %Y}}: %{{y:,.1f}} {unit}<extra></extra>",
            )
        )
    fig.add_trace(
        go.Scatter(
            x=total["month"], y=total[col], mode="lines", name="Selected regions (total)",
            line=dict(color=BLUE, width=4),
            hovertemplate=f"Selected regions<br>%{{x|%b %Y}}: %{{y:,.1f}} {unit}<extra></extra>",
        )
    )
    last = total.iloc[-1]
    fig.add_annotation(
        x=last["month"], y=last[col], text=f"{last[col]:,.1f} {unit}",
        showarrow=True, ax=-50, ay=-40, font=dict(color=BLUE),
    )
    if col == "autonomy":
        fig.add_trace(
            go.Scatter(
                x=[total["month"].min(), total["month"].max()], y=[100, 100], mode="lines",
                name="100 % = produces what it consumes", line=dict(color="#B22222", dash="dash"),
                hoverinfo="skip",
            )
        )
    fig.update_layout(
        xaxis_title="Month (value computed over the 12 months ending that month)",
        yaxis_title=f"{short(metric)} ({unit})",
        showlegend=True,
    )
    return style(fig)


def mix_by_year_chart(yearly):
    long = long_mix(yearly.groupby("year", as_index=False)[SOURCES].sum(), ["year"])
    fig = px.bar(
        long, x="year", y="TWh", color="source",
        color_discrete_map=SOURCE_COLORS, category_orders={"source": SOURCES},
        labels={"year": "Year", "TWh": "Electricity production (TWh)", "source": "Source"},
    )
    fig.update_traces(hovertemplate="%{x} - %{fullData.name}: %{y:,.1f} TWh<extra></extra>")
    fig.update_xaxes(dtick=1)
    totals = long.groupby("year")["TWh"].sum()
    if len(totals) >= 3:
        low = totals.idxmin()
        fig.add_annotation(x=low, y=totals[low], text=f"Lowest production: {low}", showarrow=True, ax=0, ay=-40)
    return style(fig)


def map_chart(summary, geojson, metric):
    col, unit, scale = METRICS[metric]
    fig = px.choropleth(
        summary, geojson=geojson, locations="region_code", featureidkey="properties.reg",
        color=col, color_continuous_scale=scale, hover_name="region",
        hover_data={"region_code": False, col: ":,.1f", "production_twh": ":,.1f", "consumption_twh": ":,.1f"},
        labels={col: f"{short(metric)} ({unit})", "production_twh": "Production (TWh)",
                "consumption_twh": "Consumption (TWh)"},
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(coloraxis_colorbar_title=unit)
    return style(fig, 520)


def bar_chart(summary, metric, reference):
    col, unit, _ = METRICS[metric]
    data = summary.sort_values(col)
    fig = px.bar(
        data, x=col, y="region", orientation="h", text=col, color_discrete_sequence=[BLUE],
        labels={col: f"{short(metric)} ({unit})", "region": "Region"},
    )
    fig.update_traces(texttemplate="%{x:,.1f}", textposition="outside", cliponaxis=False,
                      hovertemplate=f"%{{y}}: %{{x:,.1f}} {unit}<extra></extra>")
    fig.add_vline(x=reference, line_dash="dash", line_color="#B22222",
                  annotation_text="All selected regions", annotation_position="bottom right")
    return style(fig, 520)


def scatter_chart(summary):
    data = summary.assign(dominant_source=summary[SOURCES].idxmax(axis=1))
    fig = px.scatter(
        data, x="autonomy", y="co2_intensity", size="production_twh", color="dominant_source",
        text="region", hover_name="region", size_max=45, color_discrete_map=SOURCE_COLORS,
        hover_data={"autonomy": ":.0f", "co2_intensity": ":.0f", "production_twh": ":,.1f", "dominant_source": False},
        labels={"autonomy": "Self-sufficiency (%)", "co2_intensity": "CO2 intensity (gCO2eq/kWh)",
                "production_twh": "Production (TWh)", "dominant_source": "Main source"},
    )
    fig.update_traces(textposition="top center", textfont_size=11)
    fig.add_vline(x=100, line_dash="dash", line_color="#B22222",
                  annotation_text="Production = consumption", annotation_position="top")
    return style(fig, 520)


def small_multiples(yearly, share):
    long = long_mix(yearly, ["region", "year"])
    rows = -(-yearly["region"].nunique() // 4)
    fig = px.area(
        long, x="year", y="TWh", color="source", facet_col="region", facet_col_wrap=4,
        color_discrete_map=SOURCE_COLORS, category_orders={"source": SOURCES},
        groupnorm="percent" if share else None,
        labels={"year": "Year", "TWh": "Share of production (%)" if share else "Production (TWh)",
                "source": "Source"},
    )
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_xaxes(tickformat="d", nticks=3)
    fig.update_traces(hovertemplate="%{x} - %{fullData.name}: %{y:,.1f}<extra></extra>")
    return style(fig, 230 * rows + 80)


def scenario_chart(base, scenario, consumption_twh):
    rows = [("Today (last 12 months)", base), ("Scenario", scenario)]
    fig = go.Figure()
    for source in SOURCES:
        fig.add_trace(
            go.Bar(
                x=[name for name, _ in rows], y=[values[source] / 1000 for _, values in rows],
                name=source, marker_color=SOURCE_COLORS[source],
                hovertemplate=f"{source}: %{{y:,.1f}} TWh<extra></extra>",
            )
        )
    fig.add_hline(y=consumption_twh, line_dash="dash", line_color="#B22222",
                  annotation_text="Consumption (assumed constant)", annotation_position="top left")
    fig.update_layout(barmode="stack", yaxis_title="Electricity production (TWh per year)", xaxis_title="")
    return style(fig, 420)


def missing_heatmap(quality):
    cols = [c for c in quality.columns if c.startswith("missing_")]
    matrix = quality.set_index("region")[cols]
    matrix.columns = [c.replace("missing_", "") for c in cols]
    fig = px.imshow(
        matrix, text_auto=".1f", aspect="auto", color_continuous_scale="Reds",
        labels={"x": "Column", "y": "Region", "color": "Missing (%)"},
    )
    return style(fig, 460)
