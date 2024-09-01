import requests
import pandas as pd
import schedule
import time
from datetime import datetime
import sqlite3
from dotenv import load_dotenv
import os
import tkinter as tk

load_dotenv()
API_KEY = os.getenv("API_KEY")  # Replace with your API key

your_city = [
    "Hong Kong",
    "Republic of the Congo, CG",
    "Bath, GB",
    "Odense, DK",
    "Republic of Austria, AT",
    "Budapest, HU",
    "Jakarta, ID",
    "Edinburgh, GB",
]

# Define a database and table
conn = sqlite3.connect("pipeline.db")
cursor = conn.cursor()
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS weather_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        temperature REAL,
        feels_like REAL,
        temperature_min REAL,
        temperature_max REAL,
        pressure REAL,
        humidity REAL,
        visibility INTEGER,
        wind_speed REAL,
        wind_deg REAL,
        cloudiness INTEGER,
        weather_description TEXT,
        weather_main TEXT,
        city_name TEXT,
        country_code TEXT,
        sunrise TEXT,
        sunset TEXT
    );
"""
)
conn.commit()
conn.close()


def fetch_weather_data(schedule_minutes, message_area):
    track_number_of_BatchFetch = 0
    for city in your_city:
        API_URL = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(API_URL)
        if response.status_code == 200:
            data = response.json()
            weather_data = {
                "timestamp": datetime.now().isoformat(),
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "temperature_min": data["main"]["temp_min"],
                "temperature_max": data["main"]["temp_max"],
                "pressure": data["main"]["pressure"],
                "humidity": data["main"]["humidity"],
                "visibility": data["visibility"],
                "wind_speed": data["wind"]["speed"],
                "wind_deg": data["wind"]["deg"],
                "cloudiness": data["clouds"]["all"],
                "weather_description": data["weather"][0]["description"],
                "weather_main": data["weather"][0]["main"],
                "city_name": data["name"],
                "country_code": data["sys"]["country"],
                "sunrise": datetime.fromtimestamp(data["sys"]["sunrise"]).isoformat(),
                "sunset": datetime.fromtimestamp(data["sys"]["sunset"]).isoformat(),
            }

            # Insert weather data into database
            with sqlite3.connect("pipeline.db") as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO weather_data (timestamp, temperature, feels_like, temperature_min, 
                    temperature_max, pressure, humidity, visibility, wind_speed, wind_deg, cloudiness, 
                    weather_description, weather_main, city_name, country_code, sunrise, sunset) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        weather_data["timestamp"],
                        weather_data["temperature"],
                        weather_data["feels_like"],
                        weather_data["temperature_min"],
                        weather_data["temperature_max"],
                        weather_data["pressure"],
                        weather_data["humidity"],
                        weather_data["visibility"],
                        weather_data["wind_speed"],
                        weather_data["wind_deg"],
                        weather_data["cloudiness"],
                        weather_data["weather_description"],
                        weather_data["weather_main"],
                        weather_data["city_name"],
                        weather_data["country_code"],
                        weather_data["sunrise"],
                        weather_data["sunset"],
                    ),
                )
                conn.commit()

            message_area.insert(
                tk.END, f"Weather data for {city} fetched successfully!\n"
            )
            message_area.yview(tk.END)
        else:
            print(f"Error fetching data for {city}: {response.status_code}")
    track_number_of_BatchFetch += 1
    message_area.insert(tk.END, f"Batch {track_number_of_BatchFetch} Fetch Done!\n")
    message_area.yview(tk.END)


def main():
    interval = input("Enter the interval in minutes (default is 1): ")
    interval = int(interval) if interval.isdigit() else 1
    schedule.every(interval).minutes.do(fetch_weather_data)
    print(f"Scheduler started. Fetching weather data every {interval} minute(s).")

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
