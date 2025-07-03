import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd

@st.cache_data
def load_data():
    df = pd.read_excel("vehicle_energy_labels.xlsx")
    df.columns = df.columns.str.strip()
    return df

data = load_data()

# Global font
st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-family: 'Aptos', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🚗 Vehicle Top Trumps Viewer")

manufacturers = sorted(data["Manufacturer"].dropna().unique())

with st.sidebar:
    selected_manufacturer = option_menu(
        "Select Manufacturer",
        manufacturers,
        icons=["car"] * len(manufacturers),
        menu_icon="cast",
        default_index=0,
    )

models = data.loc[
    data["Manufacturer"] == selected_manufacturer, "Model Range"
].dropna().unique()
selected_model = st.selectbox("Select Model Range", sorted(models))

descriptions = data.loc[
    (data["Manufacturer"] == selected_manufacturer)
    & (data["Model Range"] == selected_model),
    "Description"
].dropna().unique()
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

    # Car Image URL
    image_url = f"https://source.unsplash.com/featured/?{selected_manufacturer}+{selected_model}"
    fallback_image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Cars_logo.png/320px-Cars_logo.png"

    # Clean data
    mpg = vehicle.get("WLTP MPG (Comb)")
    mpg_label = f"{mpg} MPG" if pd.notnull(mpg) else "N/A"
    co2 = vehicle.get("CO2 g/KM", "N/A")
    power = vehicle.get("Power (bhp)", "N/A")
    luggage = vehicle.get("Luggage Capacity (Seats Up)", "N/A")
    ncap = vehicle.get("NCAP Rating", "N/A")
    accel = vehicle.get("0 to 62 mph (secs)", "N/A")

    # BiK
    try:
        p11d = float(vehicle.get("P11d Basic", 0))
    except:
        p11d = 0
    try:
        bik_percent = float(vehicle.get("BIK% Year 1", 0))
    except:
        bik_percent = 0

    # Tax band selection
    st.markdown("<br>", unsafe_allow_html=True)
    tax_rate_label = st.selectbox(
        "Select Tax Band",
        [
            "20% (Standard Rate Taxpayer)",
            "40% (Higher Rate Taxpayer)",
            "45% (Additional Rate Taxpayer)"
        ],
        index=0
    )
    tax_rate = {"20% (Standard Rate Taxpayer)":0.20,"40% (Higher Rate Taxpayer)":0.40,"45% (Additional Rate Taxpayer)":0.45}[tax_rate_label]
    bik_value = (p11d * (bik_percent/100)) * tax_rate

    # Efficiency rating (simplified)
    efficiency = "A" if co2 != "N/A" and float(co2) < 50 else "C"

    # Card HTML
    st.markdown(f"""
    <div style="
        max-width:500px;
        margin:auto;
        border:4px solid #ccc;
        border-radius:16px;
        background:#fefefe;
        box-shadow:0 0 12px rgba(0,0,0,0.2);
        overflow:hidden;">
        <div style="background:#222;color:white;padding:10px 0;font-size:22px;font-weight:bold;">
            {vehicle.get('Manufacturer','')} {vehicle.get('Model Range','')}
        </div>
        <img src="{image_url}" onerror="this.onerror=null;this.src='{fallback_image_url}';" style="width:100%;height:auto;display:block;">
        <div style="padding:12px;text-align:left;">
            <p style="font-size:14px;color:#333;">
            <strong>Description:</strong><br>
            {vehicle.get('Description','')}
            </p>
        </div>
        <div style="padding:0 12px 12px 12px;">
            <div style="background:#eee;padding:6px 10px;margin:4px 0;border-radius:4px;">
                <strong>MPG:</strong> {mpg_label}
            </div>
            <div style="background:#eee;padding:6px 10px;margin:4px 0;border-radius:4px;">
                <strong>CO2:</strong> {co2} g/km
            </div>
            <div style="background:#eee;padding:6px 10px;margin:4px 0;border-radius:4px;">
                <strong>Power:</strong> {power} bhp
            </div>
            <div style="background:#eee;padding:6px 10px;margin:4px 0;border-radius:4px;">
                <strong>0–62 mph:</strong> {accel} sec
            </div>
            <div style="background:#eee;padding:6px 10px;margin:4px 0;border-radius:4px;">
                <strong>NCAP Rating:</strong> {ncap}
            </div>
            <div style="background:#eee;padding:6px 10px;margin:4px 0;border-radius:4px;">
                <strong>Luggage Capacity:</strong> {luggage} L
            </div>
        </div>
        <div style="background:#ddd;padding:10px;text-align:center;">
            <strong>Efficiency Rating:</strong> {efficiency}
        </div>
        <div style="padding:12px;text-align:center;">
            <strong>💼 BiK Information</strong><br>
            BiK %: {bik_percent}%<br>
            P11D Value: £{p11d:,.2f}<br>
            {tax_rate_label} Annual Tax: £{bik_value:,.2f}<br>
            Monthly Tax: £{bik_value/12:,.2f}
        </div>
        <div style="text-align:center;padding:10px;">
            <button onclick="window.print()" style="background:#4CAF50;color:white;padding:8px 16px;border:none;border-radius:4px;cursor:pointer;">
                🖨️ Print or Save as PDF
            </button>
        </div>
    </div>
    """, unsafe_allow_html=True)
