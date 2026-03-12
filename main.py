import tkinter as tk
from tkinter import ttk, messagebox
import requests
from datetime import datetime
import pandas as pd
import os
from background_manager import BackgroundManager

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Application")
        self.root.geometry("423x630")
        self.root.resizable(False, False)
        
        # API Configuration - Open-Meteo (100% Free, No API Key Required!)
        # Using Open-Meteo: https://open-meteo.com
        self.GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
        self.WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
        
        # Variables
        self.temp_unit = tk.StringVar(value="C")
        self.search_history = []
        
        # Create main container
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        title_label = ttk.Label(
            self.main_frame,
            text="Weather Application",
            font=('Helvetica', 24, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(20, 20))
        
        # Initialize background manager
        self.bg_manager = BackgroundManager(self.main_frame)
        
        # Location Input Section
        self.create_location_section()
        
        # Weather Information Display
        self.create_weather_display()
        
        # Forecast Section
        self.create_forecast_section()
        
        # Date & Time Display
        self.create_datetime_display()
        
        # Footer
        self.create_footer()
        
        # Initialize Excel logging
        self.initialize_excel_log()
        
        # Update time display
        self.update_datetime()
    
    def create_location_section(self):
        # Add title directly in main frame
        
        
        location_frame = ttk.LabelFrame(self.main_frame, text="Location", padding="10")
        location_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # City entry with history
        self.city_var = tk.StringVar()
        self.city_combo = ttk.Combobox(location_frame, textvariable=self.city_var, width=30)
        self.city_combo.grid(row=0, column=0, padx=5)
        self.city_combo.bind('<Return>', lambda e: self.get_weather())
        
        # Get Weather button
        get_weather_btn = ttk.Button(location_frame, text="Get Weather", command=self.get_weather)
        get_weather_btn.grid(row=0, column=1, padx=5)
        
        # Temperature unit toggle
        unit_frame = ttk.Frame(location_frame)
        unit_frame.grid(row=0, column=2, padx=5)
        
        ttk.Radiobutton(unit_frame, text="°C", variable=self.temp_unit, 
                       value="C", command=self.update_temperature_display).pack(side=tk.LEFT)
        ttk.Radiobutton(unit_frame, text="°F", variable=self.temp_unit, 
                       value="F", command=self.update_temperature_display).pack(side=tk.LEFT)
    
    def create_weather_display(self):
        weather_frame = ttk.LabelFrame(self.main_frame, text="Weather Information", padding="5")
        weather_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Weather Icon
        self.weather_icon_label = ttk.Label(weather_frame)
        self.weather_icon_label.grid(row=0, column=0, rowspan=2, padx=10)
        
        # Temperature and Condition
        self.temp_label = ttk.Label(weather_frame, text="Temperature: --°C", font=("Arial", 14))
        self.temp_label.grid(row=0, column=1, sticky=tk.W)
        
        self.condition_label = ttk.Label(weather_frame, text="Condition: --")
        self.condition_label.grid(row=1, column=1, sticky=tk.W)
        
        # Detailed Information
        details_frame = ttk.Frame(weather_frame)
        details_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        self.feels_like_label = ttk.Label(details_frame, text="Feels Like: --°C")
        self.feels_like_label.grid(row=0, column=0, sticky=tk.W, padx=5)
        
        self.humidity_label = ttk.Label(details_frame, text="Humidity: --%")
        self.humidity_label.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        self.wind_label = ttk.Label(details_frame, text="Wind: -- km/h")
        self.wind_label.grid(row=1, column=0, sticky=tk.W, padx=5)
        
        self.pressure_label = ttk.Label(details_frame, text="Pressure: -- hPa")
        self.pressure_label.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        self.visibility_label = ttk.Label(details_frame, text="Visibility: -- km")
        self.visibility_label.grid(row=2, column=0, sticky=tk.W, padx=5)
        
        self.sunrise_label = ttk.Label(details_frame, text="Sunrise: --")
        self.sunrise_label.grid(row=2, column=1, sticky=tk.W, padx=5)
        
        self.sunset_label = ttk.Label(details_frame, text="Sunset: --")
        self.sunset_label.grid(row=3, column=0, sticky=tk.W, padx=5)
    
    def create_forecast_section(self):
        forecast_frame = ttk.LabelFrame(self.main_frame, text="5-Day Forecast", padding="5")
        forecast_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Create frames for each day
        self.forecast_labels = []
        for i in range(5):
            day_frame = ttk.Frame(forecast_frame)
            day_frame.grid(row=0, column=i, padx=5, pady=5)
            
            # Day label
            day_label = ttk.Label(day_frame, text=f"Day {i+1}")
            day_label.grid(row=0, column=0)
            
            # Weather icon
            icon_label = ttk.Label(day_frame)
            icon_label.grid(row=1, column=0)
            
            # Temperature
            temp_label = ttk.Label(day_frame, text="--°C")
            temp_label.grid(row=2, column=0)
            
            # Condition
            condition_label = ttk.Label(day_frame, text="--")
            condition_label.grid(row=3, column=0)
            
            self.forecast_labels.append({
                'day': day_label,
                'icon': icon_label,
                'temp': temp_label,
                'condition': condition_label
            })
    
    def create_datetime_display(self):
        datetime_frame = ttk.Frame(self.main_frame)
        datetime_frame.grid(row=4, column=0, columnspan=2, pady=5)
        
        self.date_label = ttk.Label(datetime_frame, text="Date: --")
        self.date_label.grid(row=0, column=0, padx=5)
        
        self.time_label = ttk.Label(datetime_frame, text="Time: --")
        self.time_label.grid(row=0, column=1, padx=5)
        
        self.last_updated_label = ttk.Label(datetime_frame, text="Last Updated: --")
        self.last_updated_label.grid(row=0, column=2, padx=5)
    
    def create_footer(self):
        footer_frame = ttk.Frame(self.main_frame)
        footer_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        copyright_label = ttk.Label(
            footer_frame, 
            text="© 2025 Weather Application. All rights reserved.",
            font=('Helvetica', 8)
        )
        copyright_label.grid(row=0, column=0, padx=5)
        
    
    def get_weather(self):
        city = self.city_var.get()
        if not city:
            messagebox.showerror("Error", "Please enter a city name")
            return
        
        try:
            # Step 1: Get coordinates from city name using geocoding
            geo_params = {'name': city, 'count': 1, 'language': 'en', 'format': 'json'}
            geo_response = requests.get(self.GEOCODING_URL, params=geo_params)
            geo_data = geo_response.json()
            
            if not geo_data.get('results'):
                messagebox.showerror("Error", f"City '{city}' not found. Please check the spelling.")
                return
            
            # Get coordinates
            location = geo_data['results'][0]
            lat = location['latitude']
            lon = location['longitude']
            city_name = location['name']
            country = location.get('country', '')
            
            # Step 2: Get weather data using coordinates
            weather_params = {
                'latitude': lat,
                'longitude': lon,
                'current': 'temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,cloud_cover,pressure_msl,surface_pressure,wind_speed_10m,wind_direction_10m',
                'daily': 'weather_code,temperature_2m_max,temperature_2m_min,sunrise,sunset,precipitation_sum',
                'timezone': 'auto'
            }
            
            weather_response = requests.get(self.WEATHER_URL, params=weather_params)
            weather_data = weather_response.json()
            
            if weather_response.status_code == 200:
                # Add location info to weather data
                weather_data['location'] = {'name': city_name, 'country': country}
                
                self.update_weather_display(weather_data)
                self.log_to_excel(weather_data)
                self.update_forecast_display(weather_data)
                
                # Update search history
                if city not in self.search_history:
                    self.search_history.append(city)
                    self.city_combo['values'] = self.search_history
                
                # Update background color based on weather
                weather_code = weather_data['current']['weather_code']
                condition = self.get_weather_condition(weather_code)
                self.bg_manager.update_background(condition)
            else:
                messagebox.showerror("Error", f"Failed to fetch weather data")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch weather data: {str(e)}")
    
    def update_weather_display(self, data):
        # Store for temperature unit conversion
        self.last_weather_data = data
        
        # Update main weather information from Open-Meteo
        current = data['current']
        daily = data['daily']
        
        temp = current['temperature_2m']
        feels_like = current['apparent_temperature']
        humidity = current['relative_humidity_2m']
        wind_speed = current['wind_speed_10m']
        pressure = current.get('surface_pressure', current.get('pressure_msl', 0))
        weather_code = current['weather_code']
        condition = self.get_weather_condition(weather_code)
        
        # Get sunrise and sunset from daily data
        sunrise = datetime.fromisoformat(daily['sunrise'][0]).strftime('%H:%M')
        sunset = datetime.fromisoformat(daily['sunset'][0]).strftime('%H:%M')
        
        # Visibility (Open-Meteo doesn't provide this, so we'll estimate from cloud cover)
        cloud_cover = current.get('cloud_cover', 0)
        visibility = 10 - (cloud_cover / 10)  # Rough estimate
        
        # Convert temperature based on selected unit
        if self.temp_unit.get() == "F":
            temp = (temp * 9/5) + 32
            feels_like = (feels_like * 9/5) + 32
            temp_unit = "°F"
        else:
            temp_unit = "°C"
        
        # Update labels
        self.temp_label.config(text=f"Temperature: {temp:.1f}{temp_unit}")
        self.condition_label.config(text=f"Condition: {condition}")
        self.feels_like_label.config(text=f"Feels Like: {feels_like:.1f}{temp_unit}")
        self.humidity_label.config(text=f"Humidity: {humidity}%")
        self.wind_label.config(text=f"Wind: {wind_speed:.1f} km/h")
        self.pressure_label.config(text=f"Pressure: {pressure:.1f} hPa")
        self.visibility_label.config(text=f"Visibility: ~{visibility:.1f} km")
        self.sunrise_label.config(text=f"Sunrise: {sunrise}")
        self.sunset_label.config(text=f"Sunset: {sunset}")
        
        # Update last updated time
        current_time = datetime.now().strftime('%H:%M:%S')
        self.last_updated_label.config(text=f"Last Updated: {current_time}")
        
        # Update weather icon (using emoji or text since Open-Meteo doesn't provide icons)
        self.update_weather_icon(weather_code)
    
    def update_forecast_display(self, data):
        # Store for temperature unit conversion
        self.last_forecast_data = data
        
        # Get forecast for next 5 days from Open-Meteo daily data
        daily = data['daily']
        
        # Update forecast labels for next 5 days
        for i in range(min(5, len(daily['time']))):
            if i < len(self.forecast_labels):
                # Get forecast data
                date_str = daily['time'][i]
                temp_max = daily['temperature_2m_max'][i]
                temp_min = daily['temperature_2m_min'][i]
                avg_temp = (temp_max + temp_min) / 2
                weather_code = daily['weather_code'][i]
                condition = self.get_weather_condition(weather_code)
                
                # Convert temperature based on selected unit
                if self.temp_unit.get() == "F":
                    avg_temp = (avg_temp * 9/5) + 32
                    temp_unit = "°F"
                else:
                    temp_unit = "°C"
                
                # Parse date
                forecast_date = datetime.fromisoformat(date_str)
                day_name = forecast_date.strftime('%a')
                
                # Update labels
                self.forecast_labels[i]['day'].config(text=day_name)
                self.forecast_labels[i]['temp'].config(text=f"{avg_temp:.1f}{temp_unit}")
                self.forecast_labels[i]['condition'].config(text=condition)
                
                # Update icon
                self.update_forecast_icon(i, weather_code)
    
    def update_forecast_icon(self, index, weather_code):
        # Use emoji for weather icons
        emoji = self.get_weather_emoji(weather_code)
        self.forecast_labels[index]['icon'].config(text=emoji, font=('Arial', 32))
    
    def update_temperature_display(self):
        # Refresh display with new temperature unit
        if hasattr(self, 'last_weather_data'):
            self.update_weather_display(self.last_weather_data)
            if hasattr(self, 'last_forecast_data'):
                self.update_forecast_display(self.last_forecast_data)
    
    def initialize_excel_log(self):
        # Create data folder if it doesn't exist
        data_folder = "data"
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)
            
        self.excel_file = os.path.join(data_folder, "weather_log.xlsx")
        if not os.path.exists(self.excel_file):
            df = pd.DataFrame(columns=[
                "Date", "Time", "City", "Temperature", "Condition",
                "Humidity", "Wind Speed", "Pressure", "Visibility"
            ])
            df.to_excel(self.excel_file, index=False)
    
    def update_datetime(self):
        current_time = datetime.now()
        self.date_label.config(text=f"Date: {current_time.strftime('%Y-%m-%d')}")
        self.time_label.config(text=f"Time: {current_time.strftime('%H:%M:%S')}")
        self.root.after(1000, self.update_datetime)
    
    def update_weather_icon(self, weather_code):
        # Use emoji for weather icons
        emoji = self.get_weather_emoji(weather_code)
        self.weather_icon_label.config(text=emoji, font=('Arial', 48))
    
    def get_weather_condition(self, code):
        """Convert WMO weather code to condition string"""
        conditions = {
            0: "Clear", 1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
            45: "Foggy", 48: "Foggy", 51: "Light Drizzle", 53: "Drizzle",
            55: "Heavy Drizzle", 61: "Light Rain", 63: "Rain", 65: "Heavy Rain",
            71: "Light Snow", 73: "Snow", 75: "Heavy Snow", 77: "Snow Grains",
            80: "Light Showers", 81: "Showers", 82: "Heavy Showers",
            85: "Light Snow Showers", 86: "Snow Showers", 95: "Thunderstorm",
            96: "Thunderstorm with Hail", 99: "Thunderstorm with Hail"
        }
        return conditions.get(code, "Unknown")
    
    def get_weather_emoji(self, code):
        """Convert WMO weather code to emoji"""
        emojis = {
            0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️",
            45: "🌫️", 48: "🌫️", 51: "🌦️", 53: "🌦️",
            55: "🌧️", 61: "🌧️", 63: "🌧️", 65: "⛈️",
            71: "🌨️", 73: "🌨️", 75: "❄️", 77: "🌨️",
            80: "🌦️", 81: "🌧️", 82: "⛈️",
            85: "🌨️", 86: "❄️", 95: "⛈️",
            96: "⛈️", 99: "⛈️"
        }
        return emojis.get(code, "🌡️")
    
    def log_to_excel(self, data):
        try:
            # Create new data dictionary from Open-Meteo data
            current = data['current']
            location = data.get('location', {})
            city_name = location.get('name', self.city_var.get())
            
            new_data = {
                "Date": datetime.now().strftime('%Y-%m-%d'),
                "Time": datetime.now().strftime('%H:%M:%S'),
                "City": city_name,
                "Temperature": current['temperature_2m'],
                "Condition": self.get_weather_condition(current['weather_code']),
                "Humidity": current['relative_humidity_2m'],
                "Wind Speed": current['wind_speed_10m'],
                "Pressure": current.get('surface_pressure', current.get('pressure_msl', 0)),
                "Visibility": 10 - (current.get('cloud_cover', 0) / 10)
            }
            
            # Read existing data or create new DataFrame
            if os.path.exists(self.excel_file):
                df = pd.read_excel(self.excel_file)
                # Convert new_data to DataFrame with same columns
                new_df = pd.DataFrame([new_data], columns=df.columns)
                # Concatenate with proper dtypes
                df = pd.concat([df, new_df], ignore_index=True)
            else:
                # Create new DataFrame if file doesn't exist
                df = pd.DataFrame([new_data])
            
            # Save to Excel
            df.to_excel(self.excel_file, index=False)
            
        except Exception as e:
            print(f"Failed to log to Excel: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop() 
