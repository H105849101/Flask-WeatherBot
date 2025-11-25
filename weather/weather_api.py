import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging
from models import db, City



load_dotenv()
api_key = os.getenv("OPENWEATHER_API_KEY")
if not api_key:
    raise RuntimeError("OPENWEATHER_API_KEY is not set in .env")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# tf = TimezoneFinder()

# travel_locations = {
#     'cumbria': {'latitude': 54.4609, 'longitude': -3.0886},
#     'corfe_castle': {'latitude': 50.6395, 'longitude': -2.0566},
#     'the_cotswolds': {'latitude': 51.8330, 'longitude': -1.8433},
#     'cambridge': {'latitude': 52.2053, 'longitude': 0.1218},
#     'bristol': {'latitude': 51.4545, 'longitude': -2.5879},
#     'oxford': {'latitude': 51.7520, 'longitude': -1.2577},
#     'norwich': {'latitude': 52.6309, 'longitude': 1.2974},
#     'stonehenge': {'latitude': 51.1789, 'longitude': -1.8262},
#     'watergate_bay': {'latitude': 50.4429, 'longitude': -5.0553},
#     'birmingham': {'latitude': 52.4862, 'longitude': -1.8904}
# }

def save_city_to_db(city, lat, lon):
    if not City.query.filter_by(name=city.lower()).first():
        new_city = City(name=city.lower(), lat=lat, lon=lon)
        db.session.add(new_city)
        db.session.commit()

def get_coordinates_from_db(city):
    record = City.query.filter_by(name=city.lower()).first()
    if record:
        return record.lat, record.lon
    return None, None


def populate_cities():
    cities = {
        "cumbria": (54.4609, -3.0886),
        "corfe_castle": (50.6395, -2.0566),
        "the_cotswolds": (51.8330, -1.8433),
        "cambridge": (52.2053, 0.1218),
        "bristol": (51.4545, -2.5879),
        "oxford": (51.7520, -1.2577),
        "norwich": (52.6309, 1.2974),
        "stonehenge": (51.1789, -1.8262),
        "watergate_bay": (50.4429, -5.0553),
        "birmingham": (52.4862, -1.8904)
    }

    for name, (lat, lon) in cities.items():
        save_city_to_db(name, lat, lon)




# def init_locations_db():
#     with sqlite3.connect("locations.db") as conn:
#         cursor = conn.cursor()
#         cursor.execute("""
#         CREATE TABLE IF NOT EXISTS locations (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT UNIQUE,
#             latitude REAL,
#             longitude REAL
#         )
#         """)
#         locations_data = [
#             ("cumbria", 54.4609, -3.0886),
#             ("corfe_castle", 50.6395, -2.0566),
#             ("the_cotswolds", 51.8330, -1.8433),
#             ("cambridge", 52.2053, 0.1218),
#             ("bristol", 51.4545, -2.5879),
#             ("oxford", 51.7520, -1.2577),
#             ("norwich", 52.6309, 1.2974),
#             ("stonehenge", 51.1789, -1.8262),
#             ("watergate_bay", 50.4429, -5.0553),
#             ("birmingham", 52.4862, -1.8904)
#         ]
#         for name, lat, lon in locations_data:
#             cursor.execute("""
#             INSERT OR IGNORE INTO locations (name, latitude, longitude)
#             VALUES (?, ?, ?)
#             """, (name, lat, lon))
#         conn.commit()
#
#
#         return [loc[0] for loc in locations_data]
#
# # Run once at startup
# init_locations_db()


def get_weather_data(city: str) -> dict:
    lat, lon = get_coordinates_from_db(city)
    if lat is None or lon is None:
        return {"error": "Unknown city."}


    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {"lat": lat, "lon": lon, "appid": api_key, "units": "metric"}
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        return {
            "city": city,
            "temperature": data["main"]["temp"],
            "condition": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"]
        }
    except Exception as e:
        logging.error(f"Error fetching weather for {city}: {e}")
        return {"error": "Unable to fetch weather data"}



def get_5_day_forecast(lat: float, lon: float) -> dict:
    try:
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {"lat": lat, "lon": lon, "appid": api_key, "units": "metric"}
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        forecast_dict = {}
        for entry in data.get("list", []):
            date_str = entry["dt_txt"].split(" ")[0]
            temp = entry["main"]["temp"]
            condition = entry["weather"][0]["description"]
            forecast_dict.setdefault(date_str, []).append({"temp": temp, "condition": condition})
        return forecast_dict
    except Exception as e:
        logging.error(f"Error fetching forecast for coordinates {lat},{lon}: {e}")
        return {"error": "Unable to fetch forecast"}

def get_sun_times(lat: float, lon: float, city_name: str = None) -> dict:
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {"lat": lat, "lon": lon, "appid": api_key}

        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        sunrise_utc = datetime.utcfromtimestamp(data["sys"]["sunrise"])
        sunset_utc = datetime.utcfromtimestamp(data["sys"]["sunset"])
        tz_offset = data["timezone"]  # seconds

        sunrise_local = sunrise_utc + timedelta(seconds=tz_offset)
        sunset_local = sunset_utc + timedelta(seconds=tz_offset)

        return {
            "sunrise": sunrise_local.strftime("%H:%M"),
            "sunset": sunset_local.strftime("%H:%M")
        }
    except Exception as e:
        logging.error(f"Error fetching sun times for {city_name or lat}:{lon}: {e}")
        return {"error": "Unable to fetch sun times"}


# @app.route("/weather/<city>")
# def get_weather(city):
#     start = time.time()
#     data = get_weather_data(city)
#     duration = time.time() - start
#     logging.info(f"Weather data fetched in {duration:.2f} seconds for {city}")
#     return jsonify(data)
#
# @app.route("/forecast/<city>")
# def forecast_route(city):
#     data = get_5_day_forecast(city)
#     return jsonify(data)
#
# @app.route("/sun/<city>")
# def sun_route(city):
#     coords = get_coordinates_from_db(city)
#     if coords is None:
#         return jsonify({"error": "Unknown city."})
#     lat, lon = coords
#     data = get_sun_times(lat, lon)
#     if not data:
#         return jsonify({"error": "Unable to fetch sun times."})
#     return jsonify(data)
#
# if __name__ == "__main__":
#     app.run(debug=True)