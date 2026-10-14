from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
MONTHLY_FILE = DATA_DIR / "eco2mix_monthly.csv"
QUALITY_FILE = DATA_DIR / "quality.csv"
GEO_FILE = DATA_DIR / "regions.geojson"

ODRE_URL = (
    "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/"
    "eco2mix-regional-cons-def/exports/csv"
)
GEO_URL = (
    "https://static.data.gouv.fr/resources/"
    "contours-des-communes-de-france-simplifie-avec-regions-et-departement-doutre-mer-rapproches/"
    "20210523-142617/a-reg2021.json"
)
SOURCE_PAGE = "https://www.data.gouv.fr/datasets/donnees-eco2mix-regionales-consolidees-et-definitives"
LICENSE = "Licence Ouverte v2.0 (Etalab)"

REGION_CODES = ["84", "27", "53", "24", "44", "32", "28", "75", "76", "52", "93", "11"]
METROPOLE_CODES = REGION_CODES + ["94"]

RAW_RENAME = {
    "consommation": "consumption",
    "thermique": "thermal",
    "nucleaire": "nuclear",
    "eolien": "wind",
    "solaire": "solar",
    "hydraulique": "hydro",
    "bioenergies": "bioenergy",
    "pompage": "pumping",
    "ech_physiques": "exchanges",
}
RAW_COLUMNS = ["code_insee_region", "libelle_region", "date_heure"] + list(RAW_RENAME)

SOURCES = ["nuclear", "hydro", "wind", "solar", "bioenergy", "thermal"]
RENEWABLES = ["hydro", "wind", "solar", "bioenergy"]
GWH_COLUMNS = ["consumption", *SOURCES, "pumping", "exchanges"]

SOURCE_COLORS = {
    "nuclear": "#E69F00",
    "hydro": "#0072B2",
    "wind": "#56B4E9",
    "solar": "#B8860B",
    "bioenergy": "#009E73",
    "thermal": "#444444",
}

# Life-cycle emission factors in gCO2eq/kWh (IPCC AR5, WG3, Annex III, medians)
CO2_FACTORS = {
    "nuclear": 12,
    "hydro": 24,
    "wind": 11,
    "solar": 41,
    "bioenergy": 230,
    "thermal": 490,
}

METRICS = {
    "Renewable share of production": ("renewable_share", "%", "YlGn"),
    "Low-carbon share of production": ("low_carbon_share", "%", "YlGn"),
    "Self-sufficiency (production / consumption)": ("autonomy", "%", "Blues"),
    "CO2 intensity of production": ("co2_intensity", "gCO2eq/kWh", "YlOrRd"),
    "Electricity production": ("production_twh", "TWh", "Purples"),
    "Electricity consumption": ("consumption_twh", "TWh", "Purples"),
}
