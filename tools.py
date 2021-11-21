import datetime
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
    "reg":'Register 🐣',
    "events":'Events 🥳'
}

def get_markup(chat_id):
    response = requestAPI.getUser(chat_id).json().get('exist')
    if response:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=False)
        about = types.KeyboardButton(texts.get('about'))
        info = types.KeyboardButton(texts.get('me'))
        change = types.KeyboardButton(texts.get('change'))
        events = types.KeyboardButton(texts.get('events'))
        markup.add(about, info, change, events)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=False)
        about = types.KeyboardButton(texts.get('about'))
        reg = types.KeyboardButton(texts.get('reg'))
        events = types.KeyboardButton(texts.get('events'))
        markup.add(about, reg, events)

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

def getEvent(event_json):
    t = Template('Name: *$name* \nDate: *$date* \nTime: *$time* \nTickets: *$tickets*')
    date = datetime.datetime.strptime(event_json.get('date'), "%Y-%m-%dT%H:%M:%S.%fZ")
    return t.substitute({
        'name': event_json.get('name'),
        'date': date.strftime('%A %d %B %Y'),
        'time': date.strftime('%H:%M'),
        'tickets': event_json.get('ticketsAmount')
    })

