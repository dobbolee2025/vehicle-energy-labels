import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd

# Load data
@st.cache_data
def load_data():
    return pd.read_excel("vehicle_energy_labels.xlsx")

data = load_data()

st.title("🚗 Vehicle Energy Label Viewer")

# Manufacturer logos - load from web URLs
manufacturer_logos = {
    "Tesla": "https://upload.wikimedia.org/wikipedia/commons/b/bd/Tesla_Motors.svg",
    "BMW": "https://upload.wikimedia.org/wikipedia/commons/4/44/BMW.svg",
    "Audi": "https://upload.wikimedia.org/wikipedia/commons/7/7d/Audi_logo_detail.svg",
}

# Get sorted manufacturers
manufacturers = sorted(data["Manufacturer"].dropna().unique())

# Sidebar visual menu with logos
with st.sidebar:
    selected_manufacturer = option_menu(
        "Select Manufacturer",
        manufacturers,
        icons=["car"] * len(manufacturers),  # simple placeholder icons
        menu_icon="cast",
        default_index=0,
    )

# Show selected manufacturer logo
logo_url = manufacturer_logos.get(selected_manufacturer, None)
if logo_url:
    st.image(logo_url, width=150)

# Model Range filter
models = (
    data[data["Manufacturer"] == selected_manufacturer]["Model Range"]
    .dropna()
    .unique()
)
selected_model = st.selectbox("Select Model Range", sorted(models))

# Description filter
descriptions = (
    data[
        (data["Manufacturer"] == selected_manufacturer)
        & (data["Model Range"] == selected_model)
    ]["Description"]
    .dropna()
    .unique()
)
selected_description = st.selectbox("Select Description", sorted(descriptions))

# Filter final vehicle
filtered = data[
    (data["Manufacturer"] == selected_manufacturer)
    & (data["Model Range"] == selected_model)
    & (data["Description"] == selected_description)
]

if filtered.empty:
    st.warning("No data found.")
else:
    vehicle = filtered.iloc[0]

    st.header(f"{vehicle['Manufacturer']} {vehicle['Model Range']}")
    st.subheader(vehicle["Description"])

    # Efficiency rating logic
    try:
        co2 = float(vehicle["CO2 g/KM"])
    except:
        co2 = 999

    if co2 <= 50:
        rating = "A"
        progress = 100
    elif co2 <= 90:
        rating = "B"
        progress = 80
    elif co2 <= 130:
        rating = "C"
        progress = 60
    elif co2 <= 170:
        rating = "D"
        progress = 40
    else:
        rating = "E"
        progress = 20

    st.subheader(f"🌱 Efficiency Rating: {rating}")
    st.progress(progress)

    # Key metrics in columns
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("CO2", f"{vehicle['CO2 g/KM']} g/km")
        st.metric("Electric Range", f"{vehicle['WLTP Electric Range (miles)']} mi")

    with col2:
        mpg = vehicle["WLTP MPG (Comb)"] if pd.notnull(vehicle["WLTP MPG (Comb)"]) else "N/A"
        st.metric("MPG", mpg)
        st.metric("Power", f"{vehicle['Power (bhp)']} bhp")

    with col3:
        st.metric("Luggage", f"{vehicle['Luggage Capacity (L)']} L")
        st.metric("NCAP Rating", vehicle["NCAP Rating"])

    st.write(f"💰 **Net Basic Price:** {vehicle['Net Basic Price']}")

    # Download
    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download as CSV",
        data=csv,
        file_name="vehicle_energy_label.csv",
        mime="text/csv",
    )
