import os
import streamlit as st

# ---------------------------------------------------------
# Page Configuration (MUST be the very first Streamlit command)
# ---------------------------------------------------------
st.set_page_config(
    page_title="MOIL Manganese Mining Command Center",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Earth-from-space background — 100% pure CSS (no external images/scripts)
# ---------------------------------------------------------
st.markdown(
    """
    <style>
    .stApp {
        background-color: #05070f !important;
    }

    /* Twinkling starfield */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background-image:
            radial-gradient(2px 2px at 20px 30px, #eee, transparent),
            radial-gradient(2px 2px at 60px 120px, #fff, transparent),
            radial-gradient(1.5px 1.5px at 100px 60px, #ddd, transparent),
            radial-gradient(1.5px 1.5px at 160px 20px, #fff, transparent),
            radial-gradient(2px 2px at 200px 150px, #ccc, transparent),
            radial-gradient(1px 1px at 260px 80px, #fff, transparent),
            radial-gradient(2px 2px at 320px 40px, #eee, transparent),
            radial-gradient(1.5px 1.5px at 380px 110px, #fff, transparent);
        background-repeat: repeat;
        background-size: 400px 200px;
        animation: twinkle 4s ease-in-out infinite alternate;
        opacity: 0.8;
        z-index: -2;
        pointer-events: none;
    }

    /* Rotating Earth sphere (pure CSS gradients, no image) */
    .stApp::after {
        content: "";
        position: fixed;
        bottom: -35vw;
        right: -20vw;
        width: 70vw;
        height: 70vw;
        max-width: 900px;
        max-height: 900px;
        border-radius: 50%;
        background:
            radial-gradient(circle at 35% 30%, rgba(255,255,255,0.25), transparent 8%),
            radial-gradient(circle at 65% 70%, #2a6b3a 0%, transparent 18%),
            radial-gradient(circle at 25% 65%, #3a7d4a 0%, transparent 15%),
            radial-gradient(circle at 75% 25%, #2a6b3a 0%, transparent 12%),
            radial-gradient(circle at 50% 50%, #1a4d8f 0%, #0d2b52 60%, #060f22 100%);
        box-shadow:
            0 0 80px 20px rgba(60, 140, 255, 0.35),
            inset -40px -40px 80px rgba(0,0,0,0.6);
        animation: earth-spin 90s linear infinite;
        z-index: -1;
        pointer-events: none;
    }

    @keyframes twinkle {
        from { opacity: 0.6; }
        to   { opacity: 1; }
    }
    @keyframes earth-spin {
        from { transform: rotate(0deg); }
        to   { transform: rotate(360deg); }
    }

    [data-testid="stHeader"] {
        background-color: transparent !important;
    }
    .block-container {
        position: relative;
        z-index: 1;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("MOIL Manganese Command Center")

import folium
from folium.plugins import HeatMap, MiniMap
from streamlit_folium import st_folium
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import datetime
from dotenv import load_dotenv
from google import genai

# Load environment variables from .env
load_dotenv()

# Initialize Gemini Client using official google-genai SDK
gemini_api_key = os.getenv("GEMINI_API_KEY")
client = None
if gemini_api_key:
    client = genai.Client(api_key=gemini_api_key)

# ---------------------------------------------------------
# Glassmorphism & Custom Sci-Fi Theme CSS
# ---------------------------------------------------------
st.markdown("""
<style>
/* Make header completely transparent */
header[data-testid="stHeader"] {
    background-color: transparent !important;
}
/* Make sidebar semi-transparent glass */
[data-testid="stSidebar"] {
    background-color: rgba(5, 10, 25, 0.65) !important;
    backdrop-filter: blur(15px);
}
/* Make all main area metric cards and containers frosted glass */
.kpi-card, .zone-info-card, .command-header, [data-testid="stMetricValue"], [data-testid="stText"] {
    background-color: rgba(15, 20, 35, 0.45) !important;
    backdrop-filter: blur(10px) !important;
    border-radius: 12px;
    border: 1px solid rgba(0, 242, 254, 0.25) !important;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
}
.command-title {
    font-size: 26px;
    font-weight: 800;
    letter-spacing: -0.5px;
    color: #ffffff;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 12px;
    text-shadow: 0 0 12px rgba(0, 242, 254, 0.6);
}
.command-subtitle {
    color: #a0aec0;
    font-size: 14px;
    margin-top: 4px;
}
.badge-live {
    background: rgba(0, 242, 254, 0.12);
    color: #00f2fe;
    border: 1px solid #00f2fe;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.5px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    box-shadow: 0 0 15px rgba(0, 242, 254, 0.4);
}
.pulse-dot {
    width: 8px;
    height: 8px;
    background-color: #00f2fe;
    border-radius: 50%;
    box-shadow: 0 0 10px #00f2fe;
}
.kpi-label {
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    color: #a0aec0;
    letter-spacing: 1px;
}
.kpi-value {
    font-size: 30px;
    font-weight: 800;
    color: #00f2fe !important;
    text-shadow: 0 0 12px rgba(0, 242, 254, 0.6);
    margin: 8px 0 4px 0;
}
.kpi-subtext {
    font-size: 12px;
    color: #a0aec0;
}
.kpi-alert {
    border-left: 4px solid #ff007f !important;
    background: linear-gradient(135deg, rgba(255, 0, 127, 0.15) 0%, rgba(15, 20, 35, 0.45) 100%) !important;
    box-shadow: 0 0 20px rgba(255, 0, 127, 0.25) !important;
}
.kpi-alert-val {
    color: #ff007f !important;
    text-shadow: 0 0 12px rgba(255, 0, 127, 0.8) !important;
}
.stButton>button {
    background: linear-gradient(135deg, rgba(0, 242, 254, 0.15) 0%, rgba(79, 172, 254, 0.2) 100%) !important;
    color: #00f2fe !important;
    border: 1px solid #00f2fe !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 0 12px rgba(0, 242, 254, 0.2);
}
.stButton>button:hover {
    transform: scale(1.02);
    box-shadow: 0 0 22px rgba(0, 242, 254, 0.6) !important;
    color: #ffffff !important;
}
/* Style the tabs to look like minimalist glowing pills */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: transparent !important;
    padding: 4px 0;
    border: none !important;
}
button[data-baseweb="tab"] {
    background: rgba(255,255,255,0.1) !important;
    border-radius: 20px !important;
    color: white !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    padding: 8px 20px !important;
    margin-right: 10px !important;
    transition: all 0.3s ease !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%) !important;
    color: black !important;
    font-weight: bold !important;
    box-shadow: 0 0 15px rgba(0, 242, 254, 0.5) !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar: Live Data Feeds & Controls
# ---------------------------------------------------------
with st.sidebar:
    st.subheader("⛏️ MOIL AI Control Panel")
    st.caption("Manganese Ore India Limited - Nagpur Division")
    st.divider()
    
    st.header("📡 Data Ingestion Pipeline")
    st.success("🟢 System Status: All pipelines active")

    st.subheader("🌍 Earth Observation (GEE)")
    st.markdown("🟢 **Copernicus (Sentinel-1/2)** - *Active*")
    st.markdown("🟢 **Bhoonidhi (ISRO)** - *Active*")
    st.markdown("🟢 **USGS EarthExplorer** - *Active*")

    st.subheader("🌧️ Weather & Soil")
    st.markdown("🟢 **NASA POWER API** - *Live*")
    st.markdown("🟢 **CHIRPS Rainfall** - *Live*")
    st.markdown("🟢 **IMD Gridded Rainfall** - *Live*")
    st.markdown("🟢 **NASA SMAP Soil Moisture** - *Live*")

    st.subheader("🪨 Geological Mapping")
    st.markdown("🟢 **NGDR (GeoData India)** - *Synced*")
    st.markdown("🟢 **GSI Bhukosh** - *Synced*")
    st.markdown("🟢 **IBM Mineral Inventory** - *Synced*")

    st.divider()
    st.subheader("⚙️ Operational Parameters")
    selected_mine = st.selectbox(
        "Active Mining Lease",
        ["Dongri Buzurg Mine (Bhandara)", "Chikla Mine (Bhandara)", "Kandri Mine (Nagpur)", "Mansar Mine (Nagpur)"],
        index=0
    )
    
    selected_shift = st.radio("Current Shift", ["Shift A (06:00 - 14:00)", "Shift B (14:00 - 22:00)", "Shift C (22:00 - 06:00)"], index=0)
    
    ai_threshold = st.slider("AI Deposit Detection Confidence Threshold", 50, 95, 75, format="%d%%")
    
    st.divider()
    st.caption("🤖 Model: OreScan-Net v4.2 | Latency: 24ms")
    

# ---------------------------------------------------------
# Header & Top KPI Banner
# ---------------------------------------------------------
st.markdown("""
<div class="command-header">
    <div>
        <div class="command-title">
            <span>⛏️ MOIL Manganese Mining Command Center</span>
        </div>
        <div class="command-subtitle">AI-Powered Geospatial & Production Diagnostics Platform • Dongri Buzurg Mine Operations</div>
    </div>
    <div class="badge-live">
        <span class="pulse-dot"></span>
        SYSTEM ONLINE • REAL-TIME SYNC
    </div>
</div>
""", unsafe_allow_html=True)

# 4 Top KPI Cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="kpi-card">
        <div class="kpi-label">Proven Reserves</div>
        <div class="kpi-value">2.8 MT</div>
        <div class="kpi-subtext"><span style="color:#00E676;">High-Grade Ore</span> (Mn 44-49%)</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="kpi-card">
        <div class="kpi-label">Monthly Target</div>
        <div class="kpi-value">10,000 T</div>
        <div class="kpi-subtext">Sept 2026 Operational Target</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="kpi-card">
        <div class="kpi-label">Actual Output (YTD)</div>
        <div class="kpi-value">8,350 T</div>
        <div class="kpi-subtext"><span style="color:#FFB300;">83.5% Target Achieved</span> (🔻 -1,650 T)</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="kpi-card kpi-alert">
        <div class="kpi-label">System Warning</div>
        <div class="kpi-value kpi-alert-val">HIGH RISK ALERT</div>
        <div class="kpi-subtext" style="color:#FF5252;">Zone B Geotechnical Slime Warning</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Main Tabs Layout
# ---------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "🗺️ Tab 1: GIS Ore Intelligence Map", 
    "📊 Tab 2: Deficit Diagnostics & Root Cause", 
    "🎛️ Tab 3: What-If Production Simulator"
])

# =========================================================
# TAB 1: GIS Map (Geospatial Ore Intelligence)
# =========================================================
with tab1:
    st.markdown("#### 🛰️ AI Geospatial Ore Probability & Resource Map")
    st.markdown("Centered on **Dongri Buzurg Mine (21.5317° N, 79.7116° E)**. Google Earth Engine multi-satellite data fusion & anomaly detection.")
    
    # Coordinates of Dongri Buzurg Mine
    mine_lat, mine_lon = 21.5317, 79.7116
    
    # Initialize Folium Map
    m = folium.Map(
        location=[mine_lat, mine_lon],
        zoom_start=14,
        tiles=None,
        control_scale=True
    )
    
    # Esri Satellite Baseline Layer
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri World Imagery",
        name="Esri Satellite Baseline",
        overlay=False,
        control=True
    ).add_to(m)

    # CartoDB Dark Mode Layer
    folium.TileLayer(
        tiles="CartoDB dark_matter",
        name="CartoDB Dark Mode",
        overlay=False,
        control=True
    ).add_to(m)

    # Define 4 Zone Markers Data with GEE Fusion Attributions
    zones = [
        {
            "name": "Zone A: North Pit Extension",
            "lat": 21.5365,
            "lon": 79.7150,
            "prob": "88%",
            "prob_num": 88,
            "grade": "High (Mn 46%)",
            "reserves": "0.85 MT",
            "source": "GEE Fusion: Sentinel-2 + Bhoonidhi + Landsat",
            "status": "Active Extraction",
            "color": "#00f2fe",
            "icon": "cube"
        },
        {
            "name": "Zone B: South Ridge Deposit",
            "lat": 21.5260,
            "lon": 79.7080,
            "prob": "74%",
            "prob_num": 74,
            "grade": "Medium-High (Mn 38%)",
            "reserves": "0.62 MT",
            "source": "GEE Fusion: Sentinel-2 + Bhoonidhi + Landsat",
            "status": "High Geotechnical Risk (Slope Slip Warning)",
            "color": "#ff007f",
            "icon": "exclamation-triangle"
        },
        {
            "name": "Zone C: East Extension Quarry",
            "lat": 21.5340,
            "lon": 79.7220,
            "prob": "62%",
            "prob_num": 62,
            "grade": "Medium (Mn 32%)",
            "reserves": "0.45 MT",
            "source": "GEE Fusion: Sentinel-2 + Bhoonidhi + Landsat",
            "status": "Exploratory Drilling Planned",
            "color": "#ffd600",
            "icon": "search"
        },
        {
            "name": "Zone D: Central Deep Seam",
            "lat": 21.5290,
            "lon": 79.7180,
            "prob": "91%",
            "prob_num": 91,
            "grade": "Ultra-High (Mn 49%)",
            "reserves": "0.88 MT",
            "source": "GEE Fusion: Sentinel-2 + Bhoonidhi + Landsat",
            "status": "Optimal Haul Velocity Zone",
            "color": "#9d4edd",
            "icon": "star"
        }
    ]

    # Generate weighted HeatMap dataset for Manganese Ore Density
    np.random.seed(42)
    heatmap_data = []
    # Core high density cluster around central pit
    for _ in range(130):
        lat = mine_lat + np.random.normal(0, 0.003)
        lon = mine_lon + np.random.normal(0, 0.004)
        weight = np.random.uniform(0.65, 1.0)
        heatmap_data.append([lat, lon, weight])

    # Ore concentration clusters around active zones
    for z in zones:
        for _ in range(45):
            lat = z["lat"] + np.random.normal(0, 0.0018)
            lon = z["lon"] + np.random.normal(0, 0.0018)
            weight = (z["prob_num"] / 100.0) * np.random.uniform(0.7, 1.0)
            heatmap_data.append([lat, lon, weight])

    # 1. Manganese Ore Density HeatMap Layer Group
    fg_heatmap = folium.FeatureGroup(name="Manganese Ore Density Heatmap", show=True)
    HeatMap(
        heatmap_data,
        name="Manganese Ore Density",
        min_opacity=0.35,
        max_val=1.0,
        radius=18,
        blur=15,
        gradient={
            0.2: "#4a154b",  # Deep Purple
            0.5: "#00f2fe",  # Electric Cyan
            0.8: "#ffd600",  # Bright Yellow
            1.0: "#ff0055"   # Intense Red
        }
    ).add_to(fg_heatmap)
    fg_heatmap.add_to(m)

    # 2. Simulated Satellite Feature Layers
    fg_ndvi = folium.FeatureGroup(name="Sentinel-2 (NDVI / Vegetation)", show=False)
    folium.Circle(
        location=[mine_lat + 0.003, mine_lon + 0.002],
        radius=750,
        color="#00f2fe",
        fill=True,
        fill_color="#00f2fe",
        fill_opacity=0.35,
        popup="<b>Sentinel-2 MSI Layer</b><br>NDVI Index: 0.68 (High Biomass Density)"
    ).add_to(fg_ndvi)
    fg_ndvi.add_to(m)

    fg_modis = folium.FeatureGroup(name="MODIS (Land Surface Temp)", show=False)
    folium.Circle(
        location=[mine_lat - 0.004, mine_lon - 0.003],
        radius=900,
        color="#ff007f",
        fill=True,
        fill_color="#ff007f",
        fill_opacity=0.30,
        popup="<b>MODIS LST Layer</b><br>Surface Thermal Anomaly: 38.4°C (Pit Waterlogging)"
    ).add_to(fg_modis)
    fg_modis.add_to(m)

    fg_sar = folium.FeatureGroup(name="Sentinel-1 (SAR / Biomass)", show=False)
    folium.Circle(
        location=[mine_lat, mine_lon],
        radius=1100,
        color="#9d4edd",
        fill=True,
        fill_color="#9d4edd",
        fill_opacity=0.25,
        popup="<b>Sentinel-1 C-Band SAR Layer</b><br>Radar Backscatter & Slope Displacement"
    ).add_to(fg_sar)
    fg_sar.add_to(m)
    
    # Boundary / Pit Circle Overlay
    folium.Circle(
        location=[mine_lat, mine_lon],
        radius=1400,
        color="#00f2fe",
        weight=2,
        fill=True,
        fill_color="#00f2fe",
        fill_opacity=0.08,
        popup="MOIL Dongri Buzurg Lease Concession Area (1.4 km Radius)"
    ).add_to(m)

    # 3. Zone Pins Feature Group
    fg_zones = folium.FeatureGroup(name="Zone Pins", show=True)
    for z in zones:
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; min-width: 220px; color: #111;">
            <h4 style="margin: 0 0 6px 0; color: {z['color']};">{z['name']}</h4>
            <hr style="margin: 4px 0; border: 0; border-top: 1px solid #ccc;">
            <b>Ore Probability:</b> <span style="font-size: 14px; font-weight: bold; color: {z['color']};">{z['prob']}</span><br>
            <b>Ore Grade:</b> {z['grade']}<br>
            <b>Estimated Reserves:</b> {z['reserves']}<br>
            <b>Operational Status:</b> {z['status']}<br>
            <div style="margin-top: 6px; font-size: 11px; background: #eee; padding: 4px 6px; border-radius: 4px;">
                <b>Attribution:</b><br>{z['source']}
            </div>
        </div>
        """
        
        folium.Marker(
            location=[z["lat"], z["lon"]],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{z['name']} | Ore Prob: {z['prob']}",
            icon=folium.Icon(color="black", icon_color=z["color"], icon="info-sign")
        ).add_to(fg_zones)

        # Add visual pulse circle for high probability
        folium.CircleMarker(
            location=[z["lat"], z["lon"]],
            radius=16,
            color=z["color"],
            weight=2,
            fill=True,
            fill_color=z["color"],
            fill_opacity=0.25
        ).add_to(fg_zones)
    fg_zones.add_to(m)

    # Add MiniMap Tactical Radar
    MiniMap(toggle_display=True, tile_layer="CartoDB dark_matter", position="bottomleft").add_to(m)

    # Add Layer Control to Folium Map
    folium.LayerControl(position="topright", collapsed=False).add_to(m)

    # Render Folium Map in Streamlit
    st_folium(m, width="100%", height=500, key="gis_map")
    
    st.markdown("##### 🛰️ Earth Observation Layer Sources & GEE Orchestration Architecture")
    eo_col1, eo_col2, eo_col3, eo_col4, eo_col5 = st.columns(5)
    
    with eo_col1:
        st.markdown("""
        <div class="zone-info-card" style="border-top: 3px solid #2979FF;">
            <div style="font-size: 13px; font-weight: 700; color: #58A6FF;">Google Earth Engine</div>
            <div style="font-size: 11px; color: #8B949E; margin-top: 4px;"><b>Orchestrator:</b> Central data fusion and extraction.</div>
        </div>
        """, unsafe_allow_html=True)
        
    with eo_col2:
        st.markdown("""
        <div class="zone-info-card" style="border-top: 3px solid #00E676;">
            <div style="font-size: 13px; font-weight: 700; color: #FFFFFF;">Copernicus (Sentinel-1/2)</div>
            <div style="font-size: 11px; color: #8B949E; margin-top: 4px;"><b>SAR & MSI:</b> Core vegetation & radar biomass.</div>
        </div>
        """, unsafe_allow_html=True)
        
    with eo_col3:
        st.markdown("""
        <div class="zone-info-card" style="border-top: 3px solid #FFD600;">
            <div style="font-size: 13px; font-weight: 700; color: #FFFFFF;">Bhoonidhi (ISRO)</div>
            <div style="font-size: 11px; color: #8B949E; margin-top: 4px;"><b>LISS-IV:</b> Ultra-high-res boundary demarcation.</div>
        </div>
        """, unsafe_allow_html=True)

    with eo_col4:
        st.markdown("""
        <div class="zone-info-card" style="border-top: 3px solid #FF9100;">
            <div style="font-size: 13px; font-weight: 700; color: #FFFFFF;">USGS (Landsat)</div>
            <div style="font-size: 11px; color: #8B949E; margin-top: 4px;"><b>Landsat 8/9:</b> Historical baseline classification.</div>
        </div>
        """, unsafe_allow_html=True)

    with eo_col5:
        st.markdown("""
        <div class="zone-info-card" style="border-top: 3px solid #FF5252;">
            <div style="font-size: 13px; font-weight: 700; color: #FFFFFF;">MODIS/SMAP</div>
            <div style="font-size: 11px; color: #8B949E; margin-top: 4px;"><b>Thermal & SM:</b> Thermal anomalies and soil moisture.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background-color: #161B22; border: 1px solid #30363D; border-left: 4px solid #00E676; border-radius: 8px; padding: 12px 16px; margin-top: 15px;">
        <span style="font-size: 13px; color: #C9D1D9;">
            🪨 <b>Geological Reserve Mapping Engine:</b> Reserve Mapping Labels are driven by <b>NGDR (Primary)</b>, <b>GSI Bhukosh</b>, and <b>IBM Mineral Inventory</b> combined with <b>MOIL historical reports</b>.
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    st.markdown("##### 📍 Zone Ore Probability & Source Attribution Breakdown")
    z_col1, z_col2, z_col3, z_col4 = st.columns(4)
    
    cols = [z_col1, z_col2, z_col3, z_col4]
    for idx, z in enumerate(zones):
        with cols[idx]:
            st.markdown(f"""
            <div class="zone-info-card" style="border-top: 3px solid {z['color']};">
                <div style="font-size: 14px; font-weight: 700; color: #FFFFFF;">{z['name']}</div>
                <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                    <span style="font-size: 12px; color: #8B949E;">Ore Probability:</span>
                    <span style="font-size: 14px; font-weight: 800; color: {z['color']};">{z['prob']}</span>
                </div>
                <div style="font-size: 12px; color: #C9D1D9;"><b>Grade:</b> {z['grade']}</div>
                <div style="font-size: 12px; color: #C9D1D9;"><b>Est. Reserves:</b> {z['reserves']}</div>
                <div style="margin-top: 8px; font-size: 11px; color: #8B949E; border-top: 1px solid #21262D; padding-top: 6px;">
                    📡 <b>Source:</b> {z['source']}
                </div>
            </div>
            """, unsafe_allow_html=True)

# =========================================================
# TAB 2: Diagnostics (Production Deficit & Root Cause)
# =========================================================
with tab2:
    st.markdown("#### 📊 Production Deficit Diagnostics & Root Cause Attribution")
    st.markdown("Analyzing the **1,650 Tonne deficit** against the 10,000 T monthly target using AI sensor telemetry and historical trends.")
    st.caption("🌧️ *Shortfall predictions powered by NASA POWER API, CHIRPS, and IMD Gridded Rainfall data.*")
    
    diag_col1, diag_col2 = st.columns([6, 4])
    
    with diag_col1:
        st.markdown("##### 📈 30-Day Production Output & AI Forecast (Sept 2026)")
        
        # Generate 30-day realistic time series
        np.random.seed(42)
        days = [f"Day {i}" for i in range(1, 31)]
        
        # Target per day = 10000 / 30 = 333.3 T
        target_daily = [333.3] * 30
        
        # Actual production for first 20 days (low output on days 12-17 due to rain/downtime)
        actual_days = 20
        actual_prod = [320, 315, 330, 340, 310, 305, 335, 325, 290, 280, 275, 190, 180, 210, 230, 220, 240, 300, 310, 315]
        
        # AI Forecast for days 21 to 30
        forecast_prod = [None]*20 + [325, 330, 340, 345, 350, 355, 360, 350, 345, 340]
        
        # Create Plotly figure
        fig_forecast = go.Figure()
        
        # Target line
        fig_forecast.add_trace(go.Scatter(
            x=days, y=target_daily,
            mode='lines',
            name='Daily Target (333 T/day)',
            line=dict(color='#00f2fe', width=2, dash='dash')
        ))
        
        # Actual Line
        fig_forecast.add_trace(go.Scatter(
            x=days[:actual_days], y=actual_prod,
            mode='lines+markers',
            name='Actual Production (T)',
            line=dict(color='#9d4edd', width=3),
            marker=dict(size=6, color='#9d4edd')
        ))
        
        # Forecast Line
        fig_forecast.add_trace(go.Scatter(
            x=days[actual_days-1:], y=[actual_prod[-1]] + forecast_prod[actual_days:],
            mode='lines+markers',
            name='AI Forecast Output (T)',
            line=dict(color='#ffd600', width=3, dash='dot'),
            marker=dict(size=6, color='#ffd600')
        ))

        # Highlight Deficit Dip (Monsoon & Excavator failure)
        fig_forecast.add_vrect(
            x0="Day 11", x1="Day 17",
            fillcolor="#ff007f", opacity=0.18,
            layer="below", line_width=0,
            annotation_text="Critical Downtime & Heavy Rain Window",
            annotation_position="top left",
            annotation_font=dict(color="#ff007f", size=11)
        )
        
        fig_forecast.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(15, 23, 42, 0.65)",
            plot_bgcolor="rgba(3, 7, 18, 0.8)",
            height=380,
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#00f2fe")),
            xaxis=dict(gridcolor="rgba(0, 242, 254, 0.1)"),
            yaxis=dict(title="Production Output (Tonnes)", gridcolor="rgba(0, 242, 254, 0.1)"),
            hoverlabel=dict(bgcolor="#0f172a", bordercolor="#00f2fe", font=dict(color="#00f2fe"))
        )
        
        st.plotly_chart(fig_forecast, use_container_width=True)

    with diag_col2:
        st.markdown("##### 🧱 Root Cause Loss Contributions (1,650 T Deficit)")
        
        root_causes = [
            "Equipment Downtime (Excavator E-04)",
            "CHIRPS & IMD: Heavy Rainfall Risk",
            "Blasting Reschedule / Safety Hold",
            "NASA SMAP: High Soil Moisture Delay"
        ]
        tonnage_loss = [742, 495, 247, 166]
        percentage = [45.0, 30.0, 15.0, 10.0]
        
        fig_bar = go.Figure(go.Bar(
            x=tonnage_loss,
            y=root_causes,
            orientation='h',
            marker=dict(
                color=['#ff007f', '#ff9100', '#ffd600', '#00f2fe'],
                line=dict(color='#00f2fe', width=1)
            ),
            text=[f"{val} T ({pct}%)" for val, pct in zip(tonnage_loss, percentage)],
            textposition='auto',
            textfont=dict(color='#ffffff', size=12, family='sans-serif')
        ))
        
        fig_bar.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(15, 23, 42, 0.65)",
            plot_bgcolor="rgba(3, 7, 18, 0.8)",
            height=380,
            margin=dict(l=20, r=20, t=30, b=20),
            xaxis=dict(title="Tonnage Loss (Tonnes)", gridcolor="rgba(0, 242, 254, 0.1)"),
            yaxis=dict(autorange="reversed", gridcolor="rgba(0, 242, 254, 0.1)"),
            hoverlabel=dict(bgcolor="#0f172a", bordercolor="#ff007f", font=dict(color="#ff007f"))
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("""
    <div style="background: rgba(15, 23, 42, 0.65); border: 1px solid rgba(0, 242, 254, 0.3); border-left: 4px solid #00f2fe; border-radius: 8px; padding: 14px 18px; box-shadow: 0 0 15px rgba(0, 242, 254, 0.15);">
        <h5 style="margin:0 0 6px 0; color:#00f2fe;">🤖 AI Diagnostic Summary & Action Priority</h5>
        <p style="margin:0; font-size: 13px; color:#f1f5f9;">
            Primary cause for the <b>1,650 T production shortfall</b> was the hydraulic pressure failure on <b>Excavator E-04</b> (accounting for 45% / 742 T loss), compounded by 3 days of torrential monsoon rainfall in Pit 2. 
            <b>Recommendation:</b> Deploy spare hydraulic seals to E-04 immediately and activate auxiliary sump pumps in Zone B to recover output.
        </p>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# TAB 3: What-If Simulator (Interactive Operational Modeling)
# =========================================================
with tab3:
    st.markdown("#### 🎛️ Real-Time What-If Production Optimization Simulator")
    st.markdown("Adjust operational parameters below to model real-time production recovery and evaluate strategies to hit the **10,000 T monthly target**.")
    
    sim_col1, sim_col2 = st.columns([5, 7])
    
    with sim_col1:
        st.markdown("<div style='background-color:#161B22; border: 1px solid #30363D; padding: 18px; border-radius: 10px;'>", unsafe_allow_html=True)
        st.markdown("##### 🎚️ Simulator Inputs")
        
        # 1. Excavator E-04 Utilization
        excavator_util = st.slider(
            "Excavator E-04 Utilization Rate (%)",
            min_value=40, max_value=100, value=65, step=5,
            help="Current baseline is 65%. Increasing utilization improves heavy digging throughput."
        )
        
        # 2. Zone Selection
        selected_zones = st.multiselect(
            "Select Active Mining Zones",
            ["Zone A (North Extension)", "Zone B (South Ridge)", "Zone C (East Quarry)", "Zone D (Central Deep Seam)"],
            default=["Zone A (North Extension)", "Zone B (South Ridge)", "Zone C (East Quarry)", "Zone D (Central Deep Seam)"],
            help="High grade zones (Zone A & D) yield higher recoverable tonnage."
        )
        
        # 3. Blasting Reschedule Toggle
        blasting_toggle = st.checkbox(
            "Enable AI Rescheduled Blasting Window",
            value=False,
            help="Synchronizes blasting times with shift handovers to minimize pit stoppage (+8% output boost)."
        )

        # 4. Haul Truck Count
        haul_trucks = st.slider(
            "Haul Truck Fleet Count",
            min_value=10, max_value=30, value=18, step=1,
            help="Optimal fleet size prevents excavator waiting times."
        )
        
        # 5. Pit Dewatering Pump Rate
        dewatering_rate = st.slider(
            "Pit Dewatering Pump Capacity (%)",
            min_value=30, max_value=100, value=70, step=5,
            help="Mitigates monsoon mud siltation."
        )
        
        st.markdown("</div>", unsafe_allow_html=True)
        
    with sim_col2:
        # Real-time Recalculation Math Engine
        base_output = 8350
        
        # Multipliers
        util_mult = 1.0 + ((excavator_util - 65) / 100.0) * 0.45
        
        # Zone grade multiplier
        zone_weights = {
            "Zone A (North Extension)": 0.28,
            "Zone B (South Ridge)": 0.20,
            "Zone C (East Quarry)": 0.15,
            "Zone D (Central Deep Seam)": 0.37
        }
        zone_mult = sum([zone_weights.get(z, 0) for z in selected_zones])
        if len(selected_zones) == 0:
            zone_mult = 0.1
            
        blasting_mult = 1.08 if blasting_toggle else 1.00
        truck_mult = 1.0 + ((haul_trucks - 18) / 18.0) * 0.15
        pump_mult = 1.0 + ((dewatering_rate - 70) / 70.0) * 0.10
        
        # Total Simulated Output
        simulated_output = int(base_output * util_mult * (zone_mult / 1.0) * blasting_mult * truck_mult * pump_mult)
        target = 10000
        delta = simulated_output - target
        
        # Financial calculation: Mn Ore ~$220/T (~₹18,500/T)
        revenue_diff_cr = ((simulated_output - base_output) * 18500) / 10000000.0
        
        st.markdown("##### 📈 Real-Time Simulated Production Results")
        
        # Metric outputs
        s_col1, s_col2, s_col3 = st.columns(3)
        with s_col1:
            st.metric("Simulated Output", f"{simulated_output:,} T", delta=f"{simulated_output - base_output:+} T vs Actual")
        with s_col2:
            status_color = "#00E676" if delta >= 0 else "#FF5252"
            st.metric("Target Delta (10k T)", f"{delta:+} T", delta_color="normal")
        with s_col3:
            st.metric("Est. Revenue Impact", f"₹ {revenue_diff_cr:+.2f} Cr", delta=f"{'Surplus' if revenue_diff_cr >= 0 else 'Shortfall'}")
            
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        
        # Plotly Gauge Chart for Target Accomplishment
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = simulated_output,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Simulated Monthly Production vs 10,000 T Target", 'font': {'size': 14, 'color': '#C9D1D9'}},
            delta = {'reference': target, 'increasing': {'color': "#00E676"}, 'decreasing': {'color': "#FF5252"}},
            gauge = {
                'axis': {'range': [None, 13000], 'tickwidth': 1, 'tickcolor': "#30363D"},
                'bar': {'color': "#2979FF"},
                'bgcolor': "#0D1117",
                'borderwidth': 2,
                'bordercolor': "#30363D",
                'steps': [
                    {'range': [0, 8350], 'color': 'rgba(255, 82, 82, 0.2)'},
                    {'range': [8350, 10000], 'color': 'rgba(255, 179, 0, 0.2)'},
                    {'range': [10000, 13000], 'color': 'rgba(0, 230, 118, 0.2)'}
                ],
                'threshold': {
                    'line': {'color': "#00E676", 'width': 4},
                    'thickness': 0.75,
                    'value': target
                }
            }
        ))
        
        fig_gauge.update_layout(
            template="plotly_dark",
            paper_bgcolor="#161B22",
            height=260,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        st.plotly_chart(fig_gauge, use_container_width=True)

        if delta >= 0:
            st.success(f"🎉 **Target Met!** The simulated configuration yields **{simulated_output:,} Tonnes** ({delta:+} T above target), adding **₹ {revenue_diff_cr:.2f} Cr** in incremental value.")
        else:
            st.warning(f"⚠️ **Shortfall Warning:** Production is still **{abs(delta):,} Tonnes below target**. Increase Excavator E-04 utilization above 85% or enable AI Blasting Reschedule.")

        # Action Execution Buttons
        btn1, btn2 = st.columns(2)
        with btn1:
            if st.button("🚀 Apply & Push Scenario to Pit Dispatch", use_container_width=True):
                st.toast("✅ Dispatch directives broadcasted to Excavator E-04 & Haul Fleet!", icon="🛰️")
        with btn2:
            if st.button("📄 Export Operational Report (PDF/Excel)", use_container_width=True):
                st.toast("📥 Simulation report generated for MOIL Management.", icon="📊")

        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        if st.button("✨ Generate AI Chief Engineer Briefing", type="primary", use_container_width=True):
            if not client:
                st.error("⚠️ GEMINI_API_KEY is not configured in the environment.")
            else:
                with st.spinner("🤖 AI Chief Mining Engineer analyzing active pit telemetry and parameters..."):
                    prompt = f"""
You are MOIL's AI Chief Mining Engineer at Dongri Buzurg Mine.
Analyze the following active simulation parameters for September 2026:

- Target Production Output: 10,000 Tonnes
- Base Predicted Output: 8,350 Tonnes
- Current Simulated Output: {simulated_output:,} Tonnes
- Active Shortfall / Target Delta: {delta:+} Tonnes ({'SURPLUS' if delta >= 0 else 'DEFICIT'})
- Excavator E-04 Utilization: {excavator_util}%
- Selected Mining Zones: {', '.join(selected_zones) if selected_zones else 'None'}
- Blasting Rescheduled: {'Yes' if blasting_toggle else 'No'}
- Haul Truck Fleet Count: {haul_trucks}
- Dewatering Pump Efficiency: {dewatering_rate}%

Please output a crisp, executive 3-bullet-point summary for the Mine Manager covering:
a) Operational Feasibility of current slider settings.
b) Immediate Field Risk (e.g., machinery strain, pit slope stability, monsoon weather window).
c) Final Recommendation for the Mine Manager.
"""
                    try:
                        # Primary model gemini-2.5-flash with fallback to gemini-3.6-flash
                        try:
                            response = client.models.generate_content(
                                model="gemini-2.5-flash",
                                contents=prompt
                            )
                        except Exception:
                            response = client.models.generate_content(
                                model="gemini-3.6-flash",
                                contents=prompt
                            )
                        st.markdown("#### 🤖 AI Executive Strategy Brief")
                        st.info(response.text)
                    except Exception as e:
                        st.error(f"⚠️ Unable to generate AI briefing due to API error: {str(e)}")
                        st.warning("Fallback Note: Ensure Excavator E-04 uptime exceeds 80% and monitor Zone B slope stability sensors.")

# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
st.divider()
f_col1, f_col2 = st.columns([8, 4])
with f_col1:
    st.caption("© 2026 MOIL Limited (Manganese Ore India Limited) • Dongri Buzurg Mine Division • AI Autonomous Command Center v4.2")
with f_col2:
    st.caption("Data Sources: GSI Bhusanket | ISRO Bhoonidhi | NASA Earthdata | NGMDR GeoData India")