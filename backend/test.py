import pyautogui
import time
import random
from rich.progress import Progress
import threading
import os
import signal
from rich.console import Console
console = Console()
import uvicorn
from fastapi import FastAPI

app = FastAPI()


CLIENT_ID = '2865c34cc5894effa89442ee5aed02f0'
CLIENT_SECRET = "f4f17593c827405d84d39b8c3ce0ab67"
PLAYLIST_LINK = "https://open.spotify.com/playlist/6K7ldh8yMDhJpDLesUjgHY?si=e58481a66dd8452e"

song = 'Feel it still'

auto_download = True
random_user_download = False

use_text_filter = False

allow_remix = False

use_country_filter = False
country = 'NL,US'

download = True

wait_time = 60



os.system("clear")


import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


CLIENT_CREDENTIALS_MANAGER = SpotifyClientCredentials(
    client_id=CLIENT_ID, client_secret=CLIENT_SECRET
)
SP = spotipy.Spotify(client_credentials_manager=CLIENT_CREDENTIALS_MANAGER)


def get_playlist_uri(playlist_link):
    return playlist_link.split("/")[-1].split("?")[0]


def get_tracks():
    tracks = []
    playlist_uri = get_playlist_uri(PLAYLIST_LINK)
    for track in SP.playlist_tracks(playlist_uri)["items"]:
        track_uri = track["track"]["uri"]
        track_name = track["track"]["name"]
        track_artists = track["track"]["artists"]
        result = track_name, track_artists, SP.audio_features(track_uri)
        tracks.append(result)

    return tracks

while True:
    try:
        playlist = get_tracks()
        break
    except Exception as e:
        print(f"Error getting playlist. Trying again in {wait_time} seconds...")
        time.sleep(wait_time)
        wait_time =+ 60
        continue
    

print(f"Playlist contains {len(playlist)} songs.")
confirm = input("Do you want to download these songs? (y/n)")
if "n" not in confirm.lower():
    exit()
    


def window_checker():
    global is_window_focused
    while True:
        time.sleep(0.5)
        active_window = os.popen('xdotool getwindowfocus getwindowname').read()
        is_window_focused = "Nicotine" in active_window

print("Please make sure you have Nicotine running in the background and the window is focused.")

print("Waiting for Nicotine to be focused...")
is_window_focused = False
while not is_window_focused:
    time.sleep(1)
    active_window = os.popen('xdotool getwindowfocus getwindowname').read()
    is_window_focused = "Nicotine" in active_window

window_checker_thread = threading.Thread(target=window_checker, name="Window Checker", daemon=True)
window_checker_thread.start()

print("Nicotine is focused. Starting download...")

with console.status("[bold green]Working on tasks...") as status:

    for song in playlist:
        
        song_name = song[0]
        millis = int(song[2][0]['duration_ms'])
        seconds=(millis/1000)%60
        seconds = int(seconds)
        minutes=(millis/(1000*60))%60
        minutes = int(minutes)
        hours=(millis/(1000*60*60))%24
        
        song_artists = song[1][0]['name']
        # print(song_name)
        # print(song_artists)
        # print ("%d:%d" % (minutes, seconds))
        status.update(f"[red]Downloading {song[0]} ({minutes}:{seconds})")
        
        song_name = f'{song_name} {song_artists}'
        
        

        if download:
            while not is_window_focused:
                time.sleep(2)
            time.sleep(0.7)
            pyautogui.hotkey('ctrl', '2')
            
            pyautogui.hotkey('ctrl', '1')
            
            pyautogui.write(song_name)
            pyautogui.press('enter')
            time.sleep(2)
            pyautogui.hotkey('ctrl', 'f')
            if use_text_filter:
                pyautogui.write(song_name) # text filter
            time.sleep(1)
            
            if not allow_remix:
                pyautogui.press('tab', presses=2, interval=0.1)
                pyautogui.write("remix|cover|edit|mix|version|extended") # text filter
                time.sleep(2)
                pyautogui.press('enter')
                time.sleep(2)
                
                pyautogui.press('tab', presses=6, interval=0.1)
                time.sleep(1)
            else:
                pyautogui.press('tab', presses=8, interval=0.1)
                time.sleep(1)
            pyautogui.write('=320') # Bitrate
            time.sleep(1)
            
            pyautogui.press('enter')
            time.sleep(1)
            pyautogui.press('tab', presses=2, interval=0.1) # Song duration
            time.sleep(1)
            
            pyautogui.write(f'{minutes}:{seconds}') # Song duration
            time.sleep(1)
            pyautogui.press('enter')
            time.sleep(1)
            if use_country_filter:
                pyautogui.press('tab', presses=2, interval=0.1)
                time.sleep(1)
                
                pyautogui.write(country) # Country filter
                pyautogui.press('tab', presses=4, interval=0.1)
            else:
                pyautogui.press('tab', presses=6, interval=0.1)
            
            if random_user_download:
                for i in range(0, random.randint(1, 25)):
                    pyautogui.press('down')
            time.sleep(1)
            if auto_download:
                pyautogui.press('enter')
                
            time.sleep(2)
            pyautogui.hotkey('ctrl', 'w')
            
            status.stop()
            console.log(f"[green]Downloaded {song[0]} ({minutes}:{seconds})")
            
if __name__=="__main__":
    uvicorn.run(app ,host='0.0.0.0', port=4557, reload=True, debug=True, workers=3)