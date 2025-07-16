import streamlit as st
import requests
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime

API_KEY = "17badf0db44e16808ff58e825a3d163b"
CITIES = {
    "Beirut": "LB",
    "Amman": "JO",
    "Damascus": "SY",
    "Baghdad": "IQ",
    "Kabul": "AF",
    "Ankara": "TR",
    "Yerevan": "AM",
    "Sarajevo": "BA",
    "Ramallah": "PS"
}

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
                "humidity": entry["main"]["humidity"],
                "weather": entry["weather"][0]["description"]
            })
        return pd.DataFrame(parsed)
    else:
        return pd.DataFrame()

st.title("HEWRI Weather Forecast Dashboard")
selected_city = st.selectbox("Select a City", list(CITIES.keys()))
df = get_forecast(selected_city, CITIES[selected_city])

if df.empty:
    st.error("Could not retrieve data. Please check API or city.")
else:
    st.subheader(f"7-Day Forecast for {selected_city}")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['datetime'], y=df['temperature'],
                             mode='lines+markers', name='Temperature'))
    fig.update_layout(title="Temperature Trend",
                      xaxis_title="Date",
                      yaxis_title="Temperature (°C)")
    st.plotly_chart(fig)
    st.dataframe(df)
