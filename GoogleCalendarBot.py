from __future__ import print_function
import datetime
import time

import googleapiclient
from google.oauth2 import service_account
from googleapiclient.discovery import build
from telebot import types
from menuBot import Menu, goto_menu
import calendar


# -----------------------------------------------------------------------
active_calendars = {}  # Тут будем накапливать все активные игры. У пользователя может быть только одна активная игра


def new_calendar_obj(chat_id, new_calendar):
    active_calendars.update({chat_id: new_calendar})
    return new_calendar


def get_calendar_obj(chat_id):
    return active_calendars.get(chat_id, None)


def stop_calendar_obj(chat_id):
    active_calendars.pop(chat_id, None)


# -----------------------------------------------------------------------

SCOPES = ['https://www.googleapis.com/auth/calendar']

calendarId = '459584vphd9b8vu128cp5l44v0@group.calendar.google.com'
SERVICE_ACCOUNT_FILE = 'rosy-pivot-352017-01745d2756ff.json'

# __________________________________________________________________________
dict_months = {
    '01': ' Январь',
    '02': 'Февраль',
    '03': 'Март',
    '04': 'Апрель',
    '05': 'Май',
    '06': 'Июнь',
    '07': 'Июль',
    '08': 'Август',
    '09': 'Сентябрь',
    '10': 'Октябрь',
    '11': 'Ноябрь',
    '12': 'Декабрь',

}


# _____________________________________________________________________________________


class GoogleCalendar(object):

    def __init__(self):
        credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        self.service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)
        self.summary = ""
        self.start_date_year = ""
        self.start_date_month = ""
        self.start_date_day = ""
        self.start_time_hour = ""
        self.start_time_minute = ""

    # создание словаря с информацией о событии
    def create_event_dict(self):
        event = {
            'summary': self.summary,
            'description': '',
            'start': {
                'dateTime': f'{self.start_date_year}-{self.start_date_month}-{self.start_date_day}T{self.start_time_hour}:{self.start_time_minute}:00+03:00',
            },
            'end': {
                'dateTime': f'{self.start_date_year}-{self.start_date_month}-{self.start_date_day}T{self.start_time_hour}:{self.start_time_minute}:01+03:00',

            }
        }
        return event

    # создание события в календаре
    def create_event(self, event):
        e = self.service.events().insert(calendarId=calendarId,
                                         body=event).execute()
        print('Event created: %s' % (e.get('id')))

    # вывод списка из десяти предстоящих событий
    def get_events_list(self, bot, chat_id):
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        print('Getting the upcoming 10 events')
        events_result = self.service.events().list(calendarId=calendarId,
                                                   timeMin=now,
                                                   maxResults=10, singleEvents=True,
                                                   orderBy='startTime').execute()
        events = events_result.get('items', [])
        # events_list = []
        if not events:
            print('No upcoming events found.')
            bot.send_message(chat_id, text="Событий нет")
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
            # events_list.append((start, event['summary']))

            date_of_event = start.split("T")[0]
            time_of_event = start.split("T")[1].split("+")[0]
            bot.send_message(chat_id,
                             text=f"""Дата: {date_of_event}. Время: {time_of_event}. Название: {event['summary']}""")

    def set_summary(self, message, bot):
        ms_text = message.text
        if len(ms_text) > 30:
            ms_text = ms_text[:30]
            bot.send_message(message.chat.id, text="Вы ввели более 30 знаков, название было обрезано")
        self.summary = ms_text
        bot.send_message(message.chat.id, text=f"Установлено название события: {self.summary}")

    def generate_inline_keyboard_month(self):
        keyboard = types.InlineKeyboardMarkup(row_width=4)

        list_btn_of_month = []

        for key, value in dict_months.items():
            print(key)
            print(value)
            btn = types.InlineKeyboardButton(text=value,
                                             callback_data=f"GCal_call_back|sdm+{key}|" + Menu.setExtPar(
                                                 self))

            # каждая кнопка содержит: текст, который показываем пользователю
            # и текст который вернется при нажатии на конкретную кнопку, в строке содежатся значения разделенные по |
            # 1 это название игры, 2 это индекс кнопки, 3 это комбинация цифр uuid4 сделанная из объекта класса
            # пример что вернется при нажатии на кнопку ['GameExtraWord', 'r+0', '8de4d7faa79c4468bfb0ea40bb1b9715']
            list_btn_of_month.append(btn)
            if len(list_btn_of_month) >= 4:
                keyboard.add(*list_btn_of_month)
                list_btn_of_month.clear()

        btn = types.InlineKeyboardButton(text="Выход из этого меню", callback_data="GCal_call_back|Exit")
        keyboard.add(btn)

        return keyboard

    def generate_inline_keyboard_days(self, count_days):
        keyboard = types.InlineKeyboardMarkup(row_width=7)
        list_btn_of_day = []
        for i in range(1, count_days + 1):
            btn = types.InlineKeyboardButton(text=i,
                                             callback_data=f"GCal_call_back|sdd+{i}|" + Menu.setExtPar(
                                                 self))
            list_btn_of_day.append(btn)
            if len(list_btn_of_day) >= 7 or i == count_days:
                keyboard.row(*list_btn_of_day)
                list_btn_of_day.clear()
        print(list_btn_of_day)
        btn = types.InlineKeyboardButton(text="Выход из этого меню", callback_data="GCal_call_back|Exit")
        keyboard.add(btn)

        return keyboard

    def generate_inline_keyboard_time(self, max_value):
        keyboard = types.InlineKeyboardMarkup(row_width=6)
        list_btn_of_min = []
        time_type = ""
        if max_value == 24:
            time_type = 'h'
        elif max_value == 60:
            time_type = 'm'
        for i in range(0, max_value):
            btn = types.InlineKeyboardButton(text=i,
                                             callback_data=f"GCal_call_back|st{time_type}+{i}|" + Menu.setExtPar(
                                                 self))

            list_btn_of_min.append(btn)
            if len(list_btn_of_min) >= 6:
                keyboard.row(*list_btn_of_min)
                list_btn_of_min.clear()
        print(list_btn_of_min)
        btn = types.InlineKeyboardButton(text="Выход из этого меню", callback_data="GCal_call_back|Exit")
        keyboard.add(btn)

        return keyboard

    def generate_inline_keyboard_send_to_calendar(self):
        keyboard = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton(text="Отправить в календарь",
                                         callback_data=f"GCal_call_back|send_c+y|" + Menu.setExtPar(self))

        keyboard.add(btn)
        btn = types.InlineKeyboardButton(text="Выход из этого меню", callback_data="GCal_call_back|Exit")
        keyboard.add(btn)
        return keyboard


def callback_worker_calendar(bot, cur_user, cmd, par, call):
    chat_id = call.message.chat.id
    message_id = call.message.id
    # print(cmd, 'cmd')

    if cmd == "Exit":
        # bot.delete_message(chat_id, message_id)
        goto_menu(bot, chat_id, "Главное меню")
        bot.answer_callback_query(call.id)


    elif "sdy+" in cmd:
        print("вы нажали на год")
        obj_google_calendar = Menu.getExtPar(par)
        if obj_google_calendar is None:  # если наткнулись на кнопку, которой быть не должно - удалим её из чата
            bot.delete_message(chat_id, message_id)
        else:
            choice_year = cmd.split('+')[1]
            obj_google_calendar.start_date_year = choice_year

            chosen_year = obj_google_calendar.start_date_year

            bot.delete_message(chat_id, message_id)
            bot.send_message(chat_id, text=f"Вы выбрали {chosen_year} год")

            keyboard = obj_google_calendar.generate_inline_keyboard_month()
            bot.send_message(chat_id, "Выберите месяц", reply_markup=keyboard)

    elif "sdm+" in cmd:
        # print('мы нажали на месяц')
        obj_google_calendar = Menu.getExtPar(par)
        if obj_google_calendar is None:  # если наткнулись на кнопку, которой быть не должно - удалим её из чата
            bot.delete_message(chat_id, message_id)
        else:
            choice_month = cmd.split('+')[1]
            obj_google_calendar.start_date_month = choice_month

            chosen_month = obj_google_calendar.start_date_month

            bot.delete_message(chat_id, message_id)
            bot.send_message(chat_id, text=f"Вы выбрали {dict_months[chosen_month]} месяц")
            chosen_year = obj_google_calendar.start_date_year
            count_days = calendar.monthrange(int(chosen_year), int(chosen_month))[1]
            print(count_days)

            keyboard = obj_google_calendar.generate_inline_keyboard_days(count_days)
            bot.send_message(chat_id, "Выберите день", reply_markup=keyboard)

    elif "sdd+" in cmd:
        print('мы нажали на день')
        obj_google_calendar = Menu.getExtPar(par)
        if obj_google_calendar is None:  # если наткнулись на кнопку, которой быть не должно - удалим её из чата
            bot.delete_message(chat_id, message_id)
        else:
            choice_day = cmd.split('+')[1]
            obj_google_calendar.start_date_day = choice_day

            chosen_day = obj_google_calendar.start_date_day

            bot.delete_message(chat_id, message_id)
            bot.send_message(chat_id, text=f"Вы выбрали {chosen_day} день")

            keyboard = obj_google_calendar.generate_inline_keyboard_time(24)
            bot.send_message(chat_id, "Выберите час", reply_markup=keyboard)

    elif "sth+" in cmd:
        print('мы нажали на час')
        obj_google_calendar = Menu.getExtPar(par)
        if obj_google_calendar is None:  # если наткнулись на кнопку, которой быть не должно - удалим её из чата
            bot.delete_message(chat_id, message_id)
        else:
            choice_hour = cmd.split('+')[1]
            obj_google_calendar.start_time_hour = choice_hour

            chosen_hour = obj_google_calendar.start_time_hour

            bot.delete_message(chat_id, message_id)
            bot.send_message(chat_id, text=f"Вы выбрали {chosen_hour} час")

            keyboard = obj_google_calendar.generate_inline_keyboard_time(60)
            bot.send_message(chat_id, "Выберите минуту", reply_markup=keyboard)

    elif "stm+" in cmd:
        print('мы нажали на минуту')
        obj_google_calendar = Menu.getExtPar(par)
        if obj_google_calendar is None:  # если наткнулись на кнопку, которой быть не должно - удалим её из чата
            bot.delete_message(chat_id, message_id)
        else:
            choice_minute = cmd.split('+')[1]
            obj_google_calendar.start_time_minute = choice_minute

            chosen_minute = obj_google_calendar.start_time_minute

            bot.delete_message(chat_id, message_id)
            bot.send_message(chat_id, text=f"Вы выбрали {chosen_minute} минуту")

            keyboard = obj_google_calendar.generate_inline_keyboard_send_to_calendar()
            bot.send_message(chat_id, "Нажмите для отправки:", reply_markup=keyboard)

    elif "send_c+" in cmd:
        print('мы нажали на отправить событие')
        obj_google_calendar = Menu.getExtPar(par)
        if obj_google_calendar is None:  # если наткнулись на кнопку, которой быть не должно - удалим её из чата
            bot.delete_message(chat_id, message_id)
        else:
            choice_send = cmd.split('+')[1]
            if choice_send == 'y':
                bot.delete_message(chat_id, message_id)
                # bot.send_message(chat_id, text=f"")

                summary = obj_google_calendar.summary
                start_date_year = obj_google_calendar.start_date_year
                start_date_month = obj_google_calendar.start_date_month
                start_date_day = obj_google_calendar.start_date_day
                start_time_hour = obj_google_calendar.start_time_hour
                start_time_minute = obj_google_calendar.start_time_minute

                print(summary)
                print(start_date_year)
                print(start_date_month)
                print(start_date_day)
                print(start_time_hour)
                print(start_time_minute)

                sending_emoji = u"\U0001F4E9"
                waiting_emoji = u"\U000023F3"
                time_finish = u"\U0000231B"
                success_emoji = u"\U0001F3AF"

                total_message = bot.send_message(chat_id,
                                                 text=f"Происходит отправка в календарь: {sending_emoji} {waiting_emoji}\n\nНазвание события: {summary}.\n\nДата: {start_date_day}/{start_date_month}/{start_date_year}\n\nВремя: {start_time_hour}:{start_time_minute}")
                print(total_message)

                time.sleep(5)
                event = obj_google_calendar.create_event_dict()
                obj_google_calendar.create_event(event)

                bot.edit_message_text(chat_id=chat_id, message_id=total_message.message_id,
                                      text=f"Происходит отправка в календарь: {time_finish}\n\nНазвание события: {summary}.\n\nДата: {start_date_day}/{start_date_month}/{start_date_year}\n\nВремя: {start_time_hour}:{start_time_minute}\n\nУспешно отправлено в календарь {success_emoji}")


def get_text_messages(bot, cur_user, message):
    chat_id = message.chat.id
    ms_text = message.text

    if ms_text == "Добавить событие":

        keyboard = types.InlineKeyboardMarkup()

        calendar_obj = get_calendar_obj(chat_id)
        if calendar_obj is None:  # если мы случайно попали в это меню, а объекта с игрой нет
            goto_menu(bot, chat_id, "Выход")
            return

        bot.send_message(chat_id, text="Введите название")
        bot.register_next_step_handler(message, calendar_obj.set_summary, bot)
        print(calendar_obj.summary)

        while calendar_obj.summary == "":
            pass

        list_of_years = ['2022', '2023', '2024', '2025', '2026']

        for calend_obj in active_calendars.values():
            if type(calend_obj) == GoogleCalendar:
                for item in list_of_years:
                    btn = types.InlineKeyboardButton(text=item,
                                                     callback_data=f"GCal_call_back|sdy+{item}|" + Menu.setExtPar(
                                                         calend_obj))

                    # каждая кнопка содержит: текст, который показываем пользователю
                    # и текст который вернется при нажатии на конкретную кнопку, в строке содежатся значения разделенные по |
                    # 1 это название игры, 2 это индекс кнопки, 3 это комбинация цифр uuid4 сделанная из объекта класса
                    # пример что вернется при нажатии на кнопку ['GameExtraWord', 'r+0', '8de4d7faa79c4468bfb0ea40bb1b9715']

                    keyboard.add(btn)
                btn = types.InlineKeyboardButton(text="Выход из этого меню", callback_data="GCal_call_back|Exit")
                keyboard.add(btn)
                bot.send_message(chat_id, "Выберите год", reply_markup=keyboard)
        print("меню добавить событие")

    elif ms_text == "Посмотреть события":
        print("меню посмотреть события")
        calendar_obj = get_calendar_obj(chat_id)
        if calendar_obj is None:  # если мы случайно попали в это меню, а объекта с игрой нет
            goto_menu(bot, chat_id, "Выход")
            return

        for calend_obj in active_calendars.values():
            if type(calend_obj) == GoogleCalendar:
                calend_obj.get_events_list(bot, chat_id)


    elif ms_text == "Выход":
        goto_menu(bot, chat_id, "Выход")
        return
