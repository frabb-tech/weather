import requests
import pandas as pd
from datetime import datetime
from prophet import Prophet
import json
import os

API_KEY = os.getenv("OPENWEATHERMAP_KEY", "17badf0db44e16808ff58e825a3d163b")
CITIES = {
    "Beirut": "LB",
    "Amman": "JO"
}

def get_forecast(city, country_code):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city},{country_code}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch data for {city}")
        return pd.DataFrame()
    data = response.json()["list"]
    enriched = []
    for f in data:
        temp = f["main"]["temp"]
        rain = f.get("rain", {}).get("3h", 0)
        snow = f.get("snow", {}).get("3h", 0)
        gust = f["wind"].get("gust", 0)
        vis = f.get("visibility", 10000)
        weather = f["weather"][0]["main"]

        enriched.append({
            "datetime": datetime.utcfromtimestamp(f["dt"]),
            "temperature": temp,
            "precipitation": rain,
            "snow": snow,
            "humidity": f["main"]["humidity"],
            "wind_speed": f["wind"]["speed"],
            "wind_gust": gust,
            "visibility": vis,
            "weather": weather,
            "flood_risk": rain > 50,
            "lightning_risk": weather == "Thunderstorm",
            "snow_risk": snow > 10,
            "wind_risk": gust > 15,
            "extreme_heat": temp > 40,
            "extreme_cold": temp < 0,
            "low_visibility": vis < 3000
        })
    return pd.DataFrame(enriched)

def apply_forecast(df, column):
    prophet_df = df[["datetime", column]].rename(columns={"datetime": "ds", column: "y"})
    model = Prophet(daily_seasonality=True)
    model.fit(prophet_df)
    future = model.make_future_dataframe(periods=3, freq='D')
    forecast = model.predict(future)
    return forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]]

all_results = {}
for city, code in CITIES.items():
    df = get_forecast(city, code)
    if df.empty:
        continue
    df.to_csv(f"{city}_raw_forecast.csv", index=False)

    temp_forecast = apply_forecast(df, "temperature")
    rain_forecast = apply_forecast(df, "precipitation")

    all_results[city] = {
        "raw": df.to_dict(orient="records"),
        "temperature_ai": temp_forecast.to_dict(orient="records"),
        "precipitation_ai": rain_forecast.to_dict(orient="records")
    }

with open("forecast_data.json", "w") as f:
    json.dump(all_results, f, indent=2, default=str)
print("Multi-hazard forecast saved.")
