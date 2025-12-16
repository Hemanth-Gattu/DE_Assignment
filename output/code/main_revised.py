import requests
import geocoder
from cachetools import cached, TTLCache
from enum import Enum
from typing import Dict, List

# Constants
API_KEY = "YOUR_OPENWEATHERMAP_API_KEY"
CACHE_SIZE = 100
CACHE_TTL = 60  # 1 minute

# Data Models
class WeatherData:
    def __init__(self, id: str, temperature: float, humidity: float, wind_speed: float, weather_conditions: str, weather_icon: str):
        self.id = id
        self.temperature = temperature
        self.humidity = humidity
        self.wind_speed = wind_speed
        self.weather_conditions = weather_conditions
        self.weather_icon = weather_icon

class Location:
    def __init__(self, id: str, name: str, latitude: float, longitude: float):
        self.id = id
        self.name = name
        self.latitude = latitude
        self.longitude = longitude

# Enum for units of measurement
class Units(Enum):
    METRIC = "metric"
    IMPERIAL = "imperial"

# Enum for language
class Language(Enum):
    ENGLISH = "en"
    SPANISH = "es"

# Function to fetch weather data from OpenWeatherMap API
@cached(cache=TTLCache(maxsize=CACHE_SIZE, ttl=CACHE_TTL))  # Cache weather data for 1 minute
def fetch_weather_data(api_key: str, location_id: str, units: Units, language: Language) -> Dict:
    try:
        base_url = f"http://api.openweathermap.org/data/2.5/weather?id={location_id}&appid={api_key}&units={units.value}&lang={language.value}"
        response = requests.get(base_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        return {
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "weather_conditions": data["weather"][0]["description"],
            "weather_icon": data["weather"][0]["icon"]
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None

# Function to fetch 5-day forecast from OpenWeatherMap API
@cached(cache=TTLCache(maxsize=CACHE_SIZE, ttl=CACHE_TTL))  # Cache 5-day forecast for 1 minute
def fetch_forecast(api_key: str, location_id: str, units: Units, language: Language) -> List[Dict]:
    try:
        base_url = f"http://api.openweathermap.org/data/2.5/forecast?id={location_id}&appid={api_key}&units={units.value}&lang={language.value}"
        response = requests.get(base_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        forecast = []
        for item in data["list"]:
            forecast.append({
                "date": item["dt_txt"],
                "temperature": item["main"]["temp"],
                "humidity": item["main"]["humidity"],
                "wind_speed": item["wind"]["speed"],
                "weather_conditions": item["weather"][0]["description"],
                "weather_icon": item["weather"][0]["icon"]
            })
        return forecast
    except requests.exceptions.RequestException as e:
        print(f"Error fetching forecast: {e}")
        return None

# Function to get user location
def get_user_location() -> Location:
    try:
        g = geocoder.ip("me")
        return Location(g.latlng[0], g.city, g.latlng[0], g.latlng[1])
    except Exception as e:
        print(f"Error getting user location: {e}")
        return None

# Function to display weather data
def display_weather_data(weather_data: WeatherData, forecast: List[Dict]):
    if weather_data is None or forecast is None:
        print("Error: Weather data or forecast is not available.")
        return

    print(f"Current Weather:")
    print(f"Temperature: {weather_data.temperature}°{get_units_symbol(weather_data.temperature)}")
    print(f"Humidity: {weather_data.humidity}%")
    print(f"Wind Speed: {weather_data.wind_speed} m/s")
    print(f"Weather Conditions: {weather_data.weather_conditions}")
    print(f"Weather Icon: {weather_data.weather_icon}")
    print("\n5-Day Forecast:")
    for item in forecast:
        print(f"{item['date']}:")
        print(f"Temperature: {item['temperature']}°{get_units_symbol(item['temperature'])}")
        print(f"Humidity: {item['humidity']}%")
        print(f"Wind Speed: {item['wind_speed']} m/s")
        print(f"Weather Conditions: {item['weather_conditions']}")
        print(f"Weather Icon: {item['weather_icon']}")
        print()

# Function to get units symbol
def get_units_symbol(temperature: float) -> str:
    if temperature < 0:
        return "C"
    else:
        return "F"

# Function to validate user-input location
def validate_location(location: str) -> bool:
    try:
        g = geocoder.search(location)
        return g.latlng is not None
    except Exception as e:
        print(f"Error validating location: {e}")
        return False

# Function to display suggested locations
def display_suggested_locations(locations: List[Location]):
    if locations is None:
        print("Error: No suggested locations available.")
        return

    print("Suggested Locations:")
    for location in locations:
        print(f"{location.name} ({location.latitude}, {location.longitude})")

# Function to get user's preferred units of measurement
def get_user_units() -> Units:
    while True:
        print("Select your preferred units of measurement:")
        print("1. Metric (Celsius)")
        print("2. Imperial (Fahrenheit)")
        choice = input("Enter your choice (1/2): ")
        if choice == "1":
            return Units.METRIC
        elif choice == "2":
            return Units.IMPERIAL
        else:
            print("Invalid choice. Please try again.")

# Function to get user's preferred language
def get_user_language() -> Language:
    while True:
        print("Select your preferred language:")
        print("1. English")
        print("2. Spanish")
        choice = input("Enter your choice (1/2): ")
        if choice == "1":
            return Language.ENGLISH
        elif choice == "2":
            return Language.SPANISH
        else:
            print("Invalid choice. Please try again.")

# Function to handle exceptions
def handle_exception(e: Exception):
    print(f"Error: {e}")

# Main function
def main():
    try:
        api_key = API_KEY
        location = get_user_location()
        if location is None:
            print("Error: Unable to get user location.")
            return

        units = get_user_units()
        language = get_user_language()
        suggested_locations = geocoder.search(location.name)
        if validate_location(location.name):
            print("Location is valid.")
        else:
            print("Location is not valid. Please try again.")
            return

        weather_data = fetch_weather_data(api_key, location.id, units, language)
        forecast = fetch_forecast(api_key, location.id, units, language)
        display_weather_data(WeatherData(location.id, weather_data["temperature"], weather_data["humidity"], weather_data["wind_speed"], weather_data["weather_conditions"], weather_data["weather_icon"]), forecast)
        display_suggested_locations(suggested_locations)
    except Exception as e:
        handle_exception(e)

if __name__ == "__main__":
    main()