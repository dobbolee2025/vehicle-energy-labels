import streamlit as st
import pandas as pd
import pdfkit

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
st.subheader("Vehicle Energy Label")

if filtered.empty:
    st.warning("No data found.")
else:
    vehicle = filtered.iloc[0]

    # Define A-G rating based on CO2
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

    # HTML label
    html_label = f"""
    <div style='border:2px solid #ccc; padding:20px; border-radius:8px; width:400px;'>
      <h3 style='text-align:center;'>{vehicle['Manufacturer']} {vehicle['Model Range']}</h3>
      <p style='text-align:center;color:gray;'>{vehicle['Description']}</p>
      <div style='height:180px; margin:10px 0; background:linear-gradient(to bottom,
        #00b050 0%,
        #92d050 20%,
        #ffff00 40%,
        #ffc000 60%,
        #ff0000 80%,
        #c00000 100%);
        position:relative;'>
        <div style='position:absolute; left:10px; top: {30 + (ord(rating)-65)*25}px;
            background:{color}; color:white; padding:3px 10px; border-radius:4px;'>
          {rating}
        </div>
      </div>
      <p><b>CO2:</b> {vehicle['CO2 g/KM']} g/km</p>
      <p><b>Range:</b> {vehicle['WLTP Electric Range (miles)']} miles</p>
      <p><b>MPG:</b> {vehicle['WLTP MPG (Comb)']}</p>
      <p><b>kWh/100km:</b> {vehicle['kWh/100km']}</p>
      <p><b>Power:</b> {vehicle['Power (bhp)']} bhp</p>
      <p><b>0–62 mph:</b> {vehicle['0-62 mph (secs)']} s</p>
      <p><b>NCAP:</b> {vehicle['NCAP Rating']}</p>
      <p><b>Price:</b> {vehicle['Net Basic Price']}</p>
    </div>
    """

    st.markdown(html_label, unsafe_allow_html=True)

    # Export to PDF
    if st.button("Download this label as PDF"):
        # Save HTML to file
        with open("label.html", "w") as f:
            f.write(html_label)
        # Convert to PDF
        pdfkit.from_file("label.html", "label.pdf")
        # Read PDF
        with open("label.pdf", "rb") as f:
            st.download_button(
                label="Click to download PDF",
                data=f,
                file_name="vehicle_energy_label.pdf",
                mime="application/pdf"
            )
