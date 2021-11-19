import os
from string import Template

import telebot
from dotenv import load_dotenv
from telebot import types

from api import Request

load_dotenv()
BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_URL = os.environ.get("API_URL")
API_TOKEN = os.environ.get('x-api-key')

bot = telebot.TeleBot(BOT_TOKEN)
requestAPI = Request(API_TOKEN, API_URL)

class User:
    def __init__(self, id, name, age = None, phone = None):
        self.id = id
        self.name = name
        self.age = age
        self.phone = phone

texts = {
    "about":'About us 👨🏻‍💻',
    "me":'Me ℹ️',
    "change":'Change 👥',
    "reg":'Register 🐣'
}

def get_markup(chat_id):
    response = requestAPI.getUser(chat_id).json().get('exist')
    if response:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=False)
        about = types.KeyboardButton(texts.get('about'))
        info = types.KeyboardButton(texts.get('me'))
        change = types.KeyboardButton(texts.get('change'))
        markup.add(about, info, change)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=False)
        about = types.KeyboardButton(texts.get('about'))
        reg = types.KeyboardButton(texts.get('reg'))
        markup.add(about, reg)

    return markup

def get_user_from_json(user_json):
    return User(user_json.get('telegramId'), user_json.get('name'), user_json.get('age'), user_json.get('phone'))

def getData(user, title):
    t = Template('*$title* \nName: *$name* \nAge: *$age* \nPhone Number: *$phone*')
    return t.substitute({
        'title': title,
        'name': user.name,
        'age': user.age,
        'phone': user.phone
    })

