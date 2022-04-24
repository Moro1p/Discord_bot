import discord
import random
from search_weather_yandex import WeatherToday
from yandex_schdule import ScheduleTransport
from music_files.music_youtube_download import download_audio
import os
import ffmpeg

with open('token.txt', encoding='utf-8') as fl:
    token = fl.readline()


class MyClient(discord.Client):
    def __init__(self):
        super().__init__()

        self.text_channels = []
        self.category_channels = []
        self.voice_channels = []

        self.connected_voice_channel = None
        self.voice_client = None

        self.room_activated = False
        self.room_channel = None

        self.guess_name_started = False
        self.names = []
        self.phrases = []
        self.i = 0

    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        for guild in client.guilds:
            for channel in guild.channels:
                if str(channel) == 'general':
                    await channel.send('К работе готова')
                if str(channel.type) == 'text':
                    self.text_channels.append(channel)
                elif str(channel.type) == 'category':
                    self.category_channels.append(channel)
                elif str(channel.type) == 'voice':
                    self.voice_channels.append(channel)

    async def on_message(self, message):
        if message.author != 'Текстовый помощник Алиса#1646':
            if self.guess_name_started:
                if message.content() == 'Нет' or message.content() == 'Не угадала' or message.content() == 'Неа':
                    await message.channel.send(f'{random.choice(self.phrases)} {self.names[self.i]}')
                    self.i += 1
                else:
                    await message.channel.send(f'Я так и знала')
                    self.i = 0
                    self.guess_name_started = False

            if message.content.startswith('Алиса, команды'):
                await message.channel.send('"привет", "как дела?", "создай канал", "удали канал", "погода на сегодня",'
                                           ' "расписание автобусов/эелектричек"')

            elif message.content.startswith('Алиса, '):
                text = message.content.replace('Алиса, ', '')
                if text == 'привет':
                    await message.channel.send(f'Привет, {str(message.author).split("#")[0]}')
                elif text == 'как дела?' or text == 'как жизнь?' or text == 'как делишки?':
                    response = self.random_choose_phrase(self.read_file('phrases/how_everything.txt'))
                    await message.channel.send(response)

                elif text == 'кто ты?' or text == 'представься':
                    response1 = self.random_choose_phrase(self.read_file('phrases/who_are_you.txt'))
                    await message.channel.send(response1)

                elif text == 'кто':
                    response = self.random_choose_phrase(self.read_file('phrases/who.txt'))
                    await message.channel.send(response)

                elif text == 'где':
                    response = self.random_choose_phrase(self.read_file('phrases/where.txt'))
                    await message.channel.send(response)

                elif text == 'зачем':
                    response = self.random_choose_phrase(self.read_file('phrases/why.txt'))
                    await message.channel.send(response)

                elif text.startswith('как'):
                    mes = text.split()[1:]
                    if mes:
                        await message.channel.send('Сейчас разберемся')
                        await message.channel.send(f'https://yandex.ru/search?text={"%20".join(text.split())}')
                    else:
                        response = self.random_choose_phrase(self.read_file('phrases/how.txt'))
                        await message.channel.send(response)

                elif text.startswith('найди') or text.startswith('поищи') or text.startswith('открой'):
                    mes = text.split()[1:]
                    if mes:
                        await message.channel.send('Ищу в Яндексе')
                        await message.channel.send(f'https://yandex.ru/search?text={"%20".join(mes)}')
                    else:
                        await message.channel.send('Я не расслышала запрос, повторите пожалуйста')

                elif text.startswith('создай канал'):
                    chan_to_create = text.replace('создай канал', '')[1:]
                    if chan_to_create:
                        chan = await message.guild.create_text_channel(chan_to_create)
                        self.text_channels.append(chan)
                        await message.channel.send(f'Канал {chan_to_create} успешно создан')
                    else:
                        await message.channel.send('Я не расслышала название, повторите пожалуйста')

                elif text.startswith('удали канал'):
                    chan_to_delete = text.replace('удали канал', '')[1:]
                    print(chan_to_delete)
                    deleted = False
                    for elem in self.text_channels:
                        if elem.name == chan_to_delete:
                            deleted = True
                            self.text_channels.remove(elem)
                            await elem.delete()
                    if deleted:
                        await message.channel.send(f'Канал {chan_to_delete} успешно удален')
                    else:
                        await message.channel.send(f'Канал {chan_to_delete} не найден')

                elif text == 'погода на сегодня':
                    wthr = WeatherToday()
                    await message.channel.send(wthr.form_answer_today())

                elif text == 'погода на завтра':
                    wthr = WeatherToday()
                    await message.channel.send(wthr.form_answer_tomorrow())

                elif text.startswith('расписание '):
                    schd = ScheduleTransport()
                    text = text.replace('расписание ', '')
                    if text.startswith('автобусов '):
                        text = text.replace('автобусов ', '')
                        a, b = text.split(' - ')
                        if a is None or b is None:
                            await message.channel.send('Не поняла вас, можете повторить?')
                        flag, response = schd.get_schedule_busAB(a, b)
                        if flag:
                            ans = '\n'.join(response)
                            await message.channel.send(f'{ans}')
                        else:
                            await message.channel.send(response)
                    if text.startswith('электричек '):
                        text = text.replace('электричек ', '')
                        a, b = text.split(' - ')
                        if a is None or b is None:
                            await message.channel.send('Не поняла вас, можете повторить?')
                        flag, response = schd.get_schedule_trainAB(a, b)
                        if flag:
                            ans = '\n'.join(response)
                            await message.channel.send(f'{ans}')
                        else:
                            await message.channel.send(response)
                elif text.startswith('подключись ко мне'):
                    for elem in self.voice_channels:
                        if message.author in elem.members:
                            print(type(elem))
                            self.connected_voice_channel = elem
                            await message.channel.send('Оки')
                            self.voice_client = await elem.connect()
                        else:
                            await message.channel.send('А куда?')
                elif text.startswith('включи'):
                    text = text.replace('включи ', '')
                    url = text
                    download_audio(url)
                    cod = text.split('=')[1]
                    sp = []
                    os.chdir('..')
                    for dirs, dir, files in os.walk('music_files'):
                        for elem in files:
                            if '.py' not in str(elem):
                                sp.append(elem)
                    for elem in sp:
                        if cod in elem:
                            print(elem)
                            input_audio = ffmpeg.input(f'./music_files/{elem}')
                            source = discord.FFmpegPCMAudio(f'music_files/{elem}')
                            self.voice_client.play(input_audio)

                elif text == 'отключись от меня':
                    if self.connected_voice_channel is None:
                        await message.channel.send('Я никуда и не подключалась')
                    else:
                        await self.voice_client.disconnect()

                elif text == 'объяви собрание':
                    if self.room_activated is False:
                        self.room_activated = True
                        self.room_channel = await message.guild.create_voice_channel('Комната сбора')
                        self.voice_channels.append(self.room_channel)
                        await message.channel.send(f'@everyone {message.author} объявил собрание'
                                                   f'в комнате сбора')
                    else:
                        await message.channel.send('Уже есть начатое собрание')

                elif text == 'закончи собрание':
                    if self.room_activated is True:

                        if len(self.room_channel.members) == 0:
                            self.room_activated = False
                            self.voice_channels.remove(self.room_channel)
                            await self.room_channel.delete()
                        else:
                            await message.channel.send('Не все участники покинули канал')
                    else:
                        await message.channel.send('Нет активной комнаты сбора')

                elif text == 'угадай имя':
                    self.guess_name_started = True
                    self.names, self.phrases = self.guess_name_game('guess_name.txt', 'guess_start_phrase.txt')
                    await message.channel.send(f'{random.choice(self.phrases)} {self.names[self.i]}')
                    self.i += 1

                else:

                    await message.channel.send('Мне неизвестна эта команда. Напишите'
                                               ' "Алиса, команды" чтобы узнать больше'
                                               'о моих способностях')

    def read_file(self, filename):
        with open(filename, mode='r', encoding='utf-8') as fl:
            sp = fl.readlines()
        return sp

    def random_choose_phrase(self, sp):
        phrase = random.choice(sp)
        return phrase

    def guess_name_game(self, names_file, start_phrases_file):
        with open(names_file, encoding='utf-8') as nfl:
            names_sp = nfl.readlines()
        nfl.close()
        random.shuffle(names_sp)
        with open(start_phrases_file, encoding='utf-8') as spfl:
            phrases_sp = spfl.readlines()
        spfl.close()
        return names_sp, phrases_sp


client = MyClient()
client.run(token)
