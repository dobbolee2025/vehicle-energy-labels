import streamlit as st
import pandas as pd

# Load data
@st.cache_data
def load_data():
    return pd.read_excel("vehicle_energy_labels.xlsx")

data = load_data()

st.title("🚗 Vehicle Energy Label Viewer")

# Manufacturer logos mapping
manufacturer_logos = {
    "Tesla": "images/tesla_logo.png",
    "BMW": "images/bmw_logo.png",
    "Audi": "images/audi_logo.png",
    # Add more as needed
}

# Sidebar Manufacturer search bar with logo
manufacturers = sorted(data["Manufacturer"].dropna().unique())

selected_manufacturer = st.sidebar.selectbox("Select Manufacturer", manufacturers)

# Display Manufacturer logo
if selected_manufacturer in manufacturer_logos:
    st.image(manufacturer_logos[selected_manufacturer], width=150)

# Model Range
models = (
    data[data["Manufacturer"] == selected_manufacturer]["Model Range"]
    .dropna()
    .unique()
)
selected_model = st.sidebar.selectbox("Model Range", sorted(models))

# Description
descriptions = (
    data[
        (data["Manufacturer"] == selected_manufacturer)
        & (data["Model Range"] == selected_model)
    ]["Description"]
    .dropna()
    .unique()
)
selected_description = st.sidebar.selectbox("Description", sorted(descriptions))

# Filter data
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

    # Determine efficiency rating
    try:
        co2 = float(vehicle["CO2 g/KM"])
    except:
        co2 = 999

    if co2 <= 50:
        rating = "A"
        progress = 100
        color = "green"
    elif co2 <= 90:
        rating = "B"
        progress = 80
        color = "lightgreen"
    elif co2 <= 130:
        rating = "C"
        progress = 60
        color = "yellow"
    elif co2 <= 170:
        rating = "D"
        progress = 40
        color = "orange"
    else:
        rating = "E"
        progress = 20
        color = "red"

    st.subheader(f"🌱 Efficiency Rating: {rating}")
    st.progress(progress)

    # 3 columns of metrics with icons
    col1, col2, col3 = st.columns(3)

    with col1:
        st.image("images/co2.png", width=40)
        st.metric("CO2", f"{vehicle['CO2 g/KM']} g/km")

        st.image("images/battery.png", width=40)
        st.metric("Range", f"{vehicle['WLTP Electric Range (miles)']} mi")

    with col2:
        st.image("images/fuel.png", width=40)
        mpg = vehicle["WLTP MPG (Comb)"] if pd.notnull(vehicle["WLTP MPG (Comb)"]) else "N/A"
        st.metric("MPG", mpg)

        st.image("images/power.png", width=40)
        st.metric("Power", f"{vehicle['Power (bhp)']} bhp")

    with col3:
        st.image("images/luggage.png", width=40)
        st.metric("Luggage", f"{vehicle['Luggage Capacity (L)']} L")

        st.image("images/ncap.png", width=40)
        st.metric("NCAP", vehicle["NCAP Rating"])

    st.write(f"💰 **Price:** {vehicle['Net Basic Price']}")

    # Download button
    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download as CSV",
        data=csv,
        file_name="vehicle_energy_label.csv",
        mime="text/csv",
    )
