import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import json
from datetime import datetime
from prophet import Prophet

API_KEY = "17badf0db44e16808ff58e825a3d163b"
CITIES = {
    "Beirut": "LB",
    "Amman": "JO"
}

# Load admin1 GeoJSON files
with open("data/lebanon_admin1.geojson", "r") as f:
    lebanon_geo = json.load(f)
with open("data/jordan_admin1.geojson", "r") as f:
    jordan_geo = json.load(f)

@st.cache_data
def get_forecast(city, country_code):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city},{country_code}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        forecasts = data['list']
        parsed = []
        for entry in forecasts:
            parsed.append({
                "datetime": datetime.utcfromtimestamp(entry["dt"]),
                "temperature": entry["main"]["temp"],
                "precipitation": entry.get("rain", {}).get("3h", 0),
                "weather": entry["weather"][0]["description"],
                "city": city
            })
        return pd.DataFrame(parsed)
    else:
        return pd.DataFrame()

st.title("HEWRI Weather Dashboard V3 — Admin1 Map + AI + Automation Ready")

# View selection
view = st.radio("Select View", ["City Forecast", "Admin1 Map"])
selected_city = st.selectbox("City", list(CITIES.keys()))

df = get_forecast(selected_city, CITIES[selected_city])

if df.empty:
    st.error("No data available")
else:
    if view == "City Forecast":
        st.subheader(f"{selected_city} 7-Day Forecast")
        st.line_chart(df.set_index("datetime")[["temperature", "precipitation"]])

        prophet_df = df[['datetime', 'temperature']].rename(columns={'datetime': 'ds', 'temperature': 'y'})
        model = Prophet(daily_seasonality=True)
        model.fit(prophet_df)
        future = model.make_future_dataframe(periods=3, freq='D')
        forecast = model.predict(future)

        st.subheader("AI Temperature Forecast")
        fig = px.line(forecast, x='ds', y='yhat', title="Predicted Temperatures")
        st.plotly_chart(fig)

    elif view == "Admin1 Map":
        st.subheader(f"{selected_city} Region Map (Mocked)")
        if selected_city == "Beirut":
            fig = px.choropleth_mapbox(
                df.groupby("city").mean().reset_index(),
                geojson=lebanon_geo,
                locations="city",
                featureidkey="properties.name",
                color="temperature",
                mapbox_style="carto-positron",
                zoom=10, center={"lat": 33.89, "lon": 35.5}
            )
            st.plotly_chart(fig)
        elif selected_city == "Amman":
            fig = px.choropleth_mapbox(
                df.groupby("city").mean().reset_index(),
                geojson=jordan_geo,
                locations="city",
                featureidkey="properties.name",
                color="temperature",
                mapbox_style="carto-positron",
                zoom=10, center={"lat": 31.96, "lon": 35.87}
            )
            st.plotly_chart(fig)

# Placeholder: Scheduled daily updates (e.g., GitHub Actions or Firebase sync)
st.markdown("🔄 Daily update automation will be configured via scheduler.")
