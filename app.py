import streamlit as st
import pandas as pd

# Load the Excel file
@st.cache_data
def load_data():
    return pd.read_excel("vehicle_energy_labels.xlsx")

data = load_data()

st.title("🚗 Vehicle Energy Label Viewer")

# Sidebar filters
st.sidebar.header("🔍 Filter Vehicles")

# Manufacturer selection
manufacturers = sorted(data["Manufacturer"].dropna().unique())
selected_manufacturer = st.sidebar.selectbox("Select Manufacturer", manufacturers)

# Filter Model Range based on Manufacturer
models = (
    data[data["Manufacturer"] == selected_manufacturer]["Model Range"]
    .dropna()
    .unique()
)
selected_model = st.sidebar.selectbox("Select Model Range", sorted(models))

# Filter Description based on Model Range
descriptions = (
    data[
        (data["Manufacturer"] == selected_manufacturer)
        & (data["Model Range"] == selected_model)
    ]["Description"]
    .dropna()
    .unique()
)
selected_description = st.sidebar.selectbox("Select Description", sorted(descriptions))

# Final filtered dataset
filtered = data[
    (data["Manufacturer"] == selected_manufacturer)
    & (data["Model Range"] == selected_model)
    & (data["Description"] == selected_description)
]

# Show label
st.subheader("📋 Vehicle Energy Label")

if filtered.empty:
    st.warning("No vehicle found with this selection.")
else:
    vehicle = filtered.iloc[0]

    # Display logos (example: you can upload and replace these image paths)
    st.image("https://upload.wikimedia.org/wikipedia/commons/4/4e/Car_logo.png", width=100)
    
    # Display label-like UI
    st.markdown(
        f"""
        <div style='border:2px solid #ccc; padding:15px; border-radius:8px; width:400px;'>
            <h2 style='text-align:center;'>{vehicle['Manufacturer']} {vehicle['Model Range']}</h2>
            <h4 style='text-align:center; color:#666;'>{vehicle['Description']}</h4>
            <hr>
            <p><b>CO2 Emissions:</b> {vehicle['CO2 g/KM']} g/km</p>
            <p><b>WLTP Electric Range:</b> {vehicle['WLTP Electric Range (miles)']} miles</p>
            <p><b>WLTP MPG:</b> {vehicle['WLTP MPG (Comb)']}</p>
            <p><b>kWh/100km:</b> {vehicle['kWh/100km']}</p>
            <p><b>0–62 mph:</b> {vehicle['0-62 mph (secs)']} seconds</p>
            <p><b>Power:</b> {vehicle['Power (bhp)']} bhp</p>
            <p><b>Luggage Capacity:</b> {vehicle['Luggage Capacity (L)']} L</p>
            <p><b>BIK% Year 1:</b> {vehicle['BIK% Year 1']}</p>
            <p><b>NCAP Rating:</b> {vehicle['NCAP Rating']}</p>
            <p><b>Net Basic Price:</b> {vehicle['Net Basic Price']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Download single vehicle info
    st.download_button(
        label="Download this vehicle info as CSV",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="vehicle_energy_label.csv",
        mime="text/csv",
    )
