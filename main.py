import requests
import telebot
from telebot import types
import config

bot = telebot.TeleBot("5506282306:AAFlnSIDFjswf_5OObeVzAXtAINcQPM2NHs")


@bot.message_handler(commands=["start"])
def start_bot(message):
    bot.send_message(message.from_user.id, "привет!")

    login = message.from_user.id
    url = config.url + "/start"

    data = {
        "login": login
    }

    requests.post(url, json=data)


@bot.message_handler(commands=["help"])
def send_help(message):
    bot.send_message(message.from_user.id, "/news - вывод пяти последних новостей из подписанных категорий \n/sub - "
                                           "подписаться на категорию \nunsub - отписаться от категории \nsubs - "
                                           "посмотреть подписки ")


@bot.message_handler(commands=["sub"])
def sub_on_category(message):
    categories = requests.post(config.url + "/sub/markup_info")
    markup = types.ReplyKeyboardMarkup()

    if categories is not None:
        for category in categories.json():
            markup.add(types.KeyboardButton(f"{category['name']}"))
    bot.send_message(message.from_user.id, "выберите категорию, на которую хотите подписаться", reply_markup=markup)

    bot.register_next_step_handler(message, subscribe_user)


def subscribe_user(message):
    login = message.from_user.id
    url = config.url + "/sub/to_sub"

    data = {
        "login": login,
        "category": message.text
    }

    result = requests.post(url, json=data)
    bot.send_message(message.from_user.id, result.json()["result_text"])


@bot.message_handler(commands=["unsub"])
def unsub_on_category(message):
    login = message.from_user.id
    url = config.url + "/unsub"

    data = {
        "login": login
    }

    sub_categories = requests.post(url, json=data)

    markup = types.ReplyKeyboardMarkup()

    if sub_categories is not None:
        for category in sub_categories.json():
            markup.add(types.KeyboardButton(category["name"]))

    bot.send_message(message.from_user.id, "выберите категорию, от которой хотите отписаться", reply_markup=markup)

    bot.register_next_step_handler(message, unsubscribe_user)


def unsubscribe_user(message):
    login = message.from_user.id
    url = config.url + "/unsub/to_unsub"

    data = {
        "login": login,
        "category": message.text
    }

    result = requests.post(url, json=data)
    bot.send_message(message.from_user.id, result.json()["result_text"])


@bot.message_handler(commands=["news"])
def send_news(message):
    login = message.from_user.id
    url = config.url + "/news"

    data = {
        "login": login
    }

    sub_categories = requests.post(url, json=data)

    for category in sub_categories.json():
        req = requests.get(f'https://newsapi.org/v2/top-headlines?apiKey={config.api_key}&country=cn&pageSize=3&category={category["name"]}')
        for i in req.json()["articles"]:
            news_list = [[i["title"], i["publishedAt"], i["url"]]]
            print(news_list)
            for new in news_list:
                bot.send_message(message.from_user.id, f"{new[0]} {new[2]}")


bot.infinity_polling()
