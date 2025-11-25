from weather_chatbot import extract_city, get_bot_response



def test_extract_city():
    assert extract_city("weather in Paris") == "paris"

def test_bot_response_unknown_city():
    response = get_bot_response("weather in Atlantis")
    assert "don't have data" in response.lower()