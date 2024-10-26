# -*- coding: utf-8 -*-
"""
Created on Mon Oct 21 16:22:50 2024

@author: pawe2
"""

import requests
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import StringVar

def load_API_key(filepath):
    try:
        with open(filepath, 'r') as file:
            return file.readline().strip()
    except Exception as ex:
        print(f"API KEY is not available: {ex}")
        return None

def fetch_weather_data(city_name, API_KEY, units):
    try:
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}&units={units}"
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city_name}&appid={API_KEY}&units={units}"
       
        weather_response = requests.get(weather_url, timeout=10)
        forecast_response = requests.get(forecast_url, timeout=10)

        weather_response.raise_for_status()
       
        forecast_response.raise_for_status()
        return weather_response.json(), forecast_response.json()
    except requests.exceptions.Timeout:
        messagebox.showerror("Network Error", "Request timed out. Please check your internet connection.")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
    return None, None

def get_weather_icon(weather_description):
    icons = {
        "clear sky": "sunny.png",
        "few clouds": "cloudy.png",
        "scattered clouds": "cloudy.png",
        "broken clouds": "cloudy.png",
        "overcast clouds": "cloudy.png",
        "shower rain": "rainy.png",
        "rain": "rainy.png",
        "thunderstorm": "storm.png",
        "snow": "snowy.png",
        "fog": "mist.png"}
    return icons.get(weather_description, "default.png")

def load_icon(weather_icon):
    try:
        icon = Image.open(f"icons/{weather_icon}").resize((150, 150), Image.LANCZOS)
        icon_image = ImageTk.PhotoImage(icon)
        icon_label.config(image=icon_image)
        icon_label.image = icon_image
    except FileNotFoundError:
        print(f"Icon file not found: icons/{weather_icon}")
        icon_label.config(image='')

def plot_forecast(forecast_dates, forecast_temps):
    fig, ax = plt.subplots(figsize=(8, 4), dpi=60)
    ax.plot(forecast_dates, forecast_temps, marker='o', color='b')
    ax.fill_between(forecast_dates, forecast_temps, color='blue', alpha=0.1)
    ax.set_title("5-Day Temperature Forecast")
    ax.set_xlabel("Date")
    ax.set_ylabel("Temperature (°C)")
    ax.grid(True)

    fig.autofmt_xdate()

    for widget in plot_frame.winfo_children():
        widget.destroy()

    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

def display_weather():
    city_name = text_field.get().strip()
    if not city_name:
        messagebox.showerror("Input Error", "Please enter a city name.")
        return
    units = current_unit.get()
    weather_data, weather_forecast = fetch_weather_data(city_name, API_KEY, units)

    listbox.delete(0, tk.END)
    if weather_data:
        weather_description = weather_data['weather'][0]['description']     
        load_icon(get_weather_icon(weather_description))
        weather_info = [
            f"City: {city_name}",
            f"Description: {weather_description}",
            f"Temperature: {weather_data['main']['temp']}°",
            f"Pressure: {weather_data['main']['pressure']} hPa",
            f"Humidity: {weather_data['main']['humidity']}%",
            f"Wind Speed: {weather_data['wind']['speed']} m/s",
            f"Visibility: {weather_data['visibility']} m",
            f"Cloudiness: {weather_data['clouds']['all']}%",
            f"Sunrise: {format_time(weather_data['sys']['sunrise'])}",
            f"Sunset: {format_time(weather_data['sys']['sunset'])}",
            f"Date & Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ]
        for info in weather_info:
            listbox.insert(tk.END, info)

        if weather_forecast:
            listbox.insert(tk.END, "5-Day Forecast:")
            forecast_dates = []
            forecast_temps = []
            for item in weather_forecast['list'][::8]:  
                date_str = item['dt_txt'].split(' ')[0]  
                forecast_dates.append(date_str)
                forecast_temps.append(item['main']['temp'])
                forecast_desc = item['weather'][0]['description']
                forecast_info = f"{date_str}: {item['main']['temp']}°, {forecast_desc}"
                listbox.insert(tk.END, forecast_info)
            plot_forecast(forecast_dates, forecast_temps)  # Pass the correct variables
    else:
        messagebox.showerror("Data Error", "Could not retrieve weather data. Please check the city name and try again.")


def format_time(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')

     
def toggle_theme():
    if current_theme.get() == "light":
        current_theme.set("dark")
        style.configure("Custom.TFrame", background="#444444")
        style.configure("Custom.TLabel", background="#444444", foreground="#ffffff")
        style.configure("Custom.TEntry", fieldbackground="#555555", foreground="#ffffff")
        style.configure("Custom.TButton", background="#666666", foreground="#ffffff")
        style.configure("Small.TButton", background="#666666", foreground="#ffffff")
        style.configure("TCombobox", fieldbackground="#555555", foreground="#ffffff", background="#666666")
        window.configure(bg="#333333")
        listbox.config(bg="#555555", fg="#ffffff")
        plot_frame.config(bg="#444444")
        
    else:
        current_theme.set("light")
        style.configure("Custom.TFrame", background="#e0f7fa")
        style.configure("Custom.TLabel", background="#e0f7fa", foreground="#333333")
        style.configure("Custom.TEntry", fieldbackground="#ffffff", foreground="#333333")
        style.configure("Custom.TButton", background="#4fc3f7", foreground="#333333")
        style.configure("Small.TButton", background="#4fc3f7", foreground="#333333")
        style.configure("TCombobox", fieldbackground="#ffffff", foreground="#333333", background="#ffffff")
        window.configure(bg="#e0f7fa")
        listbox.config(bg="#ffffff", fg="#333333")
        plot_frame.config(bg="#e0f7fa")
       
def convert_temperature(temp, to_unit):
    if to_unit == 'imperial':
        return (temp * 9/5) + 32
    else:
        return (temp - 32) * 5/9

def convert_units():
    current_temp = float(listbox.get(2).split(": ")[1][:-1])  
    if current_unit.get() == 'metric':
        converted_temp = convert_temperature(current_temp, 'imperial')
        current_unit.set('imperial')
    else:
        converted_temp = convert_temperature(current_temp, 'metric')
        current_unit.set('metric')
    listbox.delete(2)
    listbox.insert(2, f"Temperature: {round(converted_temp, 2)}°")
    
def get_current_location():
    try:
        response = requests.get('https://ipinfo.io')
        response.raise_for_status()
        location_data = response.json()
        
        city_name = location_data.get('city')
        
        if city_name:  
            confirm = messagebox.askyesno(
                "Location Confirmation",
                f"Detected location: {city_name}. Do you want to use this city for weather data?"
            )
            if confirm:
                return city_name  
        else:
            messagebox.showerror("Error", "City not found in location data.")

    except requests.RequestException:
        messagebox.showerror("Network Error", "Could not retrieve current location. Please check your internet connection.")
    
    return None  

def use_current_location():
    city_name = get_current_location()
    if city_name:
        text_field.delete(0, tk.END) 
        text_field.insert(0, city_name)
        display_weather()
    
    
API_KEY = load_API_key(r"C:\Users\pawe2\OneDrive\Pulpit\apikey.txt")

window = tk.Tk()
window.title("Weather Forecast")
window.geometry("800x800")

style = ttk.Style()
style.theme_use("clam")
style.configure("Custom.TLabel", font=("Segoe UI", 14, "bold"), background="#e0f7fa", foreground="#333333")
style.configure("Custom.TEntry", font=("Segoe UI", 12))
style.configure("Custom.TButton", font=("Segoe UI", 12, "bold"), padding=10, background="#4fc3f7")
style.configure("Custom.TFrame", background="#e0f7fa")
style.configure("Small.TButton", font=("Segoe UI", 8))

current_unit = StringVar(value="metric") 
current_theme = StringVar(value="light")

frame = ttk.Frame(window, padding="20 20 20 20", style="Custom.TFrame")
frame.pack(fill=tk.BOTH, expand=True)

input_frame = ttk.Frame(frame, style="Custom.TFrame")
input_frame.pack(pady=20, anchor='center')

ttk.Label(input_frame, text="Provide City Name:", style="Custom.TLabel").grid(row=0, column=0, padx=10, pady=10)
text_field = ttk.Entry(input_frame, width=20, style="Custom.TEntry")
text_field.grid(row=0, column=1, padx=10, pady=10)

unit_combobox = ttk.Combobox(input_frame, textvariable=current_unit, values=["metric", "imperial"], state="readonly")
unit_combobox.grid(row=0, column=2, padx=10, pady=10)
unit_combobox.current(0)  

use_location_button = ttk.Button(input_frame, text="Use My Location", command=use_current_location, style="Small.TButton")
use_location_button.grid(row=1, column=1, padx=10, pady=10)

unit_toggle_button = ttk.Button(input_frame, text='Convert Units', command=convert_units, style="Small.TButton")
unit_toggle_button.grid(row=1, column=2, padx=10, pady=10)

toggle_theme_button = ttk.Button(input_frame, text='Toggle Theme', command=toggle_theme, style="Small.TButton")
toggle_theme_button.grid(row=1, column=0, padx=10, pady=10)

ttk.Button(frame, text='Get Weather', command=display_weather, style="Custom.TButton").pack(pady=20)

icon_label = tk.Label(frame, bg="#e0f7fa")
icon_label.place(relx=1.0, rely=0.0, anchor='ne')  

listbox = tk.Listbox(frame, width=80, height=15, font=("Segoe UI", 10), bg="#ffffff", fg="#333333")
listbox.pack(pady=20)

plot_frame = tk.Frame(frame, bg="#e0f7fa")
plot_frame.pack(fill=tk.BOTH, expand=True)

window.mainloop()

