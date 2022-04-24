import os

from youtube_dl import YoutubeDL


def download_audio(link):
    audio_downloader = YoutubeDL({'format':'bestaudio', 'ext': 'mp3'})
    try:
        URL = link
        os.chdir('music_files')
        audio_downloader.extract_info(URL)

    except Exception:
        print("Couldn\'t download the audio")
