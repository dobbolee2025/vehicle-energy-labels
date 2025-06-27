import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd

@st.cache_data
def load_data():
    df = pd.read_excel("vehicle_energy_labels.xlsx")
    df.columns = df.columns.str.strip()  # Clean column names
    return df

data = load_data()

# Global font: Aptos
st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-family: 'Aptos', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🚗 Vehicle Top Trumps Viewer")

# Manufacturer logos (optional fallback)
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

    # Safe BiK using P11d Basic
    try:
        p11d = float(vehicle.get("P11d Basic", 0))
    except (ValueError, TypeError):
        p11d = 0
    try:
        bik_percent = float(vehicle.get("BIK% Year 1", 0))
    except (ValueError, TypeError):
        bik_percent = 0

    # Car Image URL
    image_url = f"https://source.unsplash.com/featured/?{selected_manufacturer}+{selected_model}"

    # Start Card
    st.markdown(f"""
        <div style="
            max-width:500px;
            margin:auto;
            padding:20px;
            border:3px solid #ccc;
            border-radius:16px;
            box-shadow:0 0 10px rgba(0,0,0,0.1);
            background:#f9f9f9;
            text-align:center;">
            <h2 style='margin-bottom:10px;'>{vehicle.get('Manufacturer', '')} {vehicle.get('Model Range', '')}</h2>
            <img src='{image_url}' style='width:100%;border-radius:8px;margin-bottom:10px;'/>
            <h4 style='color:#555;'>{vehicle.get('Description', '')}</h4>
            <h4 style='color:{color};'>🌱 Efficiency Rating: {rating} (Score {efficiency_score:.1f})</h4>
    """, unsafe_allow_html=True)

    st.progress(efficiency_score/100)

    # Metrics grid
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div style='padding:8px;border:1px solid #ddd;border-radius:6px;'>🌿 CO2<br>{vehicle.get('CO2 g/KM', 'N/A')} g/km</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='padding:8px;border:1px solid #ddd;border-radius:6px;'>⚡ MPG/Range<br>{mpg_label}</div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div style='padding:8px;border:1px solid #ddd;border-radius:6px;'>🔧 Power<br>{vehicle.get('Power (bhp)', 'N/A')} bhp</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='padding:8px;border:1px solid #ddd;border-radius:6px;'>🧳 Luggage<br>{vehicle.get('Luggage Capacity (Seats Up)', 'N/A')} L</div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div style='padding:8px;border:1px solid #ddd;border-radius:6px;'>🛡️ NCAP<br>{vehicle.get('NCAP Rating', 'N/A')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='padding:8px;border:1px solid #ddd;border-radius:6px;'>🏎️ 0–62 mph<br>{vehicle.get('0-62 mph (secs)', 'N/A')} sec</div>", unsafe_allow_html=True)

    # BiK Card with selector inside
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div style='max-width:500px;margin:auto;border:2px solid #555;border-radius:8px;padding:12px;text-align:center;'>", unsafe_allow_html=True)
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
    st.markdown(f"""
        <strong>💼 BiK Information</strong><br>
        BiK %: {bik_percent}%<br>
        P11D Value: £{p11d:,.2f}<br>
        {tax_rate_label} Annual Tax: £{bik_value:,.2f}<br>
        Monthly Tax: £{bik_value/12:,.2f}
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Net Basic Price
    st.markdown(f"<h4 style='text-align:center;'>💰 Net Basic Price: {vehicle.get('Net Basic Price', 'N/A')}</h4>", unsafe_allow_html=True)

    # Print Button
    st.markdown("""
        <div style='text-align:center;margin-top:20px;'>
        <button onclick="window.print()" style="background-color:#4CAF50;color:white;padding:10px 20px;border:none;border-radius:4px;cursor:pointer;font-size:16px;">
        🖨️ Print or Save as PDF
        </button>
        </div>
        </div>
    """, unsafe_allow_html=True)
