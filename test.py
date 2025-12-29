import os
import requests

API_KEY = os.getenv("GEMINI_API_KEY") or "AIzaSyDTX0HqYg7M3zDca4QWGQ9eWCDtjXEpeWk"
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={API_KEY}"
payload = {
    "contents": [{"parts": [{"text": "Say hello"}]}]
}
headers = {"Content-Type": "application/json"}

response = requests.post(url, headers=headers, json=payload)
print("Status code:", response.status_code)
print("Response:", response.text)