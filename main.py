import asyncio

import discord
import random
from search_weather_yandex import WeatherToday
from yandex_schdule import ScheduleTransport
from music_youtube_download import download_audio
import time

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
        self.music_queue = []
        self.message_interface = None
        self.music_count = 0
        self.mes_music_control = None
        self.clicked_next = False
        self.react_hints_mes_sp = []

        self.room_activated = False
        self.room_channel = None

    async def on_voice_server_update(self, data):
        print(data)

    async def on_reaction_add(self, reaction, user):
        if reaction.message == self.mes_music_control:
            if user.name != 'Текстовый помощник Алиса':
                if reaction.emoji == '❔':
                    await reaction.message.remove_reaction('❔', user)

                    self.react_hints_mes_sp.append(await reaction.message.channel.send(f'❔ - для подсказки\n'
                                                                                       f'❌ - для остановки потока\n'
                                                                                       f'⏸️ - для паузы\n'
                                                                                       f'▶️ - для продолжения'
                                                                                       f' воспроизведения\n'
                                                                                       f'⏭️ для пропуска трека\n'))
                elif reaction.emoji == '❌':
                    if len(self.react_hints_mes_sp) > 0:
                        for el in self.react_hints_mes_sp:
                            await el.delete()
                    if self.voice_client:
                        if self.voice_client.is_playing():
                            self.voice_client.stop()
                        self.music_queue = []
                        await reaction.message.delete()
                    self.react_hints_mes_sp = []

                elif reaction.emoji == '⏸️':
                    await reaction.message.remove_reaction('⏸️', user)
                    if self.voice_client:
                        if self.voice_client.is_playing():
                            self.voice_client.pause()
                        else:
                            self.react_hints_mes_sp.append(await reaction.message.channel.
                                                           send('Уже поставлена на паузу'))

                elif reaction.emoji == '▶️':
                    await reaction.message.remove_reaction('▶️', user)
                    if self.voice_client:
                        if self.voice_client.is_paused():
                            self.voice_client.resume()
                        else:
                            self.react_hints_mes_sp.append(await reaction.message.channel.send('Уже играет'))

                elif reaction.emoji == '⏭️':
                    await reaction.message.remove_reaction('⏭️', user)
                    if self.voice_client:
                        if len(self.music_queue) > 0:
                            self.voice_client.stop()
                            self.clicked_next = True
                            await self.play_audio()

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
            if message.content.startswith('Алиса, команды'):
                await message.channel.send('"привет", "как дела?", "создай канал", "удали канал",'
                                           ' "погода на сегодня/завтра", "подключись ко мне", "отключись от меня"'
                                           ' "включи <ссылка youtube>", "расписание автобусов/эелектричек",'
                                           ' "объяви собрание", "закончи собрание", "найди/как <запрос>"')

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
                    found = False
                    for elem in self.voice_channels:
                        if message.author in elem.members:
                            self.connected_voice_channel = elem
                            await message.channel.send('Оки')
                            self.voice_client = await elem.connect()
                            found = True
                    if found is False:
                        await message.channel.send('А куда?')

                elif text.startswith('включи'):
                    if self.voice_client is None:
                        await message.channel.send('Мне некуда включать музыку')
                    else:
                        text = text.replace('включи ', '')
                        url = text
                        await message.channel.send('Анализирую ссылку')
                        result, file, name, duration = download_audio(url)
                        if result:
                            if self.voice_client.is_playing() is False:
                                self.music_queue.append(url)
                                self.mes_music_control = await message.channel.send(f'Сейчас играет {name}')
                                await self.mes_music_control.pin()
                                await self.mes_music_control.add_reaction('❔')
                                await self.mes_music_control.add_reaction('❌')
                                await self.mes_music_control.add_reaction('⏸️')
                                await self.mes_music_control.add_reaction('▶️')
                                await self.mes_music_control.add_reaction('⏭️')
                                await self.play_audio()
                            else:
                                await message.channel.send('Добавила в очередь')
                                self.music_queue.append(url)
                        else:
                            await message.channel.send(file)
                elif text.startswith('выключи'):
                    if self.voice_client is None:
                        await message.channel.send('А я ничего и не включала')
                    else:
                        self.voice_client.stop()
                        self.music_queue = []
                        await self.mes_music_control.delete()

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
                                                   f' в комнате сбора')
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

                elif text == 'расскажи анекдот' or text == 'расскажи шутку' or text == 'пошути':
                    joke = self.random_choose_phrase(self.read_file('phrases/jokes.txt'))
                    await message.channel.send(joke)

                else:

                    await message.channel.send('Мне неизвестна эта команда. Напишите'
                                               ' "Алиса, команды" чтобы узнать больше'
                                               'о моих способностях')

    async def play_audio(self):
        ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                          'options': '-vn'}
        while len(self.music_queue) > 0:
            if self.voice_client.is_playing() is False:
                audio = download_audio(self.music_queue.pop(0))
                await self.mes_music_control.edit(content=f'Сейчас играет {audio[2]}\n'
                                                          f'Треков в очереди: {len(self.music_queue)}')
                self.voice_client.play(discord.FFmpegPCMAudio(
                    source=audio[1], **ffmpeg_options))
                await asyncio.sleep(audio[3])
            if self.clicked_next:
                self.clicked_next = False
                break

    def read_file(self, filename):
        with open(filename, mode='r', encoding='utf-8') as fl:
            sp = fl.readlines()
        return sp

    def random_choose_phrase(self, sp):
        phrase = random.choice(sp)
        return phrase


client = MyClient()
client.run(token)
