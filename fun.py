# ======================================= Развлечения
import requests
import bs4
from telebot import types
from io import BytesIO
import random
import SECRET  # секретные ключи, пароли


# -----------------------------------------------------------------------
def get_text_messages(bot, cur_user, message):
    chat_id = message.chat.id

    if message.text == "Прислать собаку":
        bot.send_photo(chat_id, photo=get_dogURL(), caption="Вот тебе собака!")

    elif message.text == "Прислать лисичку":
        contents = requests.get('https://randomfox.ca/floof/').json()
        urlFox = contents['image']
        bot.send_photo(message.chat.id, photo=urlFox, caption="Вот тебе лисичка!")

    elif message.text == "Прислать анекдот":
        bot.send_message(message.chat.id, text=get_anekdot())

    elif message.text == "Прислать фильм":
        send_film(bot, chat_id)


    elif message.text == "Прислать предпросмотр сайта":
        bot.send_message(message.chat.id, text="Отправьте ссылку")
        bot.register_next_step_handler(message, send_preview_site, bot)

    elif message.text == "Прислать новость":
        news_text = random.choice(get_random_news_from_yandex())
        bot.send_message(message.chat.id, news_text)

    elif message.text == "Угадай кто?":
        get_ManOrNot(bot, chat_id)

    elif message.text == "Прислать курсы":
        bot.send_message(chat_id, text=get_cur())


def send_film(bot, chat_id):
    film = get_randomFilm()
    info_str = f"<b>{film['Наименование']}</b>\n" \
               f"Год: {film['Год']}\n" \
               f"Страна: {film['Страна']}\n" \
               f"Жанр: {film['Жанр']}\n" \
               f"Продолжительность: {film['Продолжительность']}"
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text="Трейлер", url=film["Трейлер_url"])
    btn2 = types.InlineKeyboardButton(text="СМОТРЕТЬ онлайн", url=film["фильм_url"])
    markup.add(btn1, btn2)
    bot.send_photo(chat_id, photo=film['Обложка_url'], caption=info_str, parse_mode='HTML', reply_markup=markup)


# -----------------------------------------------------------------------
def send_preview_site(message, bot):
    link = message.text
    site_preview = get_link_preview(link)
    if site_preview:
        info_str = f"<b>{site_preview['Заголовок']}</b>\n" \
                   f"Описание: {site_preview['Описание']}\n"
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(text="Перейти", url=site_preview["Ссылка"])
        markup.add(btn1)
        bot.send_photo(message.chat.id, photo=site_preview['Изображение_url'], caption=info_str, parse_mode='HTML',
                       reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Неверная ссылка')


def get_link_preview(url_get_preview):
    dict_preview_website = {}

    headers = {
        'authority': 'my.linkpreview.net',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,it;q=0.6',
        'cookie': 'app_session=MTY1MjkwMzg1NXxEdi1CQkFFQ180SUFBUkFCRUFBQV9nRWNfNElBQmdaemRISnBibWNNRFFBTGNtVmthWEpsWTNSVlVrd0djM1J5YVc1bkRBTUFBUzhHYzNSeWFXNW5EQWtBQjE5bWJHRnphRjhIVzExMWFXNTBPQW9FQUFKN2ZRWnpkSEpwYm1jTURnQU1jbVZ4ZFdWemRHOXlYMmxrQm5OMGNtbHVad3dXQUJSaVl6VmxZamhqTURrNE1qZzFaR1ZoTUdFNU13WnpkSEpwYm1jTUVRQVBZM1Z5Y21WdWRGOTFjMlZ5WDJsa0JXbHVkRFkwQkFRQV9uUlNCbk4wY21sdVp3d09BQXh6WlhOemFXOXVYMmhoYzJnR2MzUnlhVzVuREJFQUR5UXlZU1F4TUNRMFVIcGhSeTl0TlFaemRISnBibWNNRkFBU1lYVjBhR1Z1ZEdsamFYUjVYM1J2YTJWdUIxdGRkV2x1ZERnS0lnQWdITjRWOHFzd1JKQ3docTg3NXhUSVRsMW4yVi1jSThRRy15ZWQ0MGZWS1kwPXzjIz0QlchXr_CAWy3XYOCmMOuNdpzcjZ6fHB804r-Urg==',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': 'Windows',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36'
    }
    try:
        url = 'https://my.linkpreview.net/'

        # отправить запрос
        req_link_get = requests.get(url, headers=headers)

        req_link_get_text = req_link_get.text
        #
        # print(req_link)
        # создать переменную для передачи информации в bs4
        soup_get = bs4.BeautifulSoup(req_link_get_text, 'html.parser')
        # print(soup)
        token = soup_get.find('input').get('value')
        # print(token)
        payload = {'authenticity_token': token, 'try_url': url_get_preview}
        req_post = requests.post(url, data=payload, headers=headers)

        req_post_text = req_post.text

        soup_post = bs4.BeautifulSoup(req_post_text, 'html.parser')
        # print(soup)
        section_to_get = soup_post.find("div", class_="box m-4")
        # print(section_to_get)

        try:
            img_to_get = section_to_get.find("figure", class_="image mb-2").find("img").get('src')
            # print(img_to_get)
        except:
            img_to_get = 'Image is not present'

        wrapper_text = section_to_get.find("div", class_="content is-clipped").find_all(class_="mb-2")
        # print(wrapper_text[0].text)

        title = wrapper_text[0].text
        description = wrapper_text[1].text

        link = wrapper_text[1].find_next("small", class_="has-text-grey").text
        # print(link)
        # print(f'My title {title}, my description {description}, my link {link}, my img {img_to_get}')

        dict_preview_website['Заголовок'] = title
        dict_preview_website['Описание'] = description
        dict_preview_website['Ссылка'] = link
        dict_preview_website['Изображение_url'] = img_to_get
    except:
        return None
    else:
        return dict_preview_website


# -----------------------------------------------------------------------
def get_dogURL():
    url = ""
    req = requests.get('https://random.dog/woof.json')
    if req.status_code == 200:
        r_json = req.json()
        url = r_json['url']
    return url


# -----------------------------------------------------------------------
def get_anekdot():
    array_anekdonts = []
    req_anek = requests.get('http://anekdotme.ru/random')
    if req_anek.status_code == 200:
        soup = bs4.BeautifulSoup(req_anek.text, "html.parser")
        result_find = soup.select('.anekdot_text')
        for result in result_find:
            array_anekdonts.append(result.getText().strip())
    if len(array_anekdonts) > 0:
        return array_anekdonts[0]
    else:
        return ""


# -----------------------------------------------------------------------
def get_random_news_from_yandex():
    array_news = []
    req_yandex_news = requests.get('https://yandex.ru')
    soup = bs4.BeautifulSoup(req_yandex_news.text, "html.parser")
    result_find = soup.find_all('span', class_='news__item-content')
    for result in result_find:
        array_news.append(result.getText().strip())
    return array_news


# -----------------------------------------------------------------------
def get_ManOrNot(bot, chat_id):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text="Проверить",
                                      url="https://vc.ru/dev/58543-thispersondoesnotexist-sayt-generator-realistichnyh-lic")
    markup.add(btn1)

    req = requests.get("https://thispersondoesnotexist.com/image", allow_redirects=True)
    if req.status_code == 200:
        img = BytesIO(req.content)
        bot.send_photo(chat_id, photo=img, reply_markup=markup, caption="Этот человек реален?")


# -----------------------------------------------------------------------
def get_cur_pairs():
    lst_cur_pairs = []
    req_currency_list = requests.get(f'https://currate.ru/api/?get=currency_list&key={SECRET.CURRATE_RU}')
    if req_currency_list.status_code == 200:
        currency_list_json = req_currency_list.json()
        for pairs in currency_list_json["data"]:
            if pairs[3:] == "RUB":
                lst_cur_pairs.append(pairs)
    return lst_cur_pairs


def get_cur():
    txt_curses = ""
    txt_pairs = ",".join(get_cur_pairs())
    req_currency_rates = requests.get(f'https://currate.ru/api/?get=rates&pairs={txt_pairs}&key={SECRET.CURRATE_RU}')
    if req_currency_rates.status_code == 200:
        currency_rates = req_currency_rates.json()
        for pairs, rates in currency_rates["data"].items():
            txt_curses += f"{pairs} : {rates}\n"
    else:
        txt_curses = req_currency_rates.text
    return txt_curses


# -----------------------------------------------------------------------
def get_randomFilm():
    url = 'https://randomfilm.ru/'

    infoFilm = {}

    req_film = requests.get(url)

    req_film_text = req_film.text

    soup = bs4.BeautifulSoup(req_film_text, "html.parser")

    result_find = soup.find('div', align="center", style="width: 100%")
    infoFilm["Наименование"] = result_find.find("h2").getText()
    names = infoFilm["Наименование"].split(" / ")
    infoFilm["Наименование_rus"] = names[0].strip()
    if len(names) > 1:
        infoFilm["Наименование_eng"] = names[1].strip()

    images = []
    for img in result_find.findAll('img'):
        images.append(url + img.get('src'))
    infoFilm["Обложка_url"] = images[0]

    details = result_find.findAll('td')
    infoFilm["Год"] = details[0].contents[1].strip()
    infoFilm["Страна"] = details[1].contents[1].strip()
    infoFilm["Жанр"] = details[2].contents[1].strip()
    infoFilm["Продолжительность"] = details[3].contents[1].strip()
    infoFilm["Режиссёр"] = details[4].contents[1].strip()
    infoFilm["Актёры"] = details[5].contents[1].strip()
    infoFilm["Трейлер_url"] = url + details[6].contents[0]["href"]
    infoFilm["фильм_url"] = url + details[7].contents[0]["href"]

    return infoFilm
