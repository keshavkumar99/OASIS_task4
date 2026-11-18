# SkyCast - Advanced Python Weather App

A Tkinter desktop weather dashboard using the OpenWeatherMap Current Weather and 5 Day / 3 Hour Forecast APIs.

## Features
- Search weather by city
- Current temperature and condition
- Feels-like temperature, humidity, wind speed and pressure
- Five-day forecast cards (one representative forecast per day)
- Weather icons loaded from OpenWeatherMap
- Metric and imperial unit selection
- Network calls run in a background thread so the GUI stays responsive
- API key stored in a local `.env` file

## Requirements
- Python 3.10+
- Internet connection
- OpenWeatherMap API key with access to Current Weather and 5 Day / 3 Hour Forecast endpoints

## Get an API key
1. Create an account at https://openweathermap.org/
2. Open your account's API keys section and create/copy a key.
3. API keys may take some time to become active after creation.

## Setup on Windows / VS Code
1. Extract the ZIP and open the folder in VS Code.
2. Open Terminal:

   ```powershell
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to a new file named `.env`.
4. Replace the placeholder with your key:

   ```env
   OPENWEATHER_API_KEY=your_real_api_key
   ```

5. Run the app:

   ```powershell
   python main.py
   ```

## Notes
- Choose `metric` for Celsius and metres/second, or `imperial` for Fahrenheit and miles/hour.
- The five-day forecast endpoint returns data in three-hour intervals. The app selects the forecast closest to midday for each displayed day; it is not a once-per-day official observation.
- Keep `.env` private and do not upload it to GitHub.
- API access, limits, and availability depend on your OpenWeatherMap account and subscription. See https://openweathermap.org/api.
