import os
import shutil
import json
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
import re
from rich.console import Console


def get_song_info(song_path):
    try:
        audio = EasyID3(song_path)
        artist = audio['artist'][0].strip() if 'artist' in audio else 'Unknown Artist'
        album = audio['album'][0].strip() if 'album' in audio else 'Unknown Album'
        title = audio['title'][0].strip() if 'title' in audio else os.path.splitext(os.path.basename(song_path))[0]

        audio_info = MP3(song_path)
        bitrate = audio_info.info.bitrate / 1000
        duration = int(audio_info.info.length)

        return artist, album, title, bitrate, duration
    except Exception as e:
        print(f"Error reading metadata for {song_path}: {e}")
        return 'Unknown Artist', 'Unknown Album', os.path.splitext(os.path.basename(song_path))[0], 0, 0

def remove_empty_folders(path):
    for root, dirs, files in os.walk(path, topdown=False):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            if not os.listdir(dir_path):
                os.rmdir(dir_path)
                print(f"Removed empty folder: {dir_path}")

def process_folder(folder_path, converted_songs_file):
    converted_songs = load_converted_songs(converted_songs_file)
    sorted_folder_path = "sorted_songs"
    os.makedirs(sorted_folder_path, exist_ok=True)

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(('.mp3', '.m4a', '.wav', '.flac')):
                song_path = os.path.join(root, file)

                artist, album, title, bitrate, duration = get_song_info(song_path)
                artist = re.sub(r'[^\w\-\. ]', '_', artist)
                album = re.sub(r'[^\w\-\. ]', '_', album)
                title = re.sub(r'[^\w\-\. ]', '_', title)
                new_filename = f"{artist} - {title}.{file.split('.')[-1]}"
                new_path = os.path.join(root, new_filename)

                if new_path != song_path:
                    try:
                        destination_dir = os.path.join(sorted_folder_path, artist, album)
                        os.makedirs(destination_dir, exist_ok=True)
                        destination = os.path.join(destination_dir, new_filename)
                        if destination in converted_songs:
                            print(f"Skipping '{file}' as it is a duplicate.")
                            continue
                        shutil.move(song_path, destination)
                        print(f"Moved '{file}' to '{destination}'")
                        converted_songs[destination] = {'bitrate': bitrate, 'duration': duration, 'artist': artist, 'album': album, 'title': title}
                    except Exception as e:
                        print(f"Error moving file '{file}': {e}")
                else:
                    if song_path in converted_songs:
                        print(f"Skipping '{file}' as it is a duplicate.")
                        continue
                    converted_songs[song_path] = {'bitrate': bitrate, 'duration': duration, 'artist': artist, 'album': album, 'title': title}

    save_converted_songs(converted_songs, converted_songs_file)
    remove_empty_folders(sorted_folder_path)

def load_converted_songs(converted_songs_file):
    if os.path.exists(converted_songs_file):
        with open(converted_songs_file, 'r') as f:
            converted_songs = json.load(f)
    else:
        converted_songs = {}
    return converted_songs

def save_converted_songs(converted_songs, converted_songs_file):
    with open(converted_songs_file, 'w') as f:
        json.dump(converted_songs, f, indent=4)

if __name__ == '__main__':
    folder_path = "unsorted_songs"
    converted_songs_file = 'converted_songs.json'
    process_folder(folder_path, converted_songs_file)