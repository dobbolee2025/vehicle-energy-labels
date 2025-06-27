import streamlit as st
import pandas as pd
from io import BytesIO

# Load data
@st.cache_data
def load_data():
    return pd.read_excel("vehicle_energy_labels.xlsx")

data = load_data()

st.title("🚗 Vehicle Energy Label Viewer")

# Sidebar filters
st.sidebar.header("Filter Vehicles")

# Manufacturer
manufacturers = sorted(data["Manufacturer"].dropna().unique())
selected_manufacturer = st.sidebar.selectbox("Manufacturer", manufacturers)

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

# Show label
st.subheader("📋 Vehicle Energy Label")

if filtered.empty:
    st.warning("No data found.")
else:
    vehicle = filtered.iloc[0]

    # Determine efficiency rating
    try:
        co2 = float(vehicle["CO2 g/KM"])
    except:
        co2 = 999

    if co2 <= 50:
        rating = "A"
        color = "#00b050"
    elif co2 <= 90:
        rating = "B"
        color = "#92d050"
    elif co2 <= 130:
        rating = "C"
        color = "#ffff00"
    elif co2 <= 170:
        rating = "D"
        color = "#ffc000"
    elif co2 <= 210:
        rating = "E"
        color = "#ff0000"
    else:
        rating = "F"
        color = "#c00000"

    # Create a colored rating table
    rating_table = f"""
    <table style='border-collapse:collapse;width:100%;'>
      <tr><td style='background:#00b050;color:white;padding:4px;'>A</td></tr>
      <tr><td style='background:#92d050;color:black;padding:4px;'>B</td></tr>
      <tr><td style='background:#ffff00;color:black;padding:4px;'>C</td></tr>
      <tr><td style='background:#ffc000;color:black;padding:4px;'>D</td></tr>
      <tr><td style='background:#ff0000;color:white;padding:4px;'>E</td></tr>
      <tr><td style='background:#c00000;color:white;padding:4px;'>F</td></tr>
    </table>
    """

    st.markdown(
        f"""
        <div style='border:2px solid #ccc; padding:15px; border-radius:8px;'>
          <h3 style='text-align:center;'>{vehicle['Manufacturer']} {vehicle['Model Range']}</h3>
          <h4 style='text-align:center;color:gray;'>{vehicle['Description']}</h4>
          <hr>
          <h4 style='color:{color};'>Efficiency Rating: {rating}</h4>
          {rating_table}
          <hr>
          <p>🛢️ <b>CO2:</b> {vehicle['CO2 g/KM']} g/km</p>
          <p🔋 <b>WLTP Electric Range:</b> {vehicle['WLTP Electric Range (miles)']} miles</p>
          <p>⛽ <b>WLTP MPG:</b> {vehicle['WLTP MPG (Comb)']}</p>
          <p>⚡ <b>kWh/100km:</b> {vehicle['kWh/100km']}</p>
          <p>🏎️ <b>0–62 mph:</b> {vehicle['0-62 mph (secs)']} seconds</p>
          <p>🔧 <b>Power:</b> {vehicle['Power (bhp)']} bhp</p>
          <p>🧳 <b>Luggage Capacity:</b> {vehicle['Luggage Capacity (L)']} L</p>
          <p>🛡️ <b>NCAP Rating:</b> {vehicle['NCAP Rating']}</p>
          <p>💰 <b>Net Basic Price:</b> {vehicle['Net Basic Price']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Generate a CSV for download
    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download as CSV",
        data=csv,
        file_name="vehicle_energy_label.csv",
        mime="text/csv",
    )

    # PDF generation note
    st.info("ℹ️ For PDF export, consider using browser print-to-PDF.")
