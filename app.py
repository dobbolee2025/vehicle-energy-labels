import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd

@st.cache_data
def load_data():
    return pd.read_excel("vehicle_energy_labels.xlsx")

data = load_data()

st.title("🚗 Vehicle Energy Label Viewer")

# Manufacturer logos (PNG URLs for reliability)
manufacturer_logos = {
    "Tesla": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bd/Tesla_Motors.svg/512px-Tesla_Motors.svg.png",
    "BMW": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/BMW.svg/512px-BMW.svg.png",
    "Audi": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7d/Audi_logo_detail.svg/512px-Audi_logo_detail.svg.png",
    "Hyundai": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/Hyundai_logo.svg/512px-Hyundai_logo.svg.png",
}

manufacturers = sorted(data["Manufacturer"].dropna().unique())

with st.sidebar:
    selected_manufacturer = option_menu(
        "Select Manufacturer",
        manufacturers,
        icons=["car"] * len(manufacturers),
        menu_icon="cast",
        default_index=0,
    )

models = (
    data[data["Manufacturer"] == selected_manufacturer]["Model Range"]
    .dropna()
    .unique()
)
selected_model = st.selectbox("Select Model Range", sorted(models))

descriptions = (
    data[
        (data["Manufacturer"] == selected_manufacturer)
        & (data["Model Range"] == selected_model)
    ]["Description"]
    .dropna()
    .unique()
)
selected_description = st.selectbox("Select Description", sorted(descriptions))

filtered = data[
    (data["Manufacturer"] == selected_manufacturer)
    & (data["Model Range"] == selected_model)
    & (data["Description"] == selected_description)
]

if filtered.empty:
    st.warning("No data found.")
else:
    vehicle = filtered.iloc[0]

    # Show Manufacturer logo
    logo_url = manufacturer_logos.get(selected_manufacturer)
    if logo_url:
        col_logo, col_title = st.columns([1,5])
        with col_logo:
            st.image(logo_url, width=120)
        with col_title:
            st.header(f"{vehicle['Manufacturer']} {vehicle['Model Range']}")
            st.subheader(vehicle["Description"])
    else:
        st.header(f"{vehicle['Manufacturer']} {vehicle['Model Range']}")
        st.subheader(vehicle["Description"])

    # Compute Efficiency Rating
    try:
        co2 = float(vehicle["CO2 g/KM"])
        co2_score = max(0, min(100, 100 - (co2 / 2)))
    except:
        co2_score = 50

    mpg = vehicle["WLTP MPG (Comb)"]
    electric_range = vehicle["WLTP Electric Range (miles)"]
    if pd.notnull(mpg):
        mpg_score = min(100, mpg)
        mpg_label = f"{mpg} MPG"
    elif pd.notnull(electric_range):
        mpg_score = min(100, (electric_range / 4))
        mpg_label = f"{electric_range} mi (electric)"
    else:
        mpg_score = 50
        mpg_label = "N/A"

    try:
        tco = float(vehicle["TCO"])
        tco_score = max(0, min(100, 100 - (tco / 1000)))
    except:
        tco_score = 50

    efficiency_score = (co2_score + mpg_score + tco_score) / 3

    if efficiency_score >= 80:
        rating = "A"
        color = "green"
    elif efficiency_score >= 65:
        rating = "B"
        color = "lightgreen"
    elif efficiency_score >= 50:
        rating = "C"
        color = "yellow"
    elif efficiency_score >= 35:
        rating = "D"
        color = "orange"
    elif efficiency_score >= 20:
        rating = "E"
        color = "red"
    else:
        rating = "F"
        color = "darkred"

    st.markdown(
        f"<h4 style='color:{color};'>🌱 Efficiency Rating: {rating} (Score: {efficiency_score:.1f})</h4>",
        unsafe_allow_html=True,
    )

    with st.expander("ℹ️ How we calculate this"):
        st.write(f"""
        The **Efficiency Rating** is based on:
        - **CO2 Output:** {vehicle['CO2 g/KM']} g/km
        - **MPG or Electric Range:** {mpg_label}
        - **TCO:** £{vehicle['TCO']}
        """)

    st.progress(efficiency_score / 100)

    # Metrics with emojis
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("🌿 CO2", f"{vehicle['CO2 g/KM']} g/km")
        st.metric("⚡ MPG / Range", mpg_label)

    with col2:
        st.metric("🔧 Power", f"{vehicle['Power (bhp)']} bhp")
        st.metric("🧳 Luggage", f"{vehicle['Luggage Capacity (L)']} L")

    with col3:
        st.metric("🛡️ NCAP", vehicle["NCAP Rating"])
        st.metric("🏎️ 0–62 mph", f"{vehicle['0-62 mph (secs)']} sec")

    # BiK %
    st.metric("💼 BiK %", f"{vehicle['BIK% Year 1']}%")

    st.markdown(f"💰 **Net Basic Price:** {vehicle['Net Basic Price']}")

    # Real Print to PDF button using JS
    st.markdown(
        """
        <button onclick="window.print()" style="background-color:#4CAF50;color:white;padding:10px 20px;border:none;border-radius:4px;cursor:pointer;font-size:16px;">
            🖨️ Print or Save as PDF
        </button>
        """,
        unsafe_allow_html=True
    )
