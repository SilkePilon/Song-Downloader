import threading
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
import uvicorn
import pyautogui
import time
import random
import os
import signal
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from rich.console import Console
import json
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
import urllib.parse
from fastapi.middleware.cors import CORSMiddleware
import re
from fastapi import Query
import shutil
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

console = Console()
app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
CLIENT_ID = '2865c34cc5894effa89442ee5aed02f0'
CLIENT_SECRET = "f4f17593c827405d84d39b8c3ce0ab67"
CLIENT_CREDENTIALS_MANAGER = SpotifyClientCredentials(
    client_id=CLIENT_ID, client_secret=CLIENT_SECRET
)
SP = spotipy.Spotify(client_credentials_manager=CLIENT_CREDENTIALS_MANAGER)
is_window_focused = False

global queue
queue = False


# Define the request models


class DownloadSongRequest(BaseModel):
    song_name: str
    song_artist: str
    bitrate: str = "=320"


class DownloadPlaylistRequest(BaseModel):
    playlist_link: str
    auto_download: bool = True
    random_user_download: bool = False
    use_text_filter: bool = False
    allow_remix: bool = False
    use_country_filter: bool = False
    country: str = 'NL,US'
    download: bool = True
    wait_time: int = 60


def window_checker():
    global is_window_focused
    while True:
        time.sleep(0.5)
        active_window = os.popen('xdotool getwindowfocus getwindowname').read()
        is_window_focused = "Nicotine" in active_window


def get_playlist_uri(playlist_link):
    return playlist_link.split("/")[-1].split("?")[0]


def get_tracks(link):
    tracks = []
    playlist_uri = get_playlist_uri(link)
    for track in SP.playlist_tracks(playlist_uri)["items"]:
        track_uri = track["track"]["uri"]
        track_name = track["track"]["name"]
        track_artists = track["track"]["artists"]
        result = track_name, track_artists, SP.audio_features(track_uri)
        tracks.append(result)

    return tracks


print("Please make sure you have Nicotine running in the background and the window is focused.")

print("Waiting for Nicotine to be focused...")
is_window_focused = False
while not is_window_focused:
    time.sleep(1)
    active_window = os.popen('xdotool getwindowfocus getwindowname').read()
    is_window_focused = "Nicotine" in active_window

window_checker_thread = threading.Thread(
    target=window_checker, name="Window Checker", daemon=True)
window_checker_thread.start()

print("Nicotine is focused. Starting download...")

app.mount("/download", StaticFiles(directory="download_ready",
          html=True), name="Downloads")

def ms_to_minutes_seconds(ms):
    minutes = ms // (1000 * 60)
    seconds = (ms % (1000 * 60)) // 1000
    return f"{int(minutes):02d}:{int(seconds):02d}"

@app.get("/search")
async def search(query: str = Query(...)):
    if query == "":
        raise HTTPException(
            status_code=400, detail="Query cannot be empty.")
    else:
        search_results = SP.search(q=query, limit=5)
        
        sorted_result = {}
        for result in search_results["tracks"]["items"]:
            formatted_time = ms_to_minutes_seconds(result["duration_ms"])
            sorted_result[result["name"]] = [result["artists"][0]["name"], result["album"]["name"], f"{formatted_time}"]
        
        print(sorted_result)
        return sorted_result


# Define the API endpoints
@app.get("/download_song")
async def download_song(
    song_name: str = Query(...),
    song_artist: str = Query(...),
    bitrate: str = Query(...),
    audio_type: str = Query(...)
):
    
    print(f"Downloading {song_name} by {song_artist} with a bitrate of {bitrate} kbps")
    
    global queue
    if queue:
        return {"message": "Another song is being downloaded. Please try again later."}
    queue = True

    while not is_window_focused:
        time.sleep(2)
    time.sleep(0.7)
    pyautogui.hotkey('ctrl', '2')

    pyautogui.hotkey('ctrl', '1')

    pyautogui.write(f'{song_name} {song_artist}')
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(2)
    pyautogui.hotkey('ctrl', 'f')
    # if use_text_filter:
    #     pyautogui.write(song_name) # text filter
    time.sleep(1)

    pyautogui.press('tab', presses=2, interval=0.1)
    pyautogui.write("remix|cover|edit|mix|version|extended")  # text filter
    time.sleep(2)
    pyautogui.press('enter')
    time.sleep(2)

    pyautogui.press('tab', presses=6, interval=0.1)
    time.sleep(1)
    if audio_type == "flac":
        pyautogui.write(f'>320')  # Bitrate
    else:
        pyautogui.write(f'{bitrate}')  # Bitrate
    time.sleep(1)

    pyautogui.press('enter')
    time.sleep(1)
    pyautogui.press('tab', presses=2, interval=0.1)  # Song duration
    time.sleep(1)

    # pyautogui.write(f'{minutes}:{seconds}') # Song duration
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(1)
    # if use_country_filter:
    #     pyautogui.press('tab', presses=2, interval=0.1)
    #     time.sleep(1)

    #     pyautogui.write(country) # Country filter
    #     pyautogui.press('tab', presses=4, interval=0.1)
    # else:
    pyautogui.press('tab', presses=6, interval=0.1)

    for i in range(0, random.randint(1, 4)):
        pyautogui.press('down')

    # pyautogui.press('down')
    time.sleep(4)

    pyautogui.keyDown("enter")
    time.sleep(2)
    pyautogui.keyUp("enter")
    time.sleep(4)
    pyautogui.hotkey('ctrl', 'w')
    max_checks = 60
    current_checks = 0
    while True:
        if current_checks >= max_checks:
            queue = False
            return {"message": "Song not found. Please try again."}
        for root, dirs, files in os.walk("unsorted_songs"):
            for file in files:
                print(file)
                if file.lower().endswith(('.mp3')):
                    song_path = os.path.join(root, file)
                    audio = EasyID3(song_path)
                    artist = audio['artist'][0].strip(
                    ) if 'artist' in audio else 'Unknown Artist'
                    album = audio['album'][0].strip(
                    ) if 'album' in audio else 'Unknown Album'
                    title = audio['title'][0].strip() if 'title' in audio else os.path.splitext(
                        os.path.basename(song_path))[0]

                    audio_info = MP3(song_path)
                    bitrate = audio_info.info.bitrate / 1000
                    duration = int(audio_info.info.length)

                    artist = re.sub(r'[^\w\-\. ]', '_', artist)
                    album = re.sub(r'[^\w\-\. ]', '_', album)
                    title = re.sub(r'[^\w\-\. ]', '_', title)
                    new_filename = f"{artist} - {title}.{file.split('.')[-1]}"
                    new_path = os.path.join(root, new_filename)
                    time.sleep(2)
                    shutil.move(
                        song_path, "download_ready/" + new_filename)
                    print(f"Downloaded {title} by {artist} ({bitrate} kbps)")
                    queue = False
                    return {"message": "Song downloaded successfully", "url": "http://192.168.2.162:8000/download/" + urllib.parse.quote(new_filename)}

                if file.lower().endswith(('.flac')):
                    song_path = os.path.join(root, file)
                    time.sleep(2)
                    shutil.move(
                        song_path, "download_ready/" + file)
                    print(f"Downloaded {file}")
                    queue = False
                    return {"message": "Song downloaded successfully", "url": "http://192.168.2.162:8000/download/" + urllib.parse.quote(file)}

                else:
                    time.sleep(1)
                    print("Waiting for the song to be downloaded...")
                    current_checks += 1
                    continue
        
        current_checks += 1
        print(current_checks)
        time.sleep(1)


@app.post("/download_playlist")
async def download_playlist(request: DownloadPlaylistRequest):
    global queue
    if queue:
        return {"message": "Another song is being downloaded. Please try again later."}
    queue = True
    playlist_link = request.playlist_link
    auto_download = request.auto_download
    random_user_download = request.random_user_download
    use_text_filter = request.use_text_filter
    allow_remix = request.allow_remix
    use_country_filter = request.use_country_filter
    country = request.country
    download = request.download
    wait_time = request.wait_time

    # Implement the playlist download logic here
    playlist_uri = get_playlist_uri(playlist_link)
    while True:
        try:
            playlist = get_tracks(playlist_uri)
            break
        except Exception as e:
            print(f"Error getting playlist. Trying again in {
                  wait_time} seconds...")
            time.sleep(wait_time)
            wait_time += 60
            continue

    print(f"Playlist contains {len(playlist)} songs.")

    print("Nicotine is focused. Starting download...")

    with console.status("[bold green]Working on tasks...") as status:
        for song in playlist:
            print(f".")

    return {"message": "Playlist downloaded successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="192.168.2.162", port=8000)
