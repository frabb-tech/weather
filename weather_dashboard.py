import streamlit as st
import requests
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime
from prophet import Prophet
import io

API_KEY = st.secrets["api"]["openweathermap_key"]
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
                "precipitation": entry.get("rain", {}).get("3h", 0),
                "humidity": entry["main"]["humidity"],
                "weather": entry["weather"][0]["description"]
            })
        return pd.DataFrame(parsed)
    else:
        return pd.DataFrame()

st.title("HEWRI Weather Forecast Dashboard V2")

selected_city = st.selectbox("Select a City", list(CITIES.keys()))
df = get_forecast(selected_city, CITIES[selected_city])

if df.empty:
    st.error("Could not retrieve data. Please check API or city.")
else:
    st.subheader(f"🌡 7-Day Temperature & Precipitation Forecast: {selected_city}")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['datetime'], y=df['temperature'],
                             mode='lines+markers', name='Temperature'))
    fig.add_trace(go.Bar(x=df['datetime'], y=df['precipitation'],
                         name='Precipitation', yaxis='y2'))

    fig.update_layout(
        xaxis_title="Date",
        yaxis=dict(title="Temperature (°C)"),
        yaxis2=dict(title="Precipitation (mm)", overlaying='y', side='right'),
        title="Temperature & Precipitation Trends",
        legend=dict(x=0, y=1.1, orientation="h")
    )
    st.plotly_chart(fig)

    st.subheader("🤖 AI-Based Forecasts")

    def forecast_ai(dataframe, target_col, label):
        prophet_df = dataframe[['datetime', target_col]].rename(columns={'datetime': 'ds', target_col: 'y'})
        model = Prophet(daily_seasonality=True)
        model.fit(prophet_df)
        future = model.make_future_dataframe(periods=3, freq='D')
        forecast = model.predict(future)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], name=f"{label} Forecast"))
        fig.add_trace(go.Scatter(x=prophet_df['ds'], y=prophet_df['y'], mode='markers', name='Observed'))
        fig.update_layout(title=f"{label} Prediction (AI)",
                          xaxis_title="Date",
                          yaxis_title=label)
        st.plotly_chart(fig)
        return forecast

    forecast_ai(df, 'temperature', 'Temperature')
    forecast_ai(df, 'precipitation', 'Precipitation')

    st.subheader("📥 Download Forecast Data")
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", data=csv, file_name=f"{selected_city}_forecast.csv", mime="text/csv")

# Placeholder for future admin1-level map integration
st.markdown("🗺 Admin1-level regional weather maps coming soon...")
