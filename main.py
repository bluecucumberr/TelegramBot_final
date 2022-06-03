import telebot
from telebot import types
import menuBot
from menuBot import Menu
import BotGames
import SECRET
import GoogleCalendarBot
import fun
import function_dz

bot = telebot.TeleBot(SECRET.TELEGRAM_TOKEN)


# Функция, обрабатывающая команд
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    start_bot_message = f'Привет, <b>{message.from_user.first_name}</b>. Рад тебя видеть. Обрати внимание на меню ' \
                        f'&#128071 '
    bot.send_message(message.chat.id, start_bot_message, parse_mode='html',
                     reply_markup=Menu.getMenu(chat_id, "Главное меню").markup)


# -----------------------------------------------------------------------
# Получение стикеров от юзера
@bot.message_handler(content_types=['sticker'])
def get_messages(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Это " + message.content_type)

    sticker = message.sticker
    bot.send_message(message.chat.id, sticker)


# -----------------------------------------------------------------------
# Получение аудио от юзера
@bot.message_handler(content_types=['audio'])
def get_messages(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Это " + message.content_type)

    audio = message.audio
    bot.send_message(chat_id, audio)


# -----------------------------------------------------------------------
# Получение голосовухи от юзера
@bot.message_handler(content_types=['voice'])
def get_messages(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Это " + message.content_type)

    voice = message.voice
    bot.send_message(message.chat.id, voice)


# -----------------------------------------------------------------------
# Получение фото от юзера
@bot.message_handler(content_types=['photo'])
def get_messages(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Это " + message.content_type)

    photo = message.photo
    bot.send_message(message.chat.id, photo)


# -----------------------------------------------------------------------
# Получение видео от юзера
@bot.message_handler(content_types=['video'])
def get_messages(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Это " + message.content_type)

    video = message.video
    bot.send_message(message.chat.id, video)


# -----------------------------------------------------------------------
# Получение документов от юзера
@bot.message_handler(content_types=['document'])
def get_messages(message):
    chat_id = message.chat.id
    mime_type = message.document.mime_type
    bot.send_message(chat_id, "Это " + message.content_type + " (" + mime_type + ")")

    document = message.document
    bot.send_message(message.chat.id, document)
    if message.document.mime_type == "video/mp4":
        bot.send_message(message.chat.id, "This is a GIF!")


# -----------------------------------------------------------------------
# Получение координат от юзера
@bot.message_handler(content_types=['location'])
def get_messages(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Это " + message.content_type)

    location = message.location
    bot.send_message(message.chat.id, location)

    from Weather import WeatherFromPyOWN
    pyOWN = WeatherFromPyOWN()
    bot.send_message(chat_id, pyOWN.getWeatherAtCoords(location.latitude, location.longitude))
    bot.send_message(chat_id, pyOWN.getWeatherForecastAtCoords(location.latitude, location.longitude))


# -----------------------------------------------------------------------
# Получение контактов от юзера
@bot.message_handler(content_types=['contact'])
def get_messages(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Это " + message.content_type)

    contact = message.contact
    bot.send_message(message.chat.id, contact)


# -----------------------------------------------------------------------
# Получение сообщений от юзера
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    chat_id = message.chat.id

    cur_user = menuBot.Users.getUser(chat_id)
    if cur_user is None:
        cur_user = menuBot.Users(chat_id, message.json["from"])

    # проверка = мы нажали кнопку подменю, или кнопку действия
    subMenu = menuBot.goto_menu(bot, chat_id,
                                message.text)  # попытаемся использовать текст как команду меню, и войти в него
    if subMenu is not None:
        # Проверим, нет ли обработчика для самого меню. Если есть - выполним нужные команды
        if subMenu.name == "Игра в 21":
            game21 = BotGames.newGame(chat_id, BotGames.Game21(jokers_enabled=True))  # создаём новый экземпляр игры
            text_game = game21.get_cards(2)  # просим 2 карты в начале игры
            bot.send_media_group(chat_id, media=game21.mediaCards)  # получим и отправим изображения карт
            bot.send_message(chat_id, text=text_game)

        elif subMenu.name == "Игра КНБ":
            gameRPS = BotGames.newGame(chat_id, BotGames.GameRPS())  # создаём новый экземпляр игры и регистрируем его
            bot.send_photo(chat_id, photo=gameRPS.url_picRules, caption=gameRPS.text_rules, parse_mode='HTML')

        elif subMenu.name == "Игра лишнее слово":
            game_ext_word = BotGames.newGame(chat_id, BotGames.GameExtraWord())
            # bot.send_message(chat_id, text=game_ext_word.text_rules, parse_mode='HTML')
            with open(game_ext_word.url_picRules,
                      'rb') as f:  # with open чтобы не вылетало при частом обращении к картинке
                bot.send_photo(chat_id, photo=f, caption=game_ext_word.text_rules, parse_mode='HTML')

        elif subMenu.name == "Календарь":
            print('мы создали объект календаря')
            GoogleCalendarBot.new_calendar_obj(chat_id, GoogleCalendarBot.GoogleCalendar())

        return  # мы вошли в подменю, и дальнейшая обработка не требуется

    # проверим, является ли текст текущий команды кнопкой действия
    cur_menu = Menu.getCurMenu(chat_id)
    if cur_menu is not None and message.text in cur_menu.buttons:  # проверим, что команда относится к текущему меню
        module = cur_menu.module

        if module != "":  # проверим, есть ли обработчик для этого пункта меню в другом модуле, если да - вызовем его
            # (принцип инкапсуляции)
            exec(module + ".get_text_messages(bot, cur_user, message)")

        if message.text == "Помощь":
            send_help(bot, chat_id)

    else:
        bot.send_message(chat_id, f"Вы написали: {message.text}\nУ меня нет такой команды")
        menuBot.goto_menu(bot, chat_id, "Главное меню")


# -----------------------------------------------------------------------
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    # если требуется передать один или несколько параметров обработчику кнопки,
    # используйте методы Menu.getExtPar() и Menu.setExtPar()
    # call.data это callback_data, которую мы указали при объявлении InLine-кнопки
    # После обработки каждого запроса вызовете метод answer_callback_query(), чтобы Telegram понял, что запрос обработан
    chat_id = call.message.chat.id
    message_id = call.message.id
    cur_user = menuBot.Users.getUser(chat_id)
    if cur_user is None:
        cur_user = menuBot.Users(chat_id, call.message.json["from"])

    tmp = call.data.split("|")
    print(tmp)
    menu = tmp[0] if len(tmp) > 0 else ""
    cmd = tmp[1] if len(tmp) > 1 else ""
    par = tmp[2] if len(tmp) > 2 else ""

    if menu == "GameRPSm":
        BotGames.callback_worker(bot, cur_user, cmd, par, call)  # обработчик кнопок игры находится в модули игры

    if menu == "GameExtraWord":
        BotGames.callback_worker_game_extra_word(bot, cur_user, cmd, par,
                                                 call)  # обработчик инлайн кнопок игры чата
    if menu == "GCal_call_back":
        GoogleCalendarBot.callback_worker_calendar(bot, cur_user, cmd, par, call)


# -----------------------------------------------------------------------
def send_help(bot, chat_id):
    bot.send_message(chat_id, "Автор: Соловьёва Екатерина")
    info = types.InlineKeyboardMarkup()
    info.add(types.InlineKeyboardButton("Написать автору", url="https://t.me/blue_cucumber"))
    img = open('img.jpg', 'rb')
    bot.send_photo(chat_id, img, reply_markup=info)

    bot.send_message(chat_id, "Активные пользователи чат-бота:")
    for el in menuBot.Users.activeUsers:
        bot.send_message(chat_id, menuBot.Users.activeUsers[el].getUserHTML(), parse_mode='HTML')


# ---------------------------------------------------------------------

bot.polling(none_stop=True, interval=0)  # запуск бота
