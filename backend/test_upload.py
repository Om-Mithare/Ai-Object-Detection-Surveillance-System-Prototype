import requests

try:
    with open("requirements.txt", "rb") as f:
        files = {"file": ("requirements.txt", f, "text/plain")}
        response = requests.post("http://127.0.0.1:8000/api/upload", files=files)
        print("Status Code:", response.status_code)
        print("Response Text:", response.text)
except Exception as e:
    print("Request failed:", e)
