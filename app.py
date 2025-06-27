import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd

@st.cache_data
def load_data():
    return pd.read_excel("vehicle_energy_labels.xlsx")

data = load_data()

# Global font: Aptos
st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-family: 'Aptos', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🚗 Vehicle Energy Label Viewer")

# Logos
manufacturer_logos = {
    "Tesla": "https://1000marcas.net/wp-content/uploads/2020/03/logo-Tesla.png",
    "BMW": "https://1000marcas.net/wp-content/uploads/2020/01/BMW-Logo.png",
    "Audi": "https://1000marcas.net/wp-content/uploads/2020/01/Audi-Logo.png",
    "Hyundai": "https://1000marcas.net/wp-content/uploads/2020/01/Hyundai-Logo.png",
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

    # Taxpayer Rate Selector
    tax_rate_label = st.selectbox(
        "Select Taxpayer Rate",
        ["20% Taxpayer", "40% Taxpayer", "45% Taxpayer"],
        index=0
    )
    tax_rate = {
        "20% Taxpayer": 0.20,
        "40% Taxpayer": 0.40,
        "45% Taxpayer": 0.45
    }[tax_rate_label]

    # Safe numeric parsing
    try:
        co2 = float(vehicle.get("CO2 g/KM", 0))
    except (ValueError, TypeError):
        co2 = 0
    co2_score = max(0, min(100, 100 - (co2 / 2)))

    mpg = vehicle.get("WLTP MPG (Comb)")
    electric_range = vehicle.get("WLTP Electric Range (miles)")
    if pd.notnull(mpg):
        mpg_score = min(100, mpg)
        mpg_label = f"{mpg} MPG"
    elif pd.notnull(electric_range):
        mpg_score = min(100, electric_range / 4)
        mpg_label = f"{electric_range} mi (electric)"
    else:
        mpg_score = 50
        mpg_label = "N/A"

    try:
        tco = float(vehicle.get("TCO", 0))
    except (ValueError, TypeError):
        tco = 0
    tco_score = max(0, min(100, 100 - (tco / 1000)))

    efficiency_score = (co2_score + mpg_score + tco_score) / 3

    if efficiency_score >= 80:
        rating, color = "A", "green"
    elif efficiency_score >= 65:
        rating, color = "B", "lightgreen"
    elif efficiency_score >= 50:
        rating, color = "C", "yellow"
    elif efficiency_score >= 35:
        rating, color = "D", "orange"
    elif efficiency_score >= 20:
        rating, color = "E", "red"
    else:
        rating, color = "F", "darkred"

    # Safe BiK fields
    try:
        p11d = float(vehicle.get("P11d inc. Options", 0))
    except (ValueError, TypeError):
        p11d = 0
    try:
        bik_percent = float(vehicle.get("BIK% Year 1", 0))
    except (ValueError, TypeError):
        bik_percent = 0

    bik_value = (p11d * (bik_percent / 100)) * tax_rate

    # Begin Top Trumps Card
    st.markdown("""
        <div style="max-width:650px;margin:auto;padding:20px;border:2px solid #ccc;border-radius:12px;
        box-shadow:0 0 10px rgba(0,0,0,0.1);background:#fff;text-align:center;">
    """, unsafe_allow_html=True)

    # Logo and Title
    logo_url = manufacturer_logos.get(selected_manufacturer)
    if logo_url:
        st.image(logo_url, width=100)
    st.markdown(
        f"<h2>{vehicle['Manufacturer']} {vehicle['Model Range']}</h2>"
        f"<h4 style='color:#555;'>{vehicle['Description']}</h4>",
        unsafe_allow_html=True
    )

    # Efficiency
    st.markdown(
        f"<h4 style='color:{color};'>🌱 Efficiency Rating: {rating} (Score {efficiency_score:.1f})</h4>",
        unsafe_allow_html=True
    )
    st.progress(efficiency_score / 100)

    # Metrics Grid
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"<div style='padding:8px;border:1px solid #ddd;border-radius:6px;'>🌿 <strong>CO2</strong><br>{vehicle['CO2 g/KM']} g/km</div>",
            unsafe_allow_html=True)
        st.markdown(
            f"<div style='padding:8px;border:1px solid #ddd;border-radius:6px;'>⚡ <strong>MPG/Range</strong><br>{mpg_label}</div>",
            unsafe_allow_html=True)

    with col2:
        st.markdown(
            f"<div style='padding:8px;border:1px solid #ddd;border-radius:6px;'>🔧 <strong>Power</strong><br>{vehicle['Power (bhp)']} bhp</div>",
            unsafe_allow_html=True)
        st.markdown(
            f"<div style='padding:8px;border:1px solid #ddd;border-radius:6px;'>🧳 <strong>Luggage</strong><br>{vehicle['Luggage Capacity (L)']} L</div>",
            unsafe_allow_html=True)

    with col3:
        st.markdown(
            f"<div style='padding:8px;border:1px solid #ddd;border-radius:6px;'>🛡️ <strong>NCAP</strong><br>{vehicle['NCAP Rating']}</div>",
            unsafe_allow_html=True)
        st.markdown(
            f"<div style='padding:8px;border:1px solid #ddd;border-radius:6px;'>🏎️ <strong>0–62 mph</strong><br>{vehicle['0-62 mph (secs)']} sec</div>",
            unsafe_allow_html=True)

    # BiK Card
    st.markdown(
        f"""
        <div style='padding:12px;border:2px solid #555;border-radius:8px;margin-top:12px;'>
            💼 <strong>BiK Information</strong><br><br>
            <strong>BiK %:</strong> {bik_percent}%<br>
            <strong>P11D Value:</strong> £{p11d:,.2f}<br>
            <strong>{tax_rate_label} Annual Tax:</strong> £{bik_value:,.2f}<br>
            <strong>Monthly Tax:</strong> £{bik_value/12:,.2f}
        </div>
        """,
        unsafe_allow_html=True)

    # Net Basic Price
    st.markdown(
        f"<h4 style='margin-top:20px;'>💰 Net Basic Price: {vehicle['Net Basic Price']}</h4>",
        unsafe_allow_html=True)

    # Print Button
    st.markdown(
        """
        <div style='margin-top:20px;'>
        <button onclick="window.print()" style="background-color:#4CAF50;color:white;padding:10px 20px;border:none;border-radius:4px;cursor:pointer;font-size:16px;">
            🖨️ Print or Save as PDF
        </button>
        </div>
        </div>
        """,
        unsafe_allow_html=True)
