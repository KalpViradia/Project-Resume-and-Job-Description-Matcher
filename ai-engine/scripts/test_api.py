import requests
import json

url = "http://127.0.0.1:8000/match"
payload = {
    "resume_text": "Experienced software engineer with Python and React skills.",
    "jd_text": "Looking for a software engineer proficient in Python and React."
}
headers = {'Content-Type': 'application/json'}

try:
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
