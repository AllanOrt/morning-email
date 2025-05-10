import requests
import json
import random
import smtplib

from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# === Configuration ===
# Replace this
LAT, LON = 0, 0
EMAIL = {
    "sender": "sender@example.com",
    "receiver": "receiver@example.com",
    "password": "password" # Or app password for gmail
}


FILES = {"quotes": "quotes.json", "schedule": "schedule.json", "lunch": "lunch.json"}

# === Helpers ===
def load_json(path): return json.load(open(path, encoding="utf-8"))
def comma(val): return str(round(val, 1)).replace('.', ',')

# === Load data ===
quotes = load_json(FILES["quotes"])
schedule = load_json(FILES["schedule"])
lunch = load_json(FILES["lunch"])

# === Date info ===
now = datetime.now()
weekday = now.strftime("%A").lower()
today = now.date().isoformat()
lunch_key = now.strftime("%b%d").lower()

# === Weather ===
weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&current_weather=true&hourly=temperature_2m,precipitation&timezone=auto"
weather = requests.get(weather_url).json()
hours = weather['hourly']['time']
temps = weather['hourly']['temperature_2m']
rains = weather['hourly']['precipitation']

temps_today = [t for t, h in zip(temps, hours) if h.startswith(today)]
rain_today = [(h, r) for h, r in zip(hours, rains) if today in h]
total_rain = sum(r for _, r in rain_today)
max_rain = max(rain_today, key=lambda x: x[1], default=(None, 0))
most_rain_time = datetime.fromisoformat(max_rain[0]).strftime("%H:%M") if max_rain[0] else ""

# === Quote ===
try:
    quote_data = requests.get("https://zenquotes.io/api/random").json()[0]
    extra_quote = f'<br><blockquote><em>“{quote_data["q"]}”</em><br>— {quote_data["a"]}</blockquote>'
except:
    extra_quote = ""

# === Sections ===
rain_section = f"""
    <br><li>Nederbörd idag: {comma(total_rain)} mm</li>
    <li>Mest nederbörd: kl {most_rain_time} ({comma(max_rain[1])} mm)</li>
""" if total_rain else ""

school_section = f"""
    <br><h3>🏫 Skola:</h3>
    <ul>{''.join(f"<li>{s}</li>" for s in schedule.get(weekday, []))}</ul>
""" if weekday in schedule else ""

lunch_section = f"""
    <br><h3>🍽 Lunch:</h3>
    <ul>{''.join(f"<li>{item}</li>" for item in lunch.get(lunch_key, []))}</ul>
""" if lunch_key in lunch else ""

# === HTML content ===
html = f"""
<html><body>
    <h3>⛅ Väder och temperatur:</h3>
    <ul>
        <li>Temperatur just nu: {comma(weather["current_weather"]["temperature"])}°C</li>
        <li>Kallast idag: {comma(min(temps_today))}°C</li>
        <li>Varmast idag: {comma(max(temps_today))}°C</li>
        {rain_section}
    </ul>

    <h3>💬 Dagliga citat:</h3>
    <blockquote><em>“{random.choice(quotes)}”</em><br>— Linus Torvald</blockquote>
    {extra_quote}
    {school_section}
    {lunch_section}
</body></html>
"""

# === Send email ===
msg = MIMEMultipart("alternative")
msg["From"] = EMAIL["sender"]
msg["To"] = EMAIL["receiver"]
msg["Subject"] = "God morgon!"
msg.attach(MIMEText(html, "html"))

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    server.login(EMAIL["sender"], EMAIL["password"])
    server.send_message(msg)