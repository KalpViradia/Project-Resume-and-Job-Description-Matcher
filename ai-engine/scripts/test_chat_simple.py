import requests
import time
import sys

def test_chat():
    url = "http://localhost:8000/chat"
    
    # Wait for server
    print("Waiting for server...")
    for _ in range(10):
        try:
            requests.get("http://localhost:8000/")
            break
        except:
            time.sleep(1)
    
    payload = {
        "message": "Hello, I need python help.",
        "history": [],
        "context": "User is a developer."
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        if response.status_code == 200:
            print("SUCCESS")
        else:
            print("FAILURE")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_chat()
