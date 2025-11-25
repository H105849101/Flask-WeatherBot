from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, render_template, jsonify
import os
from models import db, City
from weather.weather_api import get_weather_data, get_5_day_forecast, api_key, populate_cities
from weather_chatbot import get_bot_response, train_bot


app = Flask(__name__)
db_path = os.path.join(os.path.dirname(__file__), "SQL_db.db")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


with app.app_context():
    db.create_all()
    populate_cities()


train_bot()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/weather/<city>")
def weather(city):
    data = get_weather_data(city)
    return jsonify(data)

@app.route("/forecast/<city>")
def forecast(city):
    forecast_data = get_5_day_forecast(city, api_key)
    return jsonify(forecast_data)


@app.route("/chat", methods=["POST"])
def chat_route():
    user_message = request.json.get("message", "").strip()

    if not user_message:
        return jsonify({"response": "Please send a message."})


    print("User message received:", user_message)


    bot_response = get_bot_response(user_message)


    from weather_chatbot import extract_city, get_coordinates_from_db
    city = extract_city(user_message)
    if city:
        lat, lon = get_coordinates_from_db(city)
        print(f"Extracted city: {city}, Coordinates: ({lat}, {lon})")
    else:
        print("No city extracted from message.")

    return jsonify({"response": bot_response})

if __name__ == "__main__":
    from threading import Timer
    Timer(1, lambda: os.system("open http://127.0.0.1:5000/")).start()
    app.run(debug=True)