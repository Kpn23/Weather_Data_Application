import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker
import tkinter as tk
from tkinter import messagebox
import requests
import schedule
import time
from datetime import datetime
from dotenv import load_dotenv
import os


load_dotenv()
API_KEY = os.getenv("API_KEY")

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

conn = sqlite3.connect("weather_data.db")
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


def fetch_weather_data(message_area):
    message_area.config(state="normal")
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
            with sqlite3.connect("weather_data.db") as conn:
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

    message_area.insert(tk.END, f"Batch Fetch Done: {datetime.now()}\n")
    message_area.yview(tk.END)
    message_area.config(state="disabled")


class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Data Application")
        self.root.geometry("700x400")

        # Left column (buttons)
        self.fetch_button = tk.Button(
            root, text="Fetch Weather Data", command=self.fetch_data
        )
        self.fetch_button.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.extract_button = tk.Button(
            root, text="1. Extract Data", command=self.extract_data
        )
        self.extract_button.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.clean_button = tk.Button(
            root, text="2. Clean Data", command=self.clean_data
        )
        self.clean_button.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        self.visualize_button = tk.Button(
            root, text="3. Visualize Data", command=self.visualize_data
        )
        self.visualize_button.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        self.output_button = tk.Button(
            root, text="4. Output Report", command=self.output_report
        )
        self.output_button.grid(row=4, column=0, padx=10, pady=5, sticky="w")

        # Right column (labels and entries)
        self.schedule_label = tk.Label(root, text="Schedule Minutes:")
        self.schedule_label.grid(row=0, column=1, padx=10, pady=5, sticky="e")
        self.schedule_entry = tk.Entry(root)
        self.schedule_entry.grid(row=0, column=2, padx=10, pady=5, sticky="w")

        self.start_label = tk.Label(root, text="Start Timestamp (YYYY-MM-DD HH:MM):")
        self.start_label.grid(row=1, column=1, padx=10, pady=5, sticky="e")
        self.start_entry = tk.Entry(root)
        self.start_entry.grid(row=1, column=2, padx=10, pady=5, sticky="w")

        self.end_label = tk.Label(root, text="End Timestamp (YYYY-MM-DD HH:MM):")
        self.end_label.grid(row=2, column=1, padx=10, pady=5, sticky="e")
        self.end_entry = tk.Entry(root)
        self.end_entry.grid(row=2, column=2, padx=10, pady=5, sticky="w")

        # Time display area
        self.time_display_label = tk.Label(
            root,
            text="Current Start time & End time for \n\n 'Visualize Data' and 'Output Report'",
        )
        self.time_display_label.grid(
            row=3, column=1, rowspan=3, padx=10, pady=5, sticky="e"
        )
        self.time_display = tk.Text(root, height=6, width=25)
        self.time_display.grid(row=3, column=2, rowspan=3, padx=10, pady=10)
        self.time_display.config(state="disabled")

        # Message area spanning two columns
        self.message_area = tk.Text(root, height=10, width=90)
        self.message_area.grid(row=6, column=0, columnspan=3, padx=10, pady=10)
        self.message_area.config(state="disabled")

    # input and button execution
    def fetch_data(self):
        if not self.schedule_entry.get():
            messagebox.showwarning("Warning", "Schedule Minutes cannot be empty.")
        else:
            try:
                schedule_minutes = int(self.schedule_entry.get())
                schedule.every(schedule_minutes).minutes.do(
                    lambda: fetch_weather_data(self.message_area)
                )
                self.message_area.config(state="normal")
                self.message_area.insert(
                    tk.END,
                    f"Scheduler set to fetch data every {schedule_minutes} minutes.\n",
                )
                self.message_area.yview(tk.END)
                self.message_area.config(state="disabled")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred during fetching: {e}")

    def extract_data(self):
        try:
            self.message_area.config(state="normal")
            self.your_city, self.df = self.extract()
            self.message_area.insert(tk.END, "Data extracted successfully!\n")
            self.message_area.yview(tk.END)
            self.message_area.config(state="disabled")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during extraction: {e}")

    def clean_data(self):
        try:
            if hasattr(self, "df"):
                self.message_area.config(state="normal")
                self.df_c = self.clean(self.df)
                self.message_area.insert(tk.END, "Data cleaned successfully!\n")
                self.message_area.yview(tk.END)
                self.message_area.config(state="disabled")
            else:
                messagebox.showwarning("Warning", "Please extract data first.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during cleaning: {e}")

    def visualize_data(self):
        try:
            if hasattr(self, "df_c"):
                start_time_entry = self.start_entry.get()
                end_time_entry = self.end_entry.get()

                if not start_time_entry:
                    messagebox.showwarning("Warning", "Start time cannot be empty.")
                    return

                if not end_time_entry:
                    messagebox.showwarning("Warning", "End time cannot be empty.")
                    return

                try:
                    start_time = pd.Timestamp(start_time_entry)
                except ValueError:
                    messagebox.showerror(
                        "Error", "Start time is not a valid timestamp."
                    )
                    return

                try:
                    end_time = pd.Timestamp(end_time_entry)
                except ValueError:
                    messagebox.showerror("Error", "End time is not a valid timestamp.")
                    return

                self.df_c_t = self.df_c[
                    (self.df_c["timestamp"] >= start_time)
                    & (self.df_c["timestamp"] <= end_time)
                ]

                your_city = self.df_c["city_name"].unique()
                self.start_time = start_time
                self.end_time = end_time
                count_data = len(self.df_c_t["timestamp"])
                self.visualize(your_city, self.df_c_t)
                self.time_display.config(state="normal")
                self.time_display.delete("1.0", tk.END)
                self.message_area.config(state="normal")
                self.message_area.insert(tk.END, "Data visualized successfully!\n")
                self.message_area.yview(tk.END)
                self.time_display.insert(tk.END, f"{start_time}\n\n")
                self.message_area.yview(tk.END)
                self.time_display.insert(tk.END, f"{end_time}\n\n")
                self.message_area.yview(tk.END)
                self.time_display.insert(
                    tk.END, f"record found for 8 cities: {count_data}"
                )
                self.message_area.yview(tk.END)
                self.message_area.config(state="disabled")
                self.time_display.config(state="disabled")
            else:
                messagebox.showwarning("Warning", "Please extract and then clean data.")
        except Exception as e:
            messagebox.showerror(
                "Error", f"An error occurred during visualization: {e}"
            )

    def output_report(self):
        try:
            if hasattr(self, "df_c_t"):
                self.message_area.config(state="normal")
                self.output(self.df_c_t, self.start_time, self.end_time)
                self.message_area.insert(tk.END, "Report output successfully!\n")
                self.message_area.yview(tk.END)
                self.message_area.config(state="disabled")
            else:
                messagebox.showwarning("Warning", "Please visualize data first.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during output: {e}")

    # ETL , visualisation , export csv
    def extract(self):
        conn = sqlite3.connect("weather_data.db")
        your_city = pd.read_sql("SELECT DISTINCT city_name FROM weather_data", conn)[
            "city_name"
        ].tolist()
        df = pd.read_sql("SELECT * FROM weather_data", conn)
        conn.close()
        return your_city, df

    def clean(self, df):
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df.dropna(inplace=True)
        df_c = df
        return df_c

    def visualize(self, your_city, df_c_t):
        # start_time = pd.Timestamp("2024-08-27 09:00")
        # end_time = pd.Timestamp("2024-08-27 17:00")
        index = range(len(your_city))

        fig, axs = plt.subplots(4, 2, figsize=(20, 30))
        for city, i in zip(your_city, index):
            city_data = df_c_t[df_c_t["city_name"] == city]
            if not city_data.empty:
                ax = axs[i // 2, i % 2]
                ax.plot(
                    city_data["timestamp"],
                    city_data["temperature"],
                    label="Temperature",
                    color="blue",
                )
                ax.plot(
                    city_data["timestamp"],
                    city_data["temperature_max"],
                    label="Max Temperature",
                    color="red",
                )
                ax.plot(
                    city_data["timestamp"],
                    city_data["temperature_min"],
                    label="Min Temperature",
                    color="green",
                )
                ax.fill_between(
                    city_data["timestamp"],
                    city_data["temperature_max"],
                    city_data["temperature_min"],
                    color="lightgray",
                    alpha=0.5,
                    label="Temperature Range",
                )
                # ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=5))
                ax.set_title(f"Temperature Over Time for {city}")
                ax.set_xlabel("Time")
                ax.set_ylabel("Temperature (°C)")
                ax.legend()

        plt.tight_layout()
        plt.savefig("png_folder/temperature_over_time.png")

        plt.close()

        fig, axs = plt.subplots(4, 2, figsize=(20, 35))

        for city, i in zip(your_city, index):
            city_data = df_c_t[df_c_t["city_name"] == city]
            if not city_data.empty:
                ax = axs[i // 2, i % 2]
                correlation_matrix = city_data[
                    ["temperature", "feels_like", "humidity"]
                ].corr()
                sns.heatmap(
                    correlation_matrix,
                    annot=True,
                    cmap="coolwarm",
                    fmt=".2f",
                    square=True,
                    ax=ax,
                )
                ax.set_title(f"Heatmap for {city}")

        plt.suptitle("Heatmap of Temperature, Feels Like, and Humidity", y=0.99)
        plt.tight_layout()
        plt.savefig("png_folder/correlation_heatmap.png")
        plt.close()

        return df_c_t

    def output(self, df_c_t, start_time, end_time):
        df_c_t_t = df_c_t.groupby(["city_name"])[["temperature", "feels_like"]].mean()
        data_to_save = []

        for index, row in df_c_t_t.iterrows():
            diff = row["feels_like"] - row["temperature"]
            avg_temp = row["temperature"]
            data_to_save.append(
                {
                    "City": index,
                    "Avg Temp": f"{avg_temp:.2f}",
                    "Difference": f"{diff:.2f}",
                    "Remark": "(+) feel hotter" if diff > 0 else "(-) feel cooler",
                    "Start Time": start_time,
                    "End Time": end_time,
                }
            )

        df_to_csv = pd.DataFrame(data_to_save)
        df_to_csv.to_csv("weather_report.csv", index=False)


def run_scheduler():
    schedule.run_pending()
    root.after(1000, run_scheduler)


if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    run_scheduler()
    root.mainloop()
