import random

import requests
import threading
from telebot import types
from menuBot import Menu, goto_menu

# -----------------------------------------------------------------------
activeGames = {}  # Тут будем накапливать все активные игры. У пользователя может быть только одна активная игра


def newGame(chatID, newGame):
    activeGames.update({chatID: newGame})
    return newGame


def getGame(chatID):
    return activeGames.get(chatID, None)


def stopGame(chatID):
    activeGames.pop(chatID, None)

# -----------------------------------------------------------------------
class Card:
    emo_SPADES = "U0002660"  # Unicod эмоджи Пики
    emo_CLUBS = "U0002663"  # Unicod эмоджи Крести
    emo_HEARTS = "U0002665"  # Unicod эмоджи Черви
    emo_DIAMONDS = "U0002666"  # Unicod эмоджи Буби

    def __init__(self, card):
        if isinstance(card, dict):  # если передали словарь
            self.__card_JSON = card
            self.code = card["code"]
            self.suit = card["suit"]
            self.value = card["value"]
            self.cost = self.get_cost_card()
            self.color = self.get_color_card()
            self.__imagesPNG_URL = card["images"]["png"]
            self.__imagesSVG_URL = card["images"]["svg"]
        # print(self.value, self.suit, self.code)

        elif isinstance(card, str):  # карту передали строкой, в формате "2S"
            self.__card_JSON = None
            self.code = card

            value = card[0]
            if value == "0":
                self.value = "10"
            elif value == "J":
                self.value = "JACK"
            elif value == "Q":
                self.value = "QUEEN"
            elif value == "K":
                self.value = "KING"
            elif value == "A":
                self.value = "ACE"
            elif value == "X":
                self.value = "JOKER"
            else:
                self.value = value

            suit = card[1]
            if suit == "1":
                self.suit = ""
                self.color = "BLACK"

            elif suit == "2":
                self.suit = ""
                self.color = "RED"

            else:
                if suit == "S":
                    self.suit = "SPADES"  # Пики
                elif suit == "C":
                    self.suit = "CLUBS"  # Крести
                elif suit == "H":
                    self.suit = "HEARTS"  # Черви
                elif suit == "D":
                    self.suit = "DIAMONDS"  # Буби

                self.cost = self.get_cost_card()
                self.color = self.get_color_card()

    def get_cost_card(self):
        if self.value == "JACK":
            return 2
        elif self.value == "QUEEN":
            return 3
        elif self.value == "KING":
            return 4
        elif self.value == "ACE":
            return 11
        elif self.value == "JOKER":
            return 1
        else:
            return int(self.value)

    def get_color_card(self):
        if self.suit == "SPADES":  # Пики
            return "BLACK"
        elif self.suit == "CLUBS":  # Крести
            return "BLACK"
        elif self.suit == "HEARTS":  # Черви
            return "RED"
        elif self.suit == "DIAMONDS":  # Буби
            return "RED"


# -----------------------------------------------------------------------
class Game21:
    def __init__(self, deck_count=1, jokers_enabled=False):
        new_pack = self.new_pack(deck_count, jokers_enabled)  # в конструкторе создаём новую пачку из deck_count-колод
        if new_pack is not None:
            self.pack_card = new_pack  # сформированная колода
            self.remaining = new_pack["remaining"],  # количество оставшихся карт в колоде
            self.card_in_game = []  # карты в игре
            self.arr_cards_URL = []  # URL карт игрока
            self.mediaCards = []
            self.score = 0  # очки игрока
            self.status = None  # статус игры, True - игрок выиграл, False - Игрок проиграл, None - Игра продолжается

    # ---------------------------------------------------------------------
    def new_pack(self, deck_count, jokers_enabled=False):
        txtJoker = "&jokers_enabled=true" if jokers_enabled else ""
        response = requests.get(f"https://deckofcardsapi.com/api/deck/new/shuffle/?deck_count={deck_count}" + txtJoker)
        # создание стопки карт из "deck_count" колод по 52 карты
        if response.status_code != 200:
            return None
        pack_card = response.json()
        return pack_card

    # ---------------------------------------------------------------------
    def get_cards(self, card_count=1):
        if self.pack_card == None:
            return None
        if self.status != None:  # игра закончена
            return None

        deck_id = self.pack_card["deck_id"]
        response = requests.get(f"https://deckofcardsapi.com/api/deck/{deck_id}/draw/?count={card_count}")
        # достать из deck_id-колоды card_count-карт
        if response.status_code != 200:
            return False

        new_cards = response.json()
        if new_cards["success"] != True:
            return False
        self.remaining = new_cards["remaining"]  # обновим в классе количество оставшихся карт в колоде

        arr_newCards = []
        for card in new_cards["cards"]:
            card_obj = Card(card)  # создаем объекты класса Card и добавляем их в список карт у игрока
            arr_newCards.append(card_obj)
            self.card_in_game.append(card_obj)
            self.score = self.score + card_obj.cost
            self.arr_cards_URL.append(card["image"])
            self.mediaCards.append(types.InputMediaPhoto(card["image"]))

        if self.score > 21:
            self.status = False
            text_game = "Очков: " + str(self.score) + " ВЫ ПРОИГРАЛИ!"

        elif self.score == 21:
            self.status = True
            text_game = "ВЫ ВЫИГРАЛИ!"
        else:
            self.status = None
            text_game = "Очков: " + str(self.score) + " в колоде осталось карт: " + str(self.remaining)

        return text_game


# -----------------------------------------------------------------------
class GameRPS:
    values = ["Камень", "Ножницы", "Бумага"]
    name = "Игра Камень-Ножницы-Бумага (Мультиплеер)"
    text_rules = "<b>Победитель определяется по следующим правилам:</b>\n" \
                 "1. Камень побеждает ножницы\n" \
                 "2. Бумага побеждает камень\n" \
                 "3. Ножницы побеждают бумагу\n" \
                 "подробная информация об игре: <a href='https://ru.wikipedia.org/wiki/%D0%9A%D0%B0%D0%BC%D0%B5%D0%BD%D1%8C,_%D0%BD%D0%BE%D0%B6%D0%BD%D0%B8%D1%86%D1%8B,_%D0%B1%D1%83%D0%BC%D0%B0%D0%B3%D0%B0'>Wikipedia</a>"
    url_picRules = "https://i.ytimg.com/vi/Gvks8_WLiw0/maxresdefault.jpg"

    def __init__(self):
        self.computerChoice = self.__class__.getRandomChoice()

    def newGame(self):
        self.computerChoice = self.__class__.getRandomChoice()

    @classmethod
    def getRandomChoice(cls):
        lenValues = len(cls.values)
        import random
        rndInd = random.randint(0, lenValues - 1)
        return cls.values[rndInd]

    def playerChoice(self, player1Choice):
        winner = None

        code = player1Choice[0] + self.computerChoice[0]
        if player1Choice == self.computerChoice:
            winner = "Ничья!"
        elif code == "КН" or code == "БК" or code == "НБ":
            winner = "Игрок выиграл!"
        else:
            winner = "Компьютер выиграл!"

        return f"{player1Choice} vs {self.computerChoice} = " + winner


# -----------------------------------------------------------------------
class GameRPS_Multiplayer:
    game_duration = 10  # сек.
    values = ["Камень", "Ножницы", "Бумага"]
    name = "Игра Камень-Ножницы-Бумага (Мультиплеер)"
    text_rules = "<b>Победитель определяется по следующим правилам:</b>\n" \
                 "1. Камень побеждает ножницы\n" \
                 "2. Бумага побеждает камень\n" \
                 "3. Ножницы побеждают бумагу\n" \
                 "подробная информация об игре: <a href='https://ru.wikipedia.org/wiki/%D0%9A%D0%B0%D0%BC%D0%B5%D0%BD%D1%8C,_%D0%BD%D0%BE%D0%B6%D0%BD%D0%B8%D1%86%D1%8B,_%D0%B1%D1%83%D0%BC%D0%B0%D0%B3%D0%B0'>Wikipedia</a>"
    url_picRules = "https://i.ytimg.com/vi/Gvks8_WLiw0/maxresdefault.jpg"

    class Player:

        def __init__(self, playerID, playerName):
            self.id = playerID
            self.gameMessage = None
            self.name = playerName
            self.scores = 0
            self.choice = None
            self.lastChoice = ""

        def __str__(self):
            return self.name

    def __init__(self, bot, chat_user):
        self.id = chat_user.id
        self.gameNumber = 1  # счётчик сыгранных игр
        self.objBot = bot
        self.players = {}
        self.gameTimeLeft = 0
        self.objTimer = None
        self.winner = None
        self.lastWinner = None
        self.textGame = ""
        self.addPlayer(None, "Компьютер")
        self.addPlayer(chat_user.id, chat_user.userName)

    def addPlayer(self, playerID, playerName):
        newPlayer = self.Player(playerID, playerName)
        self.players[playerID] = newPlayer
        if playerID is not None:  # None - это компьютер
            self.startTimer()  # при присоединении нового игрока перезапустим таймер
            self.setTextGame()
            # создадим в чате пользователя игровое сообщение с кнопками, и сохраним его для последующего редактирования
            url_picRules = self.url_picRules
            keyboard = types.InlineKeyboardMarkup()
            list_btn = []
            for keyName in self.values:
                list_btn.append(types.InlineKeyboardButton(text=keyName,
                                                           callback_data="GameRPSm|Choice-" + keyName + "|" + Menu.setExtPar(
                                                               self)))
            keyboard.add(*list_btn)
            list_btn = types.InlineKeyboardButton(text="Выход", callback_data="GameRPSm|Exit|" + Menu.setExtPar(self))
            keyboard.add(list_btn)
            gameMessage = self.objBot.send_photo(playerID, photo=url_picRules, caption=self.textGame, parse_mode='HTML',
                                                 reply_markup=keyboard)
            self.players[playerID].gameMessage = gameMessage
        else:
            newPlayer.choice = self.__class__.getRandomChoice()
        self.sendMessagesAllPlayers([playerID])  # отправим всем остальным игрокам информацию о новом игроке
        return newPlayer

    def delPlayer(self, playerID):
        print("DEL")
        remotePlayer = self.players.pop(playerID)
        try:
            self.objBot.delete_message(chat_id=remotePlayer.id, message_id=remotePlayer.gameMessage.id)
        except:
            pass
        self.objBot.send_message(chat_id=remotePlayer.id, text="Мне жаль, вас выкинуло из игры!")
        goto_menu(self.objBot, remotePlayer.id, "Игры")
        self.findWiner()  # как только игрок выходит, проверим среди оставшихся есть ли победитель
        if len(self.players.values()) == 1:
            stopGame(self.id)

    def getPlayer(self, chat_userID):
        return self.players.get(chat_userID)

    def newGame(self):
        self.gameNumber += 1
        self.lastWinner = self.winner
        self.winner = None
        for player in self.players.values():
            player.lastChoice = player.choice
            if player.id == None:  # это компьютер
                player.choice = self.__class__.getRandomChoice()
            else:
                player.choice = None
        self.startTimer()  # запустим таймер игры (если таймер активен, сбросим его)

    def looper(self):
        print("LOOP", self.objTimer)
        if self.gameTimeLeft > 0:
            self.setTextGame()
            self.sendMessagesAllPlayers()
            self.gameTimeLeft -= 1
            self.objTimer = threading.Timer(1, self.looper)
            self.objTimer.start()
            print(self.objTimer.name, self.gameTimeLeft)
        else:
            delList = []
            for player in self.players.values():
                if player.choice is None:
                    delList.append(player.id)
            for idPlayer in delList:
                self.delPlayer(idPlayer)

    def startTimer(self):
        print("START")
        self.stopTimer()
        self.gameTimeLeft = self.game_duration
        self.looper()

    def stopTimer(self):
        print("STOP")
        self.gameTimeLeft = 0
        if self.objTimer is not None:
            self.objTimer.cancel()
            self.objTimer = None

    @classmethod
    def getRandomChoice(cls):
        import random
        # lenValues = len(cls.values)
        # rndInd = random.randint(0, lenValues-1)
        # return cls.values[rndInd]
        return random.choice(cls.values)

    def checkEndGame(self):
        isEndGame = True
        for player in self.players.values():
            isEndGame = isEndGame and player.choice is not None
        return isEndGame

    def playerChoice(self, chat_userID, choice):
        player = self.getPlayer(chat_userID)
        player.choice = choice
        self.findWiner()
        self.sendMessagesAllPlayers()

    def findWiner(self):
        if self.checkEndGame():
            self.stopTimer()  # все успели сделать ход, таймер выключаем
            playersChoice = []
            for player in self.players.values():
                playersChoice.append(player.choice)
            choices = dict(zip(playersChoice, [playersChoice.count(i) for i in playersChoice]))
            if len(choices) == 1 or len(choices) == len(self.__class__.values):
                # если все выбрали одно значение, или если присутствуют все возможные варианты - это ничья
                self.winner = "Ничья"
            else:
                # к этому моменту останется всего два варианта, надо понять есть ли уникальный он и бьёт ли он других
                choice1, quantity1 = choices.popitem()
                choice2, quantity2 = choices.popitem()

                code = choice1[0] + choice2[0]
                if quantity1 == 1 and code == "КН" or code == "БК" or code == "НБ":
                    choiceWiner = choice1
                elif quantity2 == 1 and code == "НК" or code == "КБ" or code == "БН":
                    choiceWiner = choice2
                else:
                    choiceWiner = None

                if choiceWiner != None:
                    winner = ""
                    for player in self.players.values():
                        if player.choice == choiceWiner:
                            winner = player
                            winner.scores += 1
                            break
                    self.winner = winner

                else:
                    self.winner = "Ничья"
        self.setTextGame()

        if self.checkEndGame() and len(self.players) > 1:  # начинаем новую партию через 3 секунды
            self.objTimer = threading.Timer(3, self.newGame)
            self.objTimer.start()

    def setTextGame(self):
        from prettytable import PrettyTable
        mytable = PrettyTable()
        mytable.field_names = ["Игрок", "Счёт", "Выбор", "Результат"]  # имена полей таблицы
        for player in self.players.values():
            mytable.add_row(
                [player.name, player.scores, player.lastChoice, "Победитель!" if self.lastWinner == player else ""])

        textGame = self.text_rules + "\n\n"
        textGame += "<code>" + mytable.get_string() + "</code>" + "\n\n"

        if self.winner is None:
            textGame += f"Идёт игра... <b>Осталось времени для выбора: {self.gameTimeLeft}</b>\n"
        elif self.winner == "Ничья":
            textGame += f"<b>Ничья!</b> Пауза 3 секунды..."
        else:
            textGame += f"Выиграл: <b>{self.winner}! Пауза 3 секунды..."

        self.textGame = textGame

    def sendMessagesAllPlayers(self, excludingPlayers=()):
        try:
            for player in self.players.values():
                if player.id is not None and player.id not in excludingPlayers:
                    textIndividual = f"\n Ваш выбор: {player.choice}, ждём остальных!" if player.choice is not None else "\n"
                    self.objBot.edit_message_caption(chat_id=player.id, message_id=player.gameMessage.id,
                                                     caption=self.textGame + textIndividual, parse_mode='HTML',
                                                     reply_markup=player.gameMessage.reply_markup)
        except:
            pass


# -----------------------------------------------------------------------
class GameExtraWord:
    text_rules = "Добро пожаловать!\nНажимайте на лишние слова и копите очки!"
    url_picRules = 'imgg.png'

    def __init__(self):
        load_possible_texts = self.load_tasks_from_file()  # загружаем все возможные тексты и создаем список словарей
        # print(load_possible_texts)
        if load_possible_texts:
            self.all_possibile_texts = load_possible_texts
            self.used_texts = []  # сюда добавим использованные текста
            self.rating = 0  # сюда добавим заработанные очки игрока
            self.game_finish = False
            self.word_extra = ''
            self.word_extra_id = 0
            self.actual_shuffled_list = []

    def load_tasks_from_file(self, file_name='set_of_words.txt'):
        texts_to_output = []
        with open(file_name, 'r', encoding='utf-8') as f:
            for line in f:
                union_dict = {}

                united_list = (line.split("\\"))

                right_words = united_list[0]
                wrong_words = united_list[1]

                list_of_right_words = right_words.split()
                # print(f'правильные слова: {list_of_right_words}')

                list_of_wrong_words = wrong_words.split()
                # print(f'неправильное слов: {list_of_wrong_words}')

                union_dict['right'] = list_of_right_words
                union_dict['wrong'] = list_of_wrong_words
                texts_to_output.append(union_dict.copy())

        return texts_to_output

    def get_clear_list(self):
        list_to_output = []  # те наборы, которые можно использовать
        for item in self.all_possibile_texts:
            if item not in self.used_texts:
                list_to_output.append(item)
        if list_to_output:
            return list_to_output
        else:
            return None

    def get_random_text_dict(self):
        got_clear_list = self.get_clear_list()

        if got_clear_list:
            random_dict = random.choice(got_clear_list)
            self.used_texts.append(random_dict)
            return random_dict
        else:
            return None

    def get_shuffled_to_give_user(self):
        random_dict = self.get_random_text_dict()

        if random_dict:
            extra_word = random_dict['wrong'][0]

            # print(extra_word, "extra_word")
            # print(type(extra_word))
            right_word = random_dict['right']

            new_list = right_word.copy()
            new_list.append(extra_word)

            random.shuffle(new_list)

            self.word_extra = extra_word
            self.word_extra_id = new_list.index(extra_word)
            self.actual_shuffled_list = new_list
            return self.actual_shuffled_list
        else:
            self.word_extra = ''
            self.word_extra_id = 0
            self.actual_shuffled_list = []  # если ничего не пришло, ставим в переменную ничего
            return self.actual_shuffled_list

    def result_of_round(self, player_choice):
        # https://emojio.ru/animals-nature/26c5-26c5-solntse-za-oblakami.html
        win_emoji = u"\U0001F44D"
        lost_emoji = u"\U0001F44E"
        no_rating_cat = u"\U0001F63E"
        yes_rating_cat = u"\U0001F63B"
        fire_smile = u"\U0001F525"
        confused_smile = u"\U0001F440"

        player_choice = int(player_choice)

        if player_choice == self.word_extra_id:
            self.rating += 100
            result = True
        else:
            if self.rating >= 50:
                self.rating -= 50
            result = False

        result_text_ok = 'Верный'
        result_text_not_ok = 'Не верный'

        rating_msg = f"""Ваши очки: {self.rating} {yes_rating_cat if self.rating else no_rating_cat}"""

        if not self.actual_shuffled_list:
            return f"""Игра окончена, вы просмотрели все варианты {confused_smile}\n\n{rating_msg}"""

        result_msg = f"""Нужно было выбрать лишнее слово из:\n{', '.join(self.actual_shuffled_list)}\n\nВы выбрали: {self.actual_shuffled_list[player_choice]}!\n\nВаш ответ: {result_text_ok if result else result_text_not_ok} {win_emoji if result else lost_emoji}"""

        if self.rating >= 300:
            self.game_finish = True
            return f"""{result_msg}\n\n{rating_msg}\n\nИгра окончена: вы победили {fire_smile}{fire_smile}{fire_smile}"""

        return result_msg + '\n\n' + rating_msg


# -----------------------------------------------------------------------
def callback_worker(bot, cur_user, cmd, par, call):
    chat_id = call.message.chat.id
    message_id = call.message.id

    if cmd == "newGame":
        # bot.edit_message_reply_markup(chat_id, message_id, reply_markup=None)  # удалим кнопки начала игры из чата
        bot.delete_message(chat_id, message_id)
        newGame(chat_id, GameRPS_Multiplayer(bot, cur_user))
        bot.answer_callback_query(call.id)

    elif cmd == "Join":
        # bot.edit_message_reply_markup(chat_id, message_id, reply_markup=None)  # удалим кнопки начала игры из чата
        bot.delete_message(chat_id, message_id)
        gameRSPMult = Menu.getExtPar(par)
        if gameRSPMult is None:  # если наткнулись на кнопку, которой быть не должно
            return
        else:
            gameRSPMult.addPlayer(cur_user.id, cur_user.userName)
        bot.answer_callback_query(call.id)

    elif cmd == "Exit":
        bot.delete_message(chat_id, message_id)
        gameRSPMult = Menu.getExtPar(par)
        if gameRSPMult is not None:
            gameRSPMult.delPlayer(cur_user.id)
        goto_menu(bot, chat_id, "Игры")
        bot.answer_callback_query(call.id)

    elif "Choice-" in cmd:
        gameRSPMult = Menu.getExtPar(par)
        if gameRSPMult is None:  # если наткнулись на кнопку, которой быть не должно - удалим её из чата
            bot.delete_message(chat_id, message_id)
        else:
            choice = cmd[7:]
            gameRSPMult.playerChoice(cur_user.id, choice)
        bot.answer_callback_query(call.id)


def callback_worker_game_extra_word(bot, cur_user, cmd, par, call):
    chat_id = call.message.chat.id
    message_id = call.message.id
    # print(cmd, 'cmd')

    if cmd == "Exit":
        # bot.delete_message(chat_id, message_id)
        goto_menu(bot, chat_id, "Игры")
        bot.answer_callback_query(call.id)


    elif "r+" in cmd:
        game_extra_word = Menu.getExtPar(par)
        # print('внутри')
        if game_extra_word is None:  # если наткнулись на кнопку, которой быть не должно - удалим её из чата
            bot.delete_message(chat_id, message_id)
        else:
            choice = cmd.split('+')[1]
            print('choice user', choice)
            result = game_extra_word.result_of_round(choice)
            print(result)
            bot.delete_message(chat_id, message_id)
            bot.send_message(chat_id, text=result)
            bot.answer_callback_query(call.id)

# -----------------------------------------------------------------------
def get_text_messages(bot, cur_user, message):
    chat_id = message.chat.id
    ms_text = message.text

    # ======================================= реализация игры в 21
    if ms_text == "Карту!":
        game21 = getGame(chat_id)
        if game21 is None:  # если мы случайно попали в это меню, а объекта с игрой нет
            goto_menu(bot, chat_id, "Выход")
            return

        text_game = game21.get_cards(1)
        bot.send_media_group(chat_id, media=game21.mediaCards)  # получим и отправим изображения карт
        bot.send_message(chat_id, text=text_game)

        if game21.status is not None:  # выход, если игра закончена
            stopGame(chat_id)
            goto_menu(bot, chat_id, "Выход")
            return

    elif ms_text == "Стоп!":
        stopGame(chat_id)
        goto_menu(bot, chat_id, "Выход")
        return

    # ======================================= реализация игры Камень-ножницы-бумага
    elif ms_text in GameRPS.values:
        gameRSP = getGame(chat_id)
        if gameRSP is None:  # если мы случайно попали в это меню, а объекта с игрой нет
            goto_menu(bot, chat_id, "Выход")
            return
        text_game = gameRSP.playerChoice(ms_text)
        bot.send_message(chat_id, text=text_game)
        gameRSP.newGame()

    # ======================================= реализация игры Камень-ножницы-бумага Multiplayer
    elif ms_text == "Игра КНБ-MP":
        print('я в мультиплеере кнб МР')
        keyboard = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton(text="Создать новую игру", callback_data="GameRPSm|newGame")
        keyboard.add(btn)
        numGame = 0
        for game in activeGames.values():
            if type(game) == GameRPS_Multiplayer:
                numGame += 1
                btn = types.InlineKeyboardButton(
                    text="Игра КНБ-" + str(numGame) + " игроков: " + str(len(game.players)),
                    callback_data="GameRPSm|Join|" + Menu.setExtPar(game))
                keyboard.add(btn)
        btn = types.InlineKeyboardButton(text="Вернуться", callback_data="GameRPSm|Exit")
        keyboard.add(btn)

        bot.send_message(chat_id, text=GameRPS_Multiplayer.name, reply_markup=types.ReplyKeyboardRemove())
        bot.send_message(chat_id, "Вы хотите начать новую игру, или присоединиться к существующей?",
                         reply_markup=keyboard)

    # ======================================= реализация игры Лишнее Слово
    elif ms_text == "Хочу играть!":

        keyboard = types.InlineKeyboardMarkup()

        game_extra_words = getGame(chat_id)
        if game_extra_words == None:  # если мы случайно попали в это меню, а объекта с игрой нет
            goto_menu(bot, chat_id, "Выход")
            return

        list_of_buttons = game_extra_words.get_shuffled_to_give_user()
        print(f'Выбрать: {game_extra_words.word_extra} ')
        print(f'Выбрать: {game_extra_words.word_extra_id + 1} ')
        if list_of_buttons:
            # print('я тут')
            # print(list_of_buttons)
            for game in activeGames.values():
                if type(game) == GameExtraWord:
                    for index, text_to_button in enumerate(list_of_buttons):
                        print(text_to_button)
                        btn = types.InlineKeyboardButton(text=text_to_button,
                                                         callback_data=f"GameExtraWord|r+{index}|" + Menu.setExtPar(
                                                             game))

                        # каждая кнопка содержит: текст, который показываем пользователю
                        # и текст который вернется при нажатии на конкретную кнопку, в строке содежатся значения разделенные по |
                        # 1 это название игры, 2 это индекс кнопки, 3 это комбинация цифр uuid4 сделанная из объекта класса
                        # пример что вернется при нажатии на кнопку ['GameExtraWord', 'r+0', '8de4d7faa79c4468bfb0ea40bb1b9715']

                        keyboard.add(btn)
                    btn = types.InlineKeyboardButton(text="Выход из игры", callback_data="GameExtraWord|Exit")
                    keyboard.add(btn)

                    bot.send_message(chat_id, "Выберите лишнее слово", reply_markup=keyboard)

        else:  # выход, если игра закончена
            text_to_ouput = game_extra_words.result_of_round(
                999)  # передаем несуществующий индекс(у нас от 0 до 3) чтобы пройти функцию без ошибок, там проверка на тип int
            bot.send_message(chat_id, text_to_ouput)
            bot.send_message(chat_id, "Включите заново если желаете играть еще")
            stopGame(chat_id)
            goto_menu(bot, chat_id, "Выход")


    elif ms_text == "Выход":
        stopGame(chat_id)
        goto_menu(bot, chat_id, "Выход")
        return

# -----------------------------------------------------------------------
if __name__ == "__main__":
    print("Этот код должен использоваться ТОЛЬКО в качестве модуля!")
