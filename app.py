import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd

# Load data
@st.cache_data
def load_data():
    return pd.read_excel("vehicle_energy_labels.xlsx")

data = load_data()

st.title("🚗 Vehicle Energy Label Viewer")

# Manufacturer logos
manufacturer_logos = {
    "Tesla": "https://upload.wikimedia.org/wikipedia/commons/b/bd/Tesla_Motors.svg",
    "BMW": "https://upload.wikimedia.org/wikipedia/commons/4/44/BMW.svg",
    "Audi": "https://upload.wikimedia.org/wikipedia/commons/7/7d/Audi_logo_detail.svg",
    "Hyundai": "https://upload.wikimedia.org/wikipedia/commons/4/45/Hyundai_logo.svg",
    # Add more brands as needed
}

# Sidebar menu
manufacturers = sorted(data["Manufacturer"].dropna().unique())

with st.sidebar:
    selected_manufacturer = option_menu(
        "Select Manufacturer",
        manufacturers,
        icons=["car"] * len(manufacturers),
        menu_icon="cast",
        default_index=0,
    )

# Model Range
models = (
    data[data["Manufacturer"] == selected_manufacturer]["Model Range"]
    .dropna()
    .unique()
)
selected_model = st.selectbox("Select Model Range", sorted(models))

# Description
descriptions = (
    data[
        (data["Manufacturer"] == selected_manufacturer)
        & (data["Model Range"] == selected_model)
    ]["Description"]
    .dropna()
    .unique()
)
selected_description = st.selectbox("Select Description", sorted(descriptions))

# Filter
filtered = data[
    (data["Manufacturer"] == selected_manufacturer)
    & (data["Model Range"] == selected_model)
    & (data["Description"] == selected_description)
]

if filtered.empty:
    st.warning("No data found.")
else:
    vehicle = filtered.iloc[0]

    # Manufacturer logo
    logo_url = manufacturer_logos.get(selected_manufacturer)
    if logo_url:
        col_logo, col_title = st.columns([1,5])
        with col_logo:
            st.image(logo_url, width=80)
        with col_title:
            st.header(f"{vehicle['Manufacturer']} {vehicle['Model Range']}")
            st.subheader(vehicle["Description"])
    else:
        st.header(f"{vehicle['Manufacturer']} {vehicle['Model Range']}")
        st.subheader(vehicle["Description"])

    # Efficiency rating
    try:
        co2 = float(vehicle["CO2 g/KM"])
    except:
        co2 = 999

    if co2 <= 50:
        rating = "A"
        progress = 100
        color = "green"
        description = "Best efficiency"
    elif co2 <= 90:
        rating = "B"
        progress = 80
        color = "lightgreen"
        description = "Very good"
    elif co2 <= 130:
        rating = "C"
        progress = 60
        color = "yellow"
        description = "Moderate"
    elif co2 <= 170:
        rating = "D"
        progress = 40
        color = "orange"
        description = "Poor"
    else:
        rating = "E"
        progress = 20
        color = "red"
        description = "Very poor"

    st.markdown(
        f"<h4 style='color:{color};'>🌱 Efficiency Rating: {rating}</h4>",
        unsafe_allow_html=True,
    )
    with st.expander("ℹ️ What does this mean?"):
        st.write("""
        **Efficiency Rating Bands (CO2 g/km):**
        - A: ≤50 (Best)
        - B: 51–90
        - C: 91–130
        - D: 131–170
        - E: >170
        """)
    
    st.progress(progress)

    # Determine MPG/Range
    wltp_mpg = vehicle["WLTP MPG (Comb)"]
    electric_range = vehicle["WLTP Electric Range (miles)"]
    if pd.notnull(wltp_mpg):
        mpg_display = f"{wltp_mpg}"
    elif pd.notnull(electric_range):
        mpg_display = f"{electric_range} mi (electric)"
    else:
        mpg_display = "N/A"

    # Columns with icons
    col1, col2, col3 = st.columns(3)

    with col1:
        st.image("https://upload.wikimedia.org/wikipedia/commons/4/45/CO2_icon.svg", width=30)
        st.metric("CO2", f"{vehicle['CO2 g/KM']} g/km")

        st.image("https://upload.wikimedia.org/wikipedia/commons/4/4e/Electric_vehicle_charging_icon.png", width=30)
        st.metric("MPG / Range", mpg_display)

    with col2:
        st.image("https://upload.wikimedia.org/wikipedia/commons/0/0b/Engine_icon.png", width=30)
        st.metric("Power", f"{vehicle['Power (bhp)']} bhp")

        st.image("https://upload.wikimedia.org/wikipedia/commons/2/2c/Suitcase_icon.png", width=30)
        st.metric("Luggage", f"{vehicle['Luggage Capacity (L)']} L")

    with col3:
        st.image("https://upload.wikimedia.org/wikipedia/commons/f/f0/Car_Crash_Test_icon.png", width=30)
        st.metric("NCAP", vehicle["NCAP Rating"])

        st.image("https://upload.wikimedia.org/wikipedia/commons/b/bd/Speedometer_icon.png", width=30)
        st.metric("0–62 mph", f"{vehicle['0-62 mph (secs)']} sec")

    st.image("https://upload.wikimedia.org/wikipedia/commons/4/4e/Currency_icon.png", width=30)
    st.markdown(f"💰 **Net Basic Price:** {vehicle['Net Basic Price']}")

    # Download
    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download as CSV",
        data=csv,
        file_name="vehicle_energy_label.csv",
        mime="text/csv",
    )
