def get_text_messages(bot, cur_user, message):

    if message.text == "1 пункт":
        bot.send_message(message.chat.id, text="Задание: создайте переменную с вашим именем. Выведите ее на экран.")
        my_name = "Екатерина"
        bot.send_message(message.chat.id, text=f"Ваше имя {my_name}")

    elif message.text == "2 пункт":
        bot.send_message(message.chat.id,
                         text="Задание: создайте переменную с вашим возрастом. Выведите на экран осмысленное сообщение о вас и вашем возрасте.")
        my_name = "Екатерина"
        my_age = "19"
        bot.send_message(message.chat.id, text=f"Ваше имя {my_name}. Вам {my_age} лет.")

    elif message.text == "3 пункт":
        bot.send_message(message.chat.id,
                         text="Задание: создайте переменную с пятикратным повторением вашего имени.")
        my_name = "Екатерина "
        bot.send_message(message.chat.id, my_name * 5)

    elif message.text == "4 пункт":
        bot.send_message(message.chat.id, text="Задание: спросите у пользователя его имя")
        punkt_4(bot, message.chat.id, message)

    elif message.text == "4.2 пункт":
        bot.send_message(message.chat.id, text="Задание: спросите у пользователя его возраст")
        punkt_4_2(bot, message.chat.id, message)

    elif message.text == "5 пункт":
        bot.send_message(message.chat.id,
                         text="Задание: Преобразуйте возраст в число. В зависимости от возраста сделайте разные варианты ответов")
        punkt_5(bot, message.chat.id, message)

    elif message.text == "6 пункт":
        bot.send_message(message.chat.id, text="Задание: преобразования имени пользователя")
        punkt_6(bot, message.chat.id, message)

    elif message.text == "7 пункт":
        bot.send_message(message.chat.id, text="Задание: математическая задача")
        punkt_7(bot, message.chat.id, message)

def punkt_4(bot, chat_id, message):
    bot.send_message(chat_id, 'Ваше имя?')
    bot.register_next_step_handler(message, get_user_name, bot)


def punkt_4_2(bot, chat_id, message):
    bot.send_message(chat_id, 'Ваш возраст?')
    bot.register_next_step_handler(message, get_user_age, bot)


def punkt_5(bot, chat_id, message):
    bot.send_message(chat_id, 'Ваш возраст?')
    bot.register_next_step_handler(message, age_proverka, bot)


def punkt_6(bot, chat_id, message):
    bot.send_message(chat_id, 'Ваше имя?')
    bot.register_next_step_handler(message, name_chast, bot)


def punkt_7(bot, chat_id, message):
    bot.send_message(chat_id, 'Сколько будет 2+2?')
    bot.register_next_step_handler(message, zadacha, bot)


def zadacha(message, bot):
    if message.text == "4":
        bot.send_message(message.chat.id, "правильно")
    else:
        bot.send_message(message.chat.id, "неправильно")


def age_proverka(message, bot):
    try:
        age = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Используйте цифры для ввода возраста")
    else:
        if 150 > age >= 18:
            bot.send_message(message.chat.id, f'Тебе {age} лет. Ты совершеннолетний')
        elif 18 > age > 0:
            bot.send_message(message.chat.id, f'Тебе {age} лет. Ты несовершеннолетний')
        else:
            bot.send_message(message.chat.id, f'Введите корректный возраст')


def name_chast(message, bot):
    name = message.text
    if not name.isalpha():
        bot.send_message(message.chat.id, 'Используйте буквы'), exit(0)
    kol = len(message.text)
    bot.send_message(message.chat.id, f"задом наперед: {name[::-1]}")
    if kol >= 3:
        bot.send_message(message.chat.id, f"от второго до предпоследнего: {name[1:kol - 1]}")
        bot.send_message(message.chat.id, f"последние 3 символа: {name[kol - 3:kol]}")
    if kol >= 5:
        bot.send_message(message.chat.id, f"первые 5 символов: {name[:5]}")
    bot.send_message(message.chat.id, f"количество букв: {kol}")
    bot.send_message(message.chat.id, f"большие буквы: {name.upper()}")
    bot.send_message(message.chat.id, f"маленькие буквы: {name.lower()}")


def get_user_name(message, bot):
    name = message.text
    bot.send_message(message.chat.id, f'Привет, {name}. Рад тебя видеть.')


def get_user_age(message, bot):
    age = message.text
    bot.send_message(message.chat.id, f'Тебе {age} лет')
