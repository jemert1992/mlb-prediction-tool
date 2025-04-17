import requests
import json
import os
from datetime import datetime

class WeatherAPI:
    """
    Class to fetch real weather data for MLB game locations
    """
    
    def __init__(self):
        """Initialize the weather API client"""
        self.api_key = "4da2a5f907a8f5bcf9d0ef8c58e9aa12"  # OpenWeatherMap API key
        self.cache_dir = 'cache/weather'
        self.cache_expiry = 3600 * 3  # Cache expiry in seconds (3 hours)
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def get_cached_data(self, city):
        """Get weather data from cache if available and not expired"""
        cache_file = os.path.join(self.cache_dir, f"{city.replace(',', '_')}.json")
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                
                # Check if cache is expired
                cache_time = cached_data.get('cache_time', 0)
                if (datetime.now() - datetime.fromtimestamp(cache_time)).total_seconds() < self.cache_expiry:
                    return cached_data.get('data')
            except Exception as e:
                print(f"Error reading weather cache: {e}")
        
        return None
    
    def save_to_cache(self, city, data):
        """Save weather data to cache"""
        cache_file = os.path.join(self.cache_dir, f"{city.replace(',', '_')}.json")
        
        try:
            with open(cache_file, 'w') as f:
                json.dump({
                    'data': data,
                    'cache_time': datetime.now().timestamp()
                }, f)
            
            return True
        except Exception as e:
            print(f"Error saving weather to cache: {e}")
            return False
    
    def get_weather(self, city):
        """
        Get current weather for a city
        """
        # Check cache first
        cached_data = self.get_cached_data(city)
        if cached_data:
            return cached_data
        
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}&units=imperial"
            response = requests.get(url)
            data = response.json()
            
            if data.get('cod') != 200:
                print(f"Error fetching weather: {data.get('message')}")
                return self.get_default_weather()
            
            weather_data = {
                'temperature': data.get('main', {}).get('temp', 70.0),
                'condition': data.get('weather', [{}])[0].get('main', 'Clear'),
                'description': data.get('weather', [{}])[0].get('description', 'clear sky'),
                'wind_speed': data.get('wind', {}).get('speed', 5.0),
                'humidity': data.get('main', {}).get('humidity', 50),
                'precipitation_chance': 0.0  # OpenWeatherMap free tier doesn't provide precipitation chance
            }
            
            # Save to cache
            self.save_to_cache(city, weather_data)
            
            return weather_data
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return self.get_default_weather()
    
    def get_default_weather(self):
        """Return default weather data if API fails"""
        return {
            'temperature': 70.0,
            'condition': 'Clear',
            'description': 'clear sky',
            'wind_speed': 5.0,
            'humidity': 50,
            'precipitation_chance': 0.0
        }
    
    def get_weather_icon(self, condition):
        """Get weather icon based on condition"""
        condition = condition.lower()
        if 'rain' in condition or 'drizzle' in condition:
            return '🌧️'
        elif 'snow' in condition:
            return '❄️'
        elif 'cloud' in condition:
            return '⛅'
        elif 'clear' in condition:
            return '☀️'
        elif 'thunder' in condition or 'storm' in condition:
            return '⛈️'
        elif 'fog' in condition or 'mist' in condition:
            return '🌫️'
        else:
            return '🌤️'

# Test the weather API
if __name__ == "__main__":
    weather_api = WeatherAPI()
    cities = ["New York,NY", "Los Angeles,CA", "Chicago,IL", "Boston,MA"]
    
    for city in cities:
        weather = weather_api.get_weather(city)
        icon = weather_api.get_weather_icon(weather['condition'])
        print(f"{city}: {icon} {weather['temperature']}°F, {weather['description']}, Wind: {weather['wind_speed']} mph")
