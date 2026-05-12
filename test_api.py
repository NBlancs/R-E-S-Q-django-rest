import requests

# Replace with your actual token
token = "YOUR_TOKEN_HERE"
headers = {"Authorization": f"Token {token}"}

# Test profile endpoint
response = requests.get("http://127.0.0.1:8000/api/auth/profile/", headers=headers)
print("Status Code:", response.status_code)
print("Response:", response.json())
