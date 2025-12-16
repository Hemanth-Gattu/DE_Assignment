import streamlit as st
import requests
import json
import time
from datetime import datetime, timedelta
import threading

# API Key for OpenWeatherMap API
API_KEY = "YOUR_API_KEY_HERE"

# Cache weather data for 1 hour
CACHE_EXPIRY = 3600

class WeatherApp:
    def __init__(self):
        self.cache = {}
        self.location = None
        self.weather_data = None
        self.update_thread = None

    def get_user_input(self):
        """Get user input for location"""
        return st.text_input("Enter your location (city, state, country): ")

    def validate_user_input(self, location):
        """Validate user input for correct location format"""
        try:
            location = location.split(", ")
            if len(location) != 3:
                return False
            return True
        except ValueError:
            return False

    def handle_invalid_input(self):
        """Handle invalid input (e.g., empty field, incorrect format)"""
        st.error("Invalid input. Please enter a valid location (city, state, country).")
        return self.get_user_input()

    def fetch_weather_data(self, location):
        """Fetch current weather data from OpenWeatherMap API"""
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def cache_weather_data(self, location, weather_data):
        """Cache weather data for a reasonable amount of time"""
        self.cache[location] = (weather_data, datetime.now() + timedelta(seconds=CACHE_EXPIRY))

    def get_cached_weather_data(self, location):
        """Get cached weather data if available"""
        if location in self.cache:
            weather_data, expiry_time = self.cache[location]
            if datetime.now() < expiry_time:
                return weather_data
        return None

    def display_weather_data(self, weather_data):
        """Display current weather data to the user"""
        st.write(f"Temperature: {weather_data['main']['temp']} K")
        st.write(f"Humidity: {weather_data['main']['humidity']} %")
        st.write(f"Wind Speed: {weather_data['wind']['speed']} m/s")

    def update_weather_data(self):
        """Update weather data display in real-time (e.g., every 5 minutes)"""
        while True:
            location = self.get_user_input()
            if self.validate_user_input(location):
                weather_data = self.get_cached_weather_data(location)
                if weather_data is None:
                    weather_data = self.fetch_weather_data(location)
                    if weather_data is not None:
                        self.cache_weather_data(location, weather_data)
                if weather_data is not None:
                    self.display_weather_data(weather_data)
                else:
                    st.error("Error fetching weather data.")
            else:
                location = self.handle_invalid_input()
            time.sleep(300)  # Update every 5 minutes

def main():
    app = WeatherApp()
    st.title("Weather Application")
    st.write("A web-based application that fetches current weather data from an API based on user-provided location")

    if st.button("Update Weather Data"):
        app.update_thread = threading.Thread(target=app.update_weather_data)
        app.update_thread.daemon = True
        app.update_thread.start()

    if app.location is not None:
        st.write(f"Location: {app.location}")
        if app.weather_data is not None:
            app.display_weather_data(app.weather_data)

if __name__ == "__main__":
    main()