import requests
import time

time.sleep(10)
song_data = {
    "song_name": "Run Boy Run",
    "song_artist": "Woodkid",
    "bitrate": "=320"
}

response = requests.post(f"http://127.0.0.1:8000/download_song", json=song_data).json()

if response:
    print(response)
else:
    print(f"Failed to download the song. Error: {response.text}")