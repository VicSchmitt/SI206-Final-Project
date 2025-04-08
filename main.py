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
