from weather_chatbot import parse_forecast_date, needs_jacket



def test_parse_forecast_date():
    date = parse_forecast_date("weather for tomorrow")
    assert date is not None

def test_needs_jacket_cold_weather():
    assert "jacket" in needs_jacket(8, "cloudy")

def test_needs_jacket_hot_weather():
    assert "no jacket" in needs_jacket(25, "clear sky")