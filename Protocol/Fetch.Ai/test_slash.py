import requests

def test_slash_api(mac_address: str):
    url = "http://127.0.0.1:5000/request-slash"   # change to server IP if running remotely
    payload = {"mac_address": mac_address}
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print("Response JSON:", response.json())
    except Exception as e:
        print("Error while calling API:", e)


if __name__ == "__main__":
    # 🔧 Replace with any MAC address you want to test
    test_slash_api("00:1A:2B:3C:4D:5E")
