import requests
import json
import random
from datetime import datetime

# Constants
LATITUDE = 0 # Set latitude here
LONGITUDE = 0 # Set longitude here
QUOTE_FILE = 'quotes.json'
SCHEDULE_FILE = 'schedule.json'
LUNCH_FILE = 'lunch.json'

# Load data
def load_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

quotes = load_json(QUOTE_FILE)
schedule = load_json(SCHEDULE_FILE)
lunch_list = load_json(LUNCH_FILE)

# Date and weekday
now = datetime.now()
weekday, today = now.strftime("%A").lower(), now.date().isoformat()
lunch_date = now.strftime("%b%d").lower()

# Weather
url = f"https://api.open-meteo.com/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&current_weather=true&hourly=temperature_2m,precipitation&timezone=auto"
weather = requests.get(url).json()

# Filter today's hours
hours, temps, rain = weather['hourly']['time'], weather['hourly']['temperature_2m'], weather['hourly']['precipitation']
rain_today = [(t, r) for t, r in zip(hours, rain) if today in t]
temps_today = [t for t, time in zip(temps, hours) if time.startswith(today)]

# Rain stats
total_rain = sum(r for _, r in rain_today)
max_rain = max(rain_today, key=lambda x: x[1], default=(None, 0))
most_rain_time = datetime.fromisoformat(max_rain[0]).strftime("%H:%M") if max_rain[0] else None

# Formatting
def use_comma(value):
    return str(round(value, 1)).replace('.', ',')

# Get random quote
quote_data = requests.get("https://zenquotes.io/api/random").json()[0] if requests.get("https://zenquotes.io/api/random").status_code == 200 else {}
quote, author = quote_data.get("q", ""), quote_data.get("a", "")

# Output
print("God morgon!")

print()
print("⛅ Väder och temperatur:")
print(f"    Temperatur just nu: {use_comma(weather['current_weather']['temperature'])}°C")
print(f"    Kallast idag: {use_comma(min(temps_today))}°C")
print(f"    Varmast idag: {use_comma(max(temps_today))}°C")

if total_rain > 0:
    print(f"\n    Nederbörd idag: {use_comma(total_rain)} mm")
    print(f"    Mest nederbörd: kl {most_rain_time} ({use_comma(max_rain[1])} mm).")

print("\n💬 Dagliga citat:")
print(f"    “{random.choice(quotes)}”")
print("    — Linus Torvald")
if quote and author:
    print(f"\n    ”{quote}”\n    — {author}")

print("\n🏫 Skola:")
for subject in schedule.get(weekday, []):
    print(f"    {subject}")

if lunch_date in lunch_list:
    for lunch in lunch_list[lunch_date]:
        print(f"\n    Lunch: {lunch}")