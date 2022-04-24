from youtube_dl import YoutubeDL
import requests
import os


def download_audio(link):
    audio_downloader = YoutubeDL({'format':'bestaudio'})
    try:
        URL = link
        audio_downloader.extract_info(URL)

    except Exception:
        print("Couldn\'t download the audio")


for dirs, dir, files in os.walk('music_files'):
    for elem in files:
        if '.py' not in str(elem):
            print(elem)