from weather_client import get_weather

# תל אביב, 1 בספטמבר 2025 בשעה 19:00 (עם אזור זמן חובה!)
data = get_weather(32.0853, 34.7818, "2025-08-01T19:00:00+03:00")
print(data)
# {'time_utc': '2025-09-01T16:00', 'temperature_c': 28.1, 'wind_speed_kmh': 18.6,
#  'precipitation_mm': 0.0, 'precipitation_probability_percent': 10,
#  'source': 'open-meteo-forecast'}
