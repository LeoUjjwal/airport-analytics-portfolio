
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# -------------------------------
# 1. Page configuration
# -------------------------------
# st.set_page_config(
#     page_title="Airport Explorer | Portfolio",
#     page_icon="✈️",
#     layout="wide",
# )

# st.title("✈️ Global Airport Explorer")
# st.caption(
#     "An interactive data analytics portfolio built with "
#     "Python, Pandas, Plotly and Streamlit."
# )


# -------------------------------
# 1. Page configuration and design
# -------------------------------
st.set_page_config(
    page_title="Airport Explorer | Data Portfolio",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom styling
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        h1 {
            font-weight: 750;
            letter-spacing: -1px;
        }

        [data-testid="stMetric"] {
            background-color: var(--secondary-background-color);
            border: 1px solid rgba(128, 128, 128, 0.25);
            padding: 18px;
            border-radius: 12px;
        }

        [data-testid="stMetricValue"] {
            font-size: 1.8rem;
            font-weight: 700;
        }

        section[data-testid="stSidebar"] {
            border-right: 1px solid rgba(128, 128, 128, 0.2);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("✈️ Global Airport Explorer")

st.markdown(
    """
    Explore airport records across cities and countries using
    interactive charts, searchable data, and customizable filters.

    **Project focus:** Data exploration · Data quality ·
    Interactive visualization · Python analytics
    """
)

st.divider()


# -------------------------------
# 2. Load the dataset
# -------------------------------
# DATA_PATH = Path(__file__).parent / "data" / "airports.csv"
DATA_PATH = (
    Path(__file__).parent / "data" / "airports_enriched.csv"
)

@st.cache_data
def load_data(path):
    data = pd.read_csv(path, encoding="utf-8-sig")

    # Remove accidental empty columns from CSV exports
    data = data.loc[
        :, ~data.columns.astype(str).str.match(r"^Unnamed")
    ]

    # Standardize headers and text
    data.columns = data.columns.str.strip()

    required = [
        "City", "Country", "Airport Name",
        "IATA Code", "ICAO Code", "Airport Type"
    ]

    missing = [col for col in required if col not in data.columns]
    if missing:
        raise ValueError(
            f"Missing required columns: {', '.join(missing)}"
        )

    for col in required:
        data[col] = data[col].astype("string").str.strip()

    data = data.dropna(how="all")
    data = data.drop_duplicates()

    return data


try:
    df = load_data(str(DATA_PATH))
except FileNotFoundError:
    st.error(
        "CSV file not found. Put airports.csv inside the data folder."
    )
    st.stop()
except (ValueError, UnicodeDecodeError, pd.errors.ParserError) as exc:
    st.error(f"Could not load the CSV: {exc}")
    st.stop()


# -------------------------------
# 3. Sidebar filters
# -------------------------------
st.sidebar.header("Explore the data")

countries = sorted(df["Country"].dropna().unique().tolist())
types = sorted(df["Airport Type"].dropna().unique().tolist())

selected_countries = st.sidebar.multiselect(
    "Country",
    countries,
    default=countries,
)

selected_types = st.sidebar.multiselect(
    "Airport type",
    types,
    default=types,
)

search_text = st.sidebar.text_input(
    "Search airport, city or code"
).strip().casefold()

filtered = df[
    df["Country"].isin(selected_countries)
    & df["Airport Type"].isin(selected_types)
].copy()

if search_text:
    searchable_columns = [
        "City", "Country", "Airport Name",
        "IATA Code", "ICAO Code"
    ]

    matches = pd.Series(False, index=filtered.index)

    for col in searchable_columns:
        matches |= (
            filtered[col]
            .fillna("")
            .str.casefold()
            .str.contains(search_text, regex=False)
        )

    filtered = filtered[matches]


# -------------------------------
# 4. KPI metrics
# -------------------------------
st.subheader("Portfolio overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Airport records", f"{len(filtered):,}")
col2.metric("Countries", f"{filtered['Country'].nunique():,}")
col3.metric("Cities", f"{filtered['City'].nunique():,}")
col4.metric(
    "Unique IATA codes",
    f"{filtered['IATA Code'].nunique():,}"
)

st.divider()


# -------------------------------
# 5. Charts
# -------------------------------

# -------------------------------
# 5B. Airport records by city
# -------------------------------
st.divider()
st.subheader("City-level airport analysis")

city_counts = (
    filtered.groupby(["Country", "City"])
    .size()
    .reset_index(name="Airport records")
    .sort_values("Airport records", ascending=False)
    .head(15)
)

if not city_counts.empty:
    city_counts["City label"] = (
        city_counts["City"] + ", " + city_counts["Country"]
    )

    fig_city = px.bar(
        city_counts,
        x="Airport records",
        y="City label",
        orientation="h",
        color="Country",
        hover_data=["City", "Country"],
        title="Cities with the Most Airport Records",
        template="plotly_white",
    )

    fig_city.update_layout(
        yaxis={"categoryorder": "total ascending"},
        xaxis_title="Number of airport records",
        yaxis_title="",
        legend_title="Country",
    )

    st.plotly_chart(
        fig_city,
        use_container_width=True,
    )
else:
    st.info("No cities match the selected filters.")


left, right = st.columns(2)

with left:
    st.subheader("Records by country")

    country_counts = (
        filtered.groupby("Country")
        .size()
        .reset_index(name="Airport records")
        .sort_values("Airport records", ascending=False)
        .head(15)
    )

    fig_country = px.bar(
        country_counts,
        x="Airport records",
        y="Country",
        orientation="h",
        color="Airport records",
        color_continuous_scale="Teal",
        template="plotly_white",
    )

    fig_country.update_layout(
        yaxis={"categoryorder": "total ascending"},
        coloraxis_showscale=False,
        xaxis_title="Airport records",
        yaxis_title="",
    )

    st.plotly_chart(fig_country, use_container_width=True)

with right:
    st.subheader("Airport type distribution")

    type_counts = (
        filtered.groupby("Airport Type")
        .size()
        .reset_index(name="Airport records")
    )

    if not type_counts.empty:
        fig_type = px.pie(
            type_counts,
            names="Airport Type",
            values="Airport records",
            hole=0.48,
            template="plotly_white",
        )
        st.plotly_chart(fig_type, use_container_width=True)
    else:
        st.info("No airport types match the selected filters.")


# -----------------------------
# ADVANCED AIRPORT ANALYTICS
# -----------------------------

st.header("Advanced Airport Insights")

# 1. Top 10 countries by airport records
st.subheader("Top 10 Countries by Airport Records")

country_counts = (
    df["Country"]
    .dropna()
    .astype(str)
    .str.strip()
)

country_counts = country_counts[country_counts != ""].value_counts().head(10)

if not country_counts.empty:
    country_chart = country_counts.rename_axis("Country").reset_index(name="Airport Records")

    fig_country = px.bar(
        country_chart,
        x="Airport Records",
        y="Country",
        orientation="h",
        title="Countries with the Most Airport Records",
        text="Airport Records"
    )

    fig_country.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_country, use_container_width=True)
else:
    st.info("No country data is available.")

# 2. Airport code completeness
st.subheader("Airport Code Completeness")

total_records = len(df)

if total_records > 0:
    iata_values = df["IATA Code"].fillna("").astype(str).str.strip()
    icao_values = df["ICAO Code"].fillna("").astype(str).str.strip()

    iata_present = iata_values.ne("") & iata_values.str.lower().ne("nan")
    icao_present = icao_values.ne("") & icao_values.str.lower().ne("nan")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Records", f"{total_records:,}")

    with col2:
        st.metric(
            "With IATA Code",
            f"{iata_present.sum():,}",
            f"{iata_present.mean() * 100:.1f}%"
        )

    with col3:
        st.metric(
            "With ICAO Code",
            f"{icao_present.sum():,}",
            f"{icao_present.mean() * 100:.1f}%"
        )

# 3. Duplicate airport code checks
st.subheader("Potential Duplicate Airport Codes")

iata_duplicates = iata_values[iata_present].duplicated(keep=False)
icao_duplicates = icao_values[icao_present].duplicated(keep=False)

col1, col2 = st.columns(2)

with col1:
    st.metric("Records with Repeated IATA Codes", int(iata_duplicates.sum()))

with col2:
    st.metric("Records with Repeated ICAO Codes", int(icao_duplicates.sum()))

st.caption(
    "Repeated codes are potential data-quality issues, not automatic proof of errors. "
    "Review the airport names and locations before removing any records."
)

# -------------------------------
# 6. Airport data table
# -------------------------------
# st.divider()
# st.subheader("Airport directory")
# st.write(f"Showing {len(filtered):,} matching records.")

# st.dataframe(
#     filtered,
#     use_container_width=True,
#     hide_index=True,
# )

# csv_bytes = filtered.to_csv(index=False).encode("utf-8-sig")

# st.download_button(
#     label="Download filtered airports as CSV",
#     data=csv_bytes,
#     file_name="filtered_airports.csv",
#     mime="text/csv",
# )

# -------------------------------
# 6. Searchable airport directory
# -------------------------------
st.divider()
st.subheader("Airport directory")

st.write(f"Found **{len(filtered):,}** matching airport records.")

if filtered.empty:
    st.warning(
        "No airports match your search. "
        "Try changing your filters or search term."
    )
else:
    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True,
        height=450,
    )

    csv_bytes = filtered.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        label="⬇️ Download filtered data",
        data=csv_bytes,
        file_name="filtered_airports.csv",
        mime="text/csv",
    )


# -------------------------------
# Interactive airport map
# -------------------------------
st.divider()
st.subheader("Explore airports on the world map")

if {"Latitude", "Longitude"}.issubset(filtered.columns):
    map_df = filtered.copy()

    map_df["Latitude"] = pd.to_numeric(
        map_df["Latitude"], errors="coerce"
    )
    map_df["Longitude"] = pd.to_numeric(
        map_df["Longitude"], errors="coerce"
    )

    map_df = map_df.dropna(
        subset=["Latitude", "Longitude"]
    )

    # Exclude invalid geographic coordinates
    map_df = map_df[
        map_df["Latitude"].between(-90, 90)
        & map_df["Longitude"].between(-180, 180)
    ]

    if not map_df.empty:
        fig_map = px.scatter_map(
            map_df,
            lat="Latitude",
            lon="Longitude",
            hover_name="Airport Name",
            hover_data=["City", "Country", "IATA Code"],
            color="Airport Type",
            zoom=1,
            height=550,
        )

        st.plotly_chart(
            fig_map,
            use_container_width=True,
        )
    else:
        st.info("No valid airport coordinates are available.")
else:
    st.info(
        "To enable the world map, add Latitude and Longitude "
        "columns to your CSV using verified airport coordinates."
    )
