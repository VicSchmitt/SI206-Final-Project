import requests
import json
import unittest
import os


def get_api_key(filename):
    try:
        with open(filename, 'r') as f:
            key = f.read().strip()
        return key
    except Exception:
        return ""


if os.path.exists("api_key.txt"):
    API_KEY = get_api_key("api_key.txt")
else:
    API_KEY = "5ccb08a7"


def build_url(movie):
    return f"http://www.omdbapi.com/?apikey={API_KEY}&t={movie.replace(' ', '+')}"

open_api_key = "3c4d479363893dd3a68aa9d11f95be22"
param3 = "units=Metric"
zipcode = "48103"
base = "https://api.openweathermap.org/data/2.5/weather"
param1 = f"appid={open_api_key}"
param2 = f"zip={zipcode}"
request = f"{base}?{param1}&{param2}&{param3}"

print(request)
page = requests.get(request)
print(page.status_code) #to check if the request is successful
weather  = page.json()    #turn the information into a json object
print(json.dumps(weather, indent = 2))
