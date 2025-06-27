import streamlit as st
import pandas as pd

# Load data
@st.cache_data
def load_data():
    return pd.read_excel("vehicle_energy_labels.xlsx")

data = load_data()

st.title("🚗 Vehicle Energy Label Viewer")

# Sidebar filters
st.sidebar.header("Filter Vehicles")

manufacturers = sorted(data["Manufacturer"].dropna().unique())
selected_manufacturer = st.sidebar.selectbox("Manufacturer", manufacturers)

models = (
    data[data["Manufacturer"] == selected_manufacturer]["Model Range"]
    .dropna()
    .unique()
)
selected_model = st.sidebar.selectbox("Model Range", sorted(models))

descriptions = (
    data[
        (data["Manufacturer"] == selected_manufacturer)
        & (data["Model Range"] == selected_model)
    ]["Description"]
    .dropna()
    .unique()
)
selected_description = st.sidebar.selectbox("Description", sorted(descriptions))

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
    st.subheader(vehicle['Description'])

    # Columns for key metrics
    col1, col2, col3 = st.columns(3)

    col1.metric("🛢️ CO2", f"{vehicle['CO2 g/KM']} g/km")
    col2.metric("🔋 Electric Range", f"{vehicle['WLTP Electric Range (miles)']} mi")
    col3.metric("⛽ MPG", vehicle['WLTP MPG (Comb)'] if pd.notnull(vehicle['WLTP MPG (Comb)']) else "N/A")

    # Efficiency rating
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

    # More details
    st.write("### Details")

    col4, col5 = st.columns(2)
    col4.write(f"⚡ **kWh/100km:** {vehicle['kWh/100km']}")
    col4.write(f"🏎️ **0–62 mph:** {vehicle['0-62 mph (secs)']} sec")
    col4.write(f"🔧 **Power:** {vehicle['Power (bhp)']} bhp")

    col5.write(f"🧳 **Luggage:** {vehicle['Luggage Capacity (L)']} L")
    col5.write(f"🛡️ **NCAP Rating:** {vehicle['NCAP Rating']}")
    col5.write(f"💰 **Price:** {vehicle['Net Basic Price']}")

    # Download button
    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download as CSV",
        data=csv,
        file_name="vehicle_energy_label.csv",
        mime="text/csv",
    )
