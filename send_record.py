import requests

partner_url = "https://maryjoydebaja.onrender.com/api/students"

record = {
    "student_id": "EXT-002",
    "name": "Sample Exchange Record",
    "program": "BSIT",
    "year": 1,
    "section": "A",
    "source": "Partner API"
}

try:
    response = requests.post(partner_url, json=record, timeout=60)
    print(response.status_code)
    print(response.text)
except requests.RequestException as e:
    print("Request failed:", e)