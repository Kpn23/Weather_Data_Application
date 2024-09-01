# Overview
The Weather Data Application is a Python-based tool designed to fetch, analyze, and visualize real-time weather data from various cities around the world. This application leverages the OpenWeatherMap API to gather weather information and provides a user-friendly interface for data extraction, cleaning, visualization, and reporting.
# Features
Fetch real-time weather data for multiple cities.
Store weather data in a SQLite database.
Extract, clean, and visualize data using various Python libraries.
Generate reports based on analyzed weather data.
# Technologies Used
Python: The primary programming language.
Tkinter: For creating the GUI.
SQLite: For database management.
Pandas: For data manipulation and analysis.
Matplotlib and Seaborn: For data visualization.
Requests: For making HTTP requests to the weather API.
Schedule: For scheduling periodic data fetching.
# Installation
1. Clone the repository:
```bash
git clone <repository-url>
cd weather-data-application
```
2. Install required packages:
```bash
pip install -r requirements.txt
```
3. Set up environment variables:
Create a .env file in the root directory and add your OpenWeatherMap API key:
```
API_KEY=your_api_key_here
```
# Usage
1. Run the application:
```bash
python main.py
```
2. Fetch Weather Data: Click the "Fetch Weather Data" button to retrieve the latest weather data for the specified cities.
3. Extract Data: Use the "Extract Data" button to pull data from the SQLite database.
4. Clean Data: Click the "Clean Data" button to preprocess the extracted data.
5. Visualize Data: Use the "Visualize Data" button to generate visual representations of the weather data.
6. Output Report: Click the "Output Report" button to generate a CSV report of the weather data analysis.
# Project Structure
```
weather-data-application/
│
├── main.py                # Main application file
├── weather_data.db       # SQLite database file
├── requirements.txt      # Python dependencies
└── .env                  # Environment variables
```