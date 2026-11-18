import os
import threading
from datetime import datetime
from io import BytesIO
import tkinter as tk
from tkinter import ttk, messagebox

import requests
from dotenv import load_dotenv
from PIL import Image, ImageTk

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY", "").strip()
BASE_URL = "https://api.openweathermap.org/data/2.5"
ICON_URL = "https://openweathermap.org/img/wn/{}@2x.png"


class WeatherApp:
    BG = "#101827"
    PANEL = "#1b2940"
    PANEL2 = "#243650"
    TEXT = "#edf4ff"
    MUTED = "#a7b7cc"
    ACCENT = "#70d6f5"

    def __init__(self, root):
        self.root = root
        self.root.title("SkyCast | Weather Dashboard")
        self.root.geometry("900x720")
        self.root.minsize(760, 650)
        self.root.configure(bg=self.BG)
        self.icon_refs = []

        self.city_var = tk.StringVar(value="Delhi")
        self.status_var = tk.StringVar(value="Enter a city and select Search.")
        self.unit_var = tk.StringVar(value="metric")

        self._style()
        self._build_ui()

    def _style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=9)
        style.configure("TEntry", padding=9)
        style.configure("TCombobox", padding=7)

    def _build_ui(self):
        header = tk.Frame(self.root, bg=self.BG)
        header.pack(fill="x", padx=25, pady=(22, 12))
        tk.Label(header, text="SKYCAST", bg=self.BG, fg=self.ACCENT,
                 font=("Segoe UI", 27, "bold")).pack(anchor="w")
        tk.Label(header, text="LIVE WEATHER • CITY FORECAST DASHBOARD",
                 bg=self.BG, fg=self.MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")

        search = tk.Frame(self.root, bg=self.PANEL, padx=15, pady=13)
        search.pack(fill="x", padx=25, pady=8)
        tk.Label(search, text="Location", bg=self.PANEL, fg=self.TEXT,
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 10))
        self.city_entry = ttk.Entry(search, textvariable=self.city_var, font=("Segoe UI", 11))
        self.city_entry.pack(side="left", fill="x", expand=True, padx=(0, 9))
        self.city_entry.bind("<Return>", lambda event: self.search_weather())
        self.unit_box = ttk.Combobox(search, textvariable=self.unit_var,
                                     values=("metric", "imperial"), state="readonly", width=10)
        self.unit_box.pack(side="left", padx=(0, 9))
        self.unit_box.bind("<<ComboboxSelected>>", lambda event: self.search_weather())
        ttk.Button(search, text="Search", command=self.search_weather).pack(side="left")

        self.status = tk.Label(self.root, textvariable=self.status_var,
                               bg=self.BG, fg=self.MUTED,
                               font=("Segoe UI", 9), anchor="w")
        self.status.pack(fill="x", padx=28, pady=(4, 7))

        self.main_card = tk.Frame(self.root, bg=self.PANEL, padx=22, pady=18)
        self.main_card.pack(fill="x", padx=25, pady=8)

        top = tk.Frame(self.main_card, bg=self.PANEL)
        top.pack(fill="x")
        self.location_label = tk.Label(top, text="Search for a city",
                                       bg=self.PANEL, fg=self.TEXT,
                                       font=("Segoe UI", 18, "bold"))
        self.location_label.pack(side="left", anchor="w")
        self.updated_label = tk.Label(top, text="", bg=self.PANEL, fg=self.MUTED,
                                      font=("Segoe UI", 9))
        self.updated_label.pack(side="right", anchor="e")

        current = tk.Frame(self.main_card, bg=self.PANEL)
        current.pack(fill="x", pady=(12, 5))
        self.icon_label = tk.Label(current, text="🌤", bg=self.PANEL,
                                   fg=self.TEXT, font=("Segoe UI Emoji", 48))
        self.icon_label.pack(side="left", padx=(0, 18))
        info = tk.Frame(current, bg=self.PANEL)
        info.pack(side="left", fill="x", expand=True)
        self.temp_label = tk.Label(info, text="--°", bg=self.PANEL, fg=self.TEXT,
                                   font=("Segoe UI", 39, "bold"))
        self.temp_label.pack(anchor="w")
        self.description_label = tk.Label(info, text="Current conditions will appear here",
                                           bg=self.PANEL, fg=self.MUTED,
                                           font=("Segoe UI", 12))
        self.description_label.pack(anchor="w")

        metrics = tk.Frame(self.main_card, bg=self.PANEL)
        metrics.pack(fill="x", pady=(14, 0))
        self.metric_labels = {}
        for title, key in [
            ("FEELS LIKE", "feels"), ("HUMIDITY", "humidity"),
            ("WIND", "wind"), ("PRESSURE", "pressure")
        ]:
            tile = tk.Frame(metrics, bg=self.PANEL2, padx=12, pady=11)
            tile.pack(side="left", fill="both", expand=True, padx=4)
            tk.Label(tile, text=title, bg=self.PANEL2, fg=self.MUTED,
                     font=("Segoe UI", 8, "bold")).pack(anchor="w")
            value = tk.Label(tile, text="--", bg=self.PANEL2, fg=self.TEXT,
                             font=("Segoe UI", 14, "bold"))
            value.pack(anchor="w", pady=(4, 0))
            self.metric_labels[key] = value

        forecast_header = tk.Frame(self.root, bg=self.BG)
        forecast_header.pack(fill="x", padx=25, pady=(17, 8))
        tk.Label(forecast_header, text="5-DAY FORECAST",
                 bg=self.BG, fg=self.TEXT,
                 font=("Segoe UI", 13, "bold")).pack(side="left")
        tk.Label(forecast_header, text="Daily outlook",
                 bg=self.BG, fg=self.MUTED,
                 font=("Segoe UI", 9)).pack(side="right")

        self.forecast_frame = tk.Frame(self.root, bg=self.BG)
        self.forecast_frame.pack(fill="both", expand=True, padx=21, pady=(0, 10))
        self.forecast_cards = []

        footer = tk.Label(self.root,
            text="Weather data provided by OpenWeatherMap • Units: °C / km/h or °F / mph",
            bg=self.BG, fg=self.MUTED, font=("Segoe UI", 8))
        footer.pack(fill="x", padx=25, pady=(3, 13))

    def search_weather(self):
        city = self.city_var.get().strip()
        if not city:
            messagebox.showwarning("Missing location", "Please enter a city name.")
            return
        if not API_KEY:
            messagebox.showerror(
                "API key required",
                "Add your OpenWeatherMap API key to the .env file.\n\n"
                "Copy .env.example to .env and set OPENWEATHER_API_KEY."
            )
            return

        self.status_var.set(f"Fetching weather for {city}...")
        threading.Thread(target=self._fetch_weather, args=(city, self.unit_var.get()),
                         daemon=True).start()

    def _fetch_weather(self, city, units):
        try:
            params = {"q": city, "appid": API_KEY, "units": units}
            current_response = requests.get(f"{BASE_URL}/weather", params=params, timeout=12)
            self._raise_api_error(current_response)
            current = current_response.json()

            forecast_response = requests.get(f"{BASE_URL}/forecast", params=params, timeout=12)
            self._raise_api_error(forecast_response)
            forecast = forecast_response.json()

            self.root.after(0, lambda: self._show_weather(current, forecast, units))
        except requests.RequestException as exc:
            message = str(exc)
            self.root.after(0, lambda: self._show_error(message))
        except (KeyError, TypeError, ValueError) as exc:
            message = f"Unexpected weather data: {exc}"
            self.root.after(0, lambda: self._show_error(message))

    @staticmethod
    def _raise_api_error(response):
        if response.ok:
            return
        try:
            detail = response.json().get("message", response.reason)
        except ValueError:
            detail = response.reason
        if response.status_code == 401:
            detail = "API key is invalid or not active yet. Check your key and try again later."
        elif response.status_code == 404:
            detail = "City not found. Try a city name with its country code, e.g. London,GB."
        elif response.status_code == 429:
            detail = "API request limit reached. Please wait before trying again."
        raise requests.HTTPError(detail, response=response)

    def _show_error(self, message):
        self.status_var.set("Could not retrieve weather.")
        messagebox.showerror("Weather API error", message)

    def _show_weather(self, current, forecast, units):
        city_name = current.get("name", self.city_var.get())
        country = current.get("sys", {}).get("country", "")
        unit_symbol = "°C" if units == "metric" else "°F"
        wind_unit = "m/s" if units == "metric" else "mph"

        self.location_label.config(text=f"{city_name}, {country}")
        self.updated_label.config(text="Updated " + datetime.now().strftime("%I:%M %p"))
        self.temp_label.config(text=f"{round(current['main']['temp'])}{unit_symbol}")
        weather = current["weather"][0]
        self.description_label.config(text=weather["description"].capitalize())
        self.metric_labels["feels"].config(
            text=f"{round(current['main']['feels_like'])}{unit_symbol}")
        self.metric_labels["humidity"].config(text=f"{current['main']['humidity']}%")
        self.metric_labels["wind"].config(text=f"{current['wind']['speed']} {wind_unit}")
        self.metric_labels["pressure"].config(text=f"{current['main']['pressure']} hPa")

        self._load_icon(weather.get("icon", "01d"), self.icon_label)
        self._show_forecast(forecast, units)
        self.status_var.set("Weather loaded successfully.")

    def _load_icon(self, icon_code, target_label):
        def worker():
            try:
                response = requests.get(ICON_URL.format(icon_code), timeout=10)
                response.raise_for_status()
                image = Image.open(BytesIO(response.content)).convert("RGBA")
                image = image.resize((100, 100), Image.Resampling.LANCZOS)
                # Create Tk image objects on the GUI thread.
                self.root.after(0, lambda: self._set_icon(target_label, image))
            except Exception:
                self.root.after(0, lambda: target_label.config(text="🌤"))
        threading.Thread(target=worker, daemon=True).start()

    def _set_icon(self, label, image):
        photo = ImageTk.PhotoImage(image)
        label.config(image=photo, text="")
        label.image = photo
        self.icon_refs.append(photo)

    def _show_forecast(self, forecast, units):
        for widget in self.forecast_frame.winfo_children():
            widget.destroy()
        self.forecast_cards.clear()

        daily = {}
        for item in forecast.get("list", []):
            date_key = item["dt_txt"].split(" ")[0]
            # Prefer the forecast closest to midday for a representative daily card.
            hour = int(item["dt_txt"].split(" ")[1][:2])
            if date_key not in daily or abs(hour - 12) < abs(daily[date_key]["hour"] - 12):
                daily[date_key] = {"item": item, "hour": hour}

        unit_symbol = "°C" if units == "metric" else "°F"
        for date_key, entry in list(daily.items())[:5]:
            item = entry["item"]
            day_name = datetime.strptime(date_key, "%Y-%m-%d").strftime("%a")
            temp = round(item["main"]["temp"])
            description = item["weather"][0]["description"].capitalize()
            card = tk.Frame(self.forecast_frame, bg=self.PANEL, padx=9, pady=12)
            card.pack(side="left", fill="both", expand=True, padx=4, pady=3)
            tk.Label(card, text=day_name, bg=self.PANEL, fg=self.MUTED,
                     font=("Segoe UI", 10, "bold")).pack()
            icon = tk.Label(card, text="🌤", bg=self.PANEL, fg=self.TEXT,
                            font=("Segoe UI Emoji", 25))
            icon.pack(pady=4)
            self._load_icon(item["weather"][0].get("icon", "01d"), icon)
            tk.Label(card, text=f"{temp}{unit_symbol}", bg=self.PANEL, fg=self.TEXT,
                     font=("Segoe UI", 16, "bold")).pack()
            tk.Label(card, text=description, bg=self.PANEL, fg=self.MUTED,
                     font=("Segoe UI", 8), wraplength=105).pack(pady=(4, 0))

    def close(self):
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()
