import streamlit as st
import pandas as pd
import json

st.set_page_config(layout="wide")
st.title("⚠️ HEWRI Multi-Hazard Forecast Dashboard")

# Load forecast data
with open("forecast_data.json") as f:
    forecast_data = json.load(f)

city = st.selectbox("Select a City", list(forecast_data.keys()))
hazards = pd.DataFrame(forecast_data[city]["raw"])

st.subheader(f"🌦 Hazard Alerts for {city}")

latest = hazards.iloc[0]

# Hazard warnings
if latest["flood_risk"]:
    st.error("🌊 Flood Risk: Heavy rainfall forecasted.")
if latest["lightning_risk"]:
    st.warning("⚡ Lightning Risk: Thunderstorms expected.")
if latest["snow_risk"]:
    st.info("❄ Snow Risk: Accumulation possible.")
if latest["wind_risk"]:
    st.warning("🌬 High Wind Risk: Gusts may exceed safe limits.")
if latest["extreme_heat"]:
    st.error("🔥 Extreme Heat: Temperatures above 40°C.")
if latest["extreme_cold"]:
    st.info("🧊 Extreme Cold: Below freezing temperatures expected.")
if latest["low_visibility"]:
    st.warning("🌫 Low Visibility: May affect transport and access.")

# Preview next 24–48h
st.subheader("🧾 Hazard Risk Table")
hazards_short = hazards[["datetime", "flood_risk", "lightning_risk", "wind_risk", "snow_risk", "extreme_heat", "extreme_cold", "low_visibility"]]
st.dataframe(hazards_short.head(8))
