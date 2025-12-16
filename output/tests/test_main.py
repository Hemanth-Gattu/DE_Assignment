import pytest
import requests
import json
from datetime import datetime, timedelta
from weather_app import WeatherApp

# API Key for OpenWeatherMap API
API_KEY = "YOUR_API_KEY_HERE"

class TestWeatherApp:
    def setup_method(self):
        self.app = WeatherApp()

    def test_get_user_input(self):
        """Test get_user_input method"""
        location = self.app.get_user_input()
        assert isinstance(location, str)

    def test_validate_user_input(self):
        """Test validate_user_input method"""
        location = "New York, NY, USA"
        assert self.app.validate_user_input(location) is True
        location = "Invalid location"
        assert self.app.validate_user_input(location) is False

    def test_handle_invalid_input(self):
        """Test handle_invalid_input method"""
        location = self.app.handle_invalid_input()
        assert isinstance(location, str)

    def test_fetch_weather_data(self, mock_requests_get):
        """Test fetch_weather_data method"""
        location = "New York, NY, USA"
        mock_requests_get.return_value.status_code = 200
        mock_requests_get.return_value.json.return_value = {"main": {"temp": 300}, "wind": {"speed": 10}}
        weather_data = self.app.fetch_weather_data(location)
        assert weather_data is not None
        assert isinstance(weather_data, dict)

    def test_fetch_weather_data_invalid_response(self, mock_requests_get):
        """Test fetch_weather_data method with invalid response"""
        location = "New York, NY, USA"
        mock_requests_get.return_value.status_code = 404
        weather_data = self.app.fetch_weather_data(location)
        assert weather_data is None

    def test_cache_weather_data(self):
        """Test cache_weather_data method"""
        location = "New York, NY, USA"
        weather_data = {"main": {"temp": 300}, "wind": {"speed": 10}}
        self.app.cache_weather_data(location, weather_data)
        assert location in self.app.cache

    def test_get_cached_weather_data(self):
        """Test get_cached_weather_data method"""
        location = "New York, NY, USA"
        weather_data = {"main": {"temp": 300}, "wind": {"speed": 10}}
        self.app.cache_weather_data(location, weather_data)
        cached_weather_data = self.app.get_cached_weather_data(location)
        assert cached_weather_data is not None
        assert isinstance(cached_weather_data, dict)

    def test_get_cached_weather_data_expired(self):
        """Test get_cached_weather_data method with expired cache"""
        location = "New York, NY, USA"
        weather_data = {"main": {"temp": 300}, "wind": {"speed": 10}}
        self.app.cache_weather_data(location, weather_data)
        self.app.cache[location] = (weather_data, datetime.now() - timedelta(seconds=self.app.CACHE_EXPIRY))
        cached_weather_data = self.app.get_cached_weather_data(location)
        assert cached_weather_data is None

    def test_display_weather_data(self):
        """Test display_weather_data method"""
        weather_data = {"main": {"temp": 300}, "wind": {"speed": 10}}
        self.app.display_weather_data(weather_data)
        assert True  # This test is more of a sanity check, as the method doesn't return anything

    def test_update_weather_data(self, mock_requests_get):
        """Test update_weather_data method"""
        mock_requests_get.return_value.status_code = 200
        mock_requests_get.return_value.json.return_value = {"main": {"temp": 300}, "wind": {"speed": 10}}
        self.app.update_weather_data()

@pytest.fixture
def mock_requests_get(mocker):
    return mocker.patch("requests.get")

@pytest.fixture
def mock_requests_post(mocker):
    return mocker.patch("requests.post")

@pytest.fixture
def mock_requests_put(mocker):
    return mocker.patch("requests.put")

@pytest.fixture
def mock_requests_delete(mocker):
    return mocker.patch("requests.delete")

