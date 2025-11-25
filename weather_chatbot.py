import logging
import os
import re
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer, ChatterBotCorpusTrainer
from datetime import datetime, timedelta
from weather.weather_api import (
    get_weather_data,
    get_5_day_forecast,
    get_sun_times,
    get_coordinates_from_db,
    save_city_to_db
)
from models import db, City

logging.basicConfig(level=logging.INFO)


db_path = os.path.expanduser("~/ChatterBot_A2/weatherbot.sqlite3")  # use absolute path
db_dir = os.path.dirname(db_path)
os.makedirs(db_dir, exist_ok=True)


db_uri = f"sqlite:///{db_path}"


my_bot = ChatBot(
    "WeatherBot",
    storage_adapter="chatterbot.storage.SQLStorageAdapter",
    database_uri=db_uri,
    logic_adapters=[
        {
            "import_path": "chatterbot.logic.BestMatch",
            "default_response": "Sorry, I don't understand that.",
            "maximum_similarity_threshold": 0.99
        }
    ]
)

trainer = ListTrainer(my_bot) # global trainer
corpus_trainer = ChatterBotCorpusTrainer(my_bot)
corpus_trainer.train('chatterbot.corpus.english.greetings')

# def train_bot():
#     trainer.train([
#         "Hi", "Hello there!",
#         "How are you?", "I'm doing well, thanks!",
#         "Thank you", "You're welcome!",
#         "Thanks", "No problem!",
#         "Cheers", "You're welcome!"
#     ])

trainer.train([
"Hi", "Hello there!",
"How are you?", "I'm doing well, thanks!",
"Thank you", "You're welcome!",
"Thanks", "No problem!",
"Cheers", "You're welcome!"
])

places = [
        "cumbria", "corfe_castle", "the_cotswolds", "cambridge",
        "bristol", "oxford", "norwich", "stonehenge",
        "watergate_bay", "birmingham"
    ]

question_variations = [
        "What is the weather like in {place} today?",
        "What's the weather in {place}?",
        "Weather in {place}?",
        "Tell me the weather in {place}.",
        "What's the temperature in {place}?",
        "How cold is it in {place}?",
        "Is it raining in {place} today?",
        "Is it raining in {place}?",
        "Is it sunny in {place} today?",
        "Is it sunny in {place}?",
        "Give me today's forecast in {place}?"
    ]

future_forecast_phrases = [
        "What's the weather in {place} tomorrow?",
        "Weather in {place} tomorrow?",
        "Forecast for {place} tomorrow?",
        "Will it rain in {place} tomorrow?",
        "Will it be sunny in {place} tomorrow?",
        "What's the weather in {place} in 2 days?",
        "Forecast for {place} in 2 days?",
        "Weather in {place} in 3 days?",
        "Forecast for {place} in 4 days?",
        "Weather in {place} in 5 days?"
    ]

jacket_questions = [
        "Do I need a jacket in {place}?",
        "Do I need a jacket in {place} today?",
        "Will I need a jacket in {place} tomorrow?",
        "Will I need a jacket in {place} in 2 days?",
        "Will I need a jacket in {place} in 3 days?",
        "Will I need a jacket in {place} in 4 days?",
        "Will I need a jacket in {place} in 5 days?"
    ]

sun_times_questions = [
        "When is sunrise in {place}?",
        "Sunrise in {place}?",
        "Tell me sunrise time in {place}.",
        "When is sunset in {place}?",
        "Sunset in {place}?",
        "Tell me sunset time in {place}.",
        "Sunrise in {place}? tomorrow?",
        "Sunset in {place}? in 2 days?",
        "Sunset in {place}? in 3 days?",
        "Sunset in {place}? in 4 days?",
        "Sunset in {place}? in 5 days?"
    ]

five_day_questions = [
    "Forecast in {place} for next 5 days",
    "What's the weather in {place} for the next 5 days?",
    "Weather forecast for {place} for 5 days",
    "Tell me the 5-day forecast for {place}",
    "{place} forecast for next five days",
    "5 days forecast for {place}",
]

place_activities = {
    "cumbria": [
        "Go water rafting at Lake District",
        "kayak on Lake Derwentwater",
        " or go on a mountain bike guide"
    ],
    "corfe_castle":[
        "Tour Corfe Castle",
        "walk around the castle",
        "or visit local cafes"
    ],
    "the_cotswolds": [
        "Explore Blenheim Palace and Sudeley Castle",
        "visit the water park",
        "or go on a bike ride"
    ],
    "cambridge":[
        "Visit Fitzwilliam Museum",
        "walk around Cambridge University Botanic Garden",
        "or visit College Chapel"
    ],
    "bristol":[
        "Visit the Bristol Aquarium",
        "go to the Bristol Museum and Art Gallery",
        "or walk over the Clifton Suspension Bridge"
    ],
    "oxford":[
        "Go on a walking tour of the city",
        "visit the Ashmolean Museum",
        "or visit the Oxford Castle and Prison"],
    "norwich":[
        "Visit the Norwich Castle",
        "go to the Norwich Market",
        "or walk through the Plantation Garden"
    ],
    "stonehenge":[
        "Explore the stone circle",
        "visit the Visitor Centre",
        "or go on a hike nearby"
    ],
    "watergate_bay":[
        "Try some water sports",
        "walk along the beach",
        "or visit the local restaurants"
    ],
    "birmingham": [
        "Visit the National Sea Life Centre",
        "visit Winterbourne House and Gardens",
        "or see a show at the Birmingham Hippodrome"
    ],
}

city_name_map = {
    "oxford": "oxford",
    "bristol": "bristol",
    "cambridge": "cambridge",
    "birmingham": "birmingham",
    "norwich": "norwich",
    "stonehenge": "stonehenge",
    "watergate bay": "watergate_bay",
    "the cotswolds": "the_cotswolds",
    "corfe castle": "corfe_castle",
    "cumbria": "cumbria"
}

waiting_for_activity_reply = False
last_city_requested = None

# for place in places:
#     readable_place = place.replace("_", " ").title()
#     for q in question_variations + future_forecast_phrases + jacket_questions + sun_times_questions:
#         formatted_q = q.format(place=readable_place)
#         trainer.train([formatted_q, f"Let me check the forecast or sun times for {readable_place}."])
#

print("Saving conversation log to:", os.path.abspath("conversation_log.txt"))

def save_to_file(text):
    with open("conversation_log.txt", "a") as file:
        file.write(text + "\n")

def get_activities_for_place(place_key: str) -> str:
    return ", ".join(place_activities.get(place_key, ["No activities available."]))


def parse_forecast_date(user_input: str) -> datetime.date:
    today = datetime.now().date()
    if "tomorrow" in user_input.lower():
        return today + timedelta(days=1)
    match = re.search(r"in (\d+) days", user_input.lower())
    if match:
        return today + timedelta(days=int(match.group(1)))
    return today


def needs_jacket(temp: float, condition: str) -> str:
    if temp <= 10 or "rain" in condition.lower():
        return "Yes, you should wear a jacket."
    if temp <= 15 and ("cloud" in condition.lower() or "wind" in condition.lower()):
        return "Probably. It might feel cool."
    return "No, you probably won't need a jacket."


def extract_city(user_input: str):
    text = user_input.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    print("Cleaned text:", text)

    for name, key in city_name_map.items():
        if name in text:
            print("Matched city:", name)
            return key

    words = text.split()
    for w in words:
        if w in city_name_map:
            print("Matched single word city:", w)
            return city_name_map[w]

    return None


def train_bot():
    all_phrases = question_variations + future_forecast_phrases + jacket_questions + sun_times_questions + five_day_questions
    for place in places:
        readable_place = place.replace("_", " ").title()
        for q in all_phrases:
            formatted_q = q.format(place=readable_place)
            trainer.train([formatted_q, f"Let me check the forecast for {readable_place}."])

# def get_5_day_forecast(lat, lon, api_key):
#     url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"
#     response = requests.get(url)
#     data = response.json()
#
#     forecast_dict = {}
#
#     if data.get("list"):
#         for entry in data["list"]:
#             dt_txt = entry["dt_txt"]  # e.g., '2025-11-22 12:00:00'
#             date_str = dt_txt.split(" ")[0]  # '2025-11-22'
#             temp = entry["main"]["temp"]
#             condition = entry["weather"][0]["description"]
#
#             if date_str not in forecast_dict:
#                 forecast_dict[date_str] = []
#             forecast_dict[date_str].append({"temp": temp, "condition": condition})
#
#     return forecast_dict

train_bot()


def get_bot_response(user_input: str) -> str:
    global waiting_for_activity_reply, last_city_requested
    user_input_clean = user_input.lower().strip()
    save_to_file("User: " + user_input)

    bot_response = my_bot.get_response(user_input)
    response_text = None

    if waiting_for_activity_reply and last_city_requested:
        affirmative_responses = ["yes", "yes please", "sure", "yep", "yeah", "ok", "okay"]
        negative_responses = ["no", "no thanks", "nope"]


        if any(user_input_clean == resp for resp in affirmative_responses):
            response_text = (
                f"Activities in {last_city_requested.replace('_', ' ').title()}: "
                f"{get_activities_for_place(last_city_requested)}"
            )
            waiting_for_activity_reply = False
            return response_text


        if any(user_input_clean == resp for resp in negative_responses):
            response_text = "Okay! Let me know if you want anything else."
            waiting_for_activity_reply = False
            return response_text

        waiting_for_activity_reply = False


    if response_text is None:
        city = extract_city(user_input_clean)
        if city:
            last_city_requested = city
            city_key = city_name_map.get(city.replace(" ", "_").lower(), city.lower())
            lat, lon = get_coordinates_from_db(city_key)

            if lat is None or lon is None:
                response_text = f"Sorry, I don’t have weather data for {city.replace('_', ' ').title()}."
            else:
                target_date = parse_forecast_date(user_input_clean).strftime("%Y-%m-%d")

                if (
                        "next 5 days" in user_input_clean
                        or "5-day forecast" in user_input_clean
                        or "5 days forecast" in user_input_clean
                        or "5 day forecast" in user_input_clean
                        or "five day forecast" in user_input_clean
                        or re.search(r"5\s*day[s]?\s*forecast", user_input_clean)
                        or re.search(r"forecast.*5.*day", user_input_clean)
                ):
                    forecast_data = get_5_day_forecast(lat, lon)  # <-- Use lat/lon, not city name

                    if forecast_data:
                        response_text = f"5-day forecast for {city.replace('_', ' ').title()}:<br>"
                        for date, entries in forecast_data.items():
                            avg_temp = sum(e["temp"] for e in entries) / len(entries)
                            conditions = [e["condition"] for e in entries]
                            most_common_condition = max(set(conditions), key=conditions.count)


                            date_obj = datetime.strptime(date, "%Y-%m-%d")
                            day_name = date_obj.strftime("%A")

                            #Adds bullet point to answer, and formats answer more clearly
                            response_text += f"&bull; {day_name} ({date}): {avg_temp:.1f}°C, {most_common_condition}<br>"
                    else:
                        response_text = f"Sorry, 5-day forecast for {city.replace('_', ' ').title()} is not available."


                elif "sunrise" in user_input_clean or "sunset" in user_input_clean:
                    sun_times = get_sun_times(lat, lon)
                    if "sunrise" in user_input_clean:
                        response_text = f"The sunrise in {city.replace('_', ' ').title()} on {target_date} is at {sun_times['sunrise']}."
                    else:
                        response_text = f"The sunset in {city.replace('_', ' ').title()} on {target_date} is at {sun_times['sunset']}."


                elif "weather" in user_input_clean or "jacket" in user_input_clean:
                    forecast_data = get_5_day_forecast(lat, lon)
                    if target_date in forecast_data:
                        entries = forecast_data[target_date]
                        avg_temp = sum(e["temp"] for e in entries) / len(entries)
                        conditions = [e["condition"] for e in entries]
                        most_common_condition = max(set(conditions), key=conditions.count)

                        response_text = (
                            f"Forecast for {city.replace('_', ' ').title()} on {target_date}: "
                            f"{avg_temp:.1f}°C, {most_common_condition}."
                        )
                        if "jacket" in user_input_clean:
                            response_text += " " + needs_jacket(avg_temp, most_common_condition)
                        response_text += f" Would you like activities to do in {city.replace('_', ' ').title()}?"
                        waiting_for_activity_reply = True
                    else:
                        response_text = f"Sorry, forecast for {target_date} is not available."


    if response_text is None:
        response_text = str(bot_response)

    save_to_file("Bot: " + response_text)
    return response_text