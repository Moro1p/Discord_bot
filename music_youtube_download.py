from youtube_dl import YoutubeDL
from pprint import pprint


def download_audio(link):

    audio_downloader = YoutubeDL({'format': 'bestaudio'})
    try:
        URL = link
        if 'list' in URL:
            return False, 'Я пока не умею работать с плейлистами'
        info = audio_downloader.extract_info(URL, download=False)
        file = info['formats'][0]['url']
        return True, file, info["title"], info["duration"]

    except Exception:
        return False, "Какая-то ошибка при воспроизведении", None
