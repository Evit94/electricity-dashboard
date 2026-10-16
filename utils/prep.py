import pandas as pd
import streamlit as st

from utils.config import (
    CO2_FACTORS,
    GWH_COLUMNS,
    RAW_RENAME,
    RENEWABLES,
    SOURCES,
)

VALUE_COLUMNS = list(RAW_RENAME.values())


def clean_raw(raw):
    df = raw.rename(columns=RAW_RENAME).rename(
        columns={"code_insee_region": "region_code", "libelle_region": "region"}
    )
    df["region_code"] = df["region_code"].astype(str).str.zfill(2)
    df["date_heure"] = pd.to_datetime(df["date_heure"], utc=True)
    expected = int((df["date_heure"].max() - df["date_heure"].min()) / pd.Timedelta("30min")) + 1
    numeric = df[VALUE_COLUMNS].apply(pd.to_numeric, errors="coerce")
    stats = {
        "region": df["region"].iloc[0],
        "region_code": df["region_code"].iloc[0],
        "rows": len(df),
        "duplicates": int(df["date_heure"].duplicated().sum()),
        "gap_timestamps": expected - df["date_heure"].nunique(),
        "non_numeric": int((numeric.isna() & df[VALUE_COLUMNS].notna()).sum().sum()),
        "negative_values": int((numeric[["consumption", *SOURCES]] < 0).sum().sum()),
    }
    for col in VALUE_COLUMNS:
        stats[f"missing_{col}"] = round(100 * numeric[col].isna().mean(), 2)
    df[VALUE_COLUMNS] = numeric
    return df.drop_duplicates(subset="date_heure"), stats


def to_monthly(df):
    local = df["date_heure"].dt.tz_convert("Europe/Paris").dt.tz_localize(None)
    df = df.assign(month=local.dt.to_period("M").dt.to_timestamp())
    grouped = df.groupby(["region_code", "region", "month"])
    out = grouped[VALUE_COLUMNS].sum() * 0.5 / 1000  # MW per half-hour -> GWh
    out["n_obs"] = grouped.size()
    return out.reset_index()


def add_indicators(df):
    df = df.copy()
    df["production"] = df[SOURCES].sum(axis=1)
    df["production_twh"] = df["production"] / 1000
    df["consumption_twh"] = df["consumption"] / 1000
    df["renewable_share"] = 100 * df[RENEWABLES].sum(axis=1) / df["production"]
    df["low_carbon_share"] = 100 * (df["production"] - df["thermal"]) / df["production"]
    df["autonomy"] = 100 * df["production"] / df["consumption"]
    emissions = sum(df[s] * f for s, f in CO2_FACTORS.items())  # GWh x g/kWh = tonnes
    df["co2_intensity"] = emissions / df["production"]
    df["balance_gap_pct"] = (
        100 * (df["consumption"] - df["production"] - df["pumping"] - df["exchanges"]).abs() / df["consumption"]
    )
    return df


def make_tables(monthly):
    monthly = monthly.sort_values(["region_code", "month"]).reset_index(drop=True)
    monthly["year"] = monthly["month"].dt.year
    rolled = monthly.groupby("region_code")[GWH_COLUMNS].rolling(12).sum()
    rolled = rolled.reset_index(level=0, drop=True)
    rolling = monthly[["region_code", "region", "month"]].join(rolled).dropna()
    return {"monthly": add_indicators(monthly), "rolling": add_indicators(rolling)}


@st.cache_data(show_spinner=False)
def summarize(monthly, regions, start, end, by=("region",)):
    sel = monthly[monthly["region"].isin(regions) & monthly["month"].between(start, end)]
    if sel.empty:
        return sel
    keys = ["region_code", *by] if "region" in by else list(by)
    grouped = sel.groupby(keys)[GWH_COLUMNS].sum().reset_index()
    return add_indicators(grouped)


def yearly_table(monthly, regions, start, end):
    yearly = summarize(monthly, regions, start, end, by=("region", "year"))
    if yearly.empty:
        return yearly
    months = monthly[monthly["month"].between(start, end)].groupby("year")["month"].nunique()
    return yearly[yearly["year"].isin(months[months == 12].index)]


def overall(df):
    return add_indicators(df[GWH_COLUMNS].sum().to_frame().T).iloc[0]


def selection_series(rolling, regions, start, end):
    sel = rolling[rolling["region"].isin(regions) & rolling["month"].between(start, end)]
    if sel.empty:
        return sel
    return add_indicators(sel.groupby("month")[GWH_COLUMNS].sum().reset_index())


def kpi_windows(start, end):
    last_start = max(start, end - pd.DateOffset(months=11))
    first_end = min(end, start + pd.DateOffset(months=11))
    return (start, first_end), (last_start, end)
