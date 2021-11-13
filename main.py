from string import Template
from dotenv import load_dotenv
import os
import telebot
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

    # def __init__(self, id, name):
    #     self.id = id
    #     self.name = name
    #     data = ['id', 'name', 'age', 'phone']
    #     for d in data:
    #         self.d = None

# response = requestAPI.postUser("13", 'awd1', 21, "dqwdqwda1s")
# print(response)
# response = requestAPI.getUser(13)
# print(response)
# response = requestAPI.changeUser(13, 'adw1', 31 ,'2131321312')
# print(requestAPI.getUser(13))
# response = requestAPI.removeUser(13)
# print(response)

def get_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=False)
    about = types.KeyboardButton('About 👨🏻‍💻')
    info = types.KeyboardButton('You ℹ️')
    # reg = types.KeyboardButton('Register 🐣')
    markup.add(about, info)
    return markup

@bot.message_handler(commands=['start'])
def start_message(msg):
    bot.send_message(msg.chat.id, 'Welcome', reply_markup=get_markup())

@bot.message_handler(regexp='About 👨🏻‍💻')
def about_message(msg):
    bot.send_message(msg.chat.id, "TODO")

user_dict = {}

@bot.message_handler(commands=['change'])
def change_info_message(msg):
    return None

@bot.message_handler(commands=['reg'])
@bot.message_handler(regexp='Register 🐣')
def reg_message(msg):
    keyboard= types.ReplyKeyboardRemove()
    bot.send_message(msg.chat.id, 'Great', reply_markup=keyboard)
    question = 'Is your name ' + msg.from_user.full_name + '?'
    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text='Yes', callback_data='yes')
    keyboard.add(key_yes)
    key_no = types.InlineKeyboardButton(text='No', callback_data='no')
    keyboard.add(key_no)
    bot.send_message(msg.chat.id, text=question, reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: call.message.chat.id == msg.chat.id)
    def callback_worker(call):
        chat_id = call.message.chat.id
        if call.data == "yes":
            bot.edit_message_text(text=question, chat_id=chat_id, message_id=call.message.message_id, reply_markup=None)
            user_dict[chat_id] = User(chat_id, msg.from_user.full_name)
            bot.send_message(chat_id, "How old are you?")
            bot.register_next_step_handler(msg, get_age)
        else:
            bot.edit_message_text(text=question, chat_id=chat_id, message_id=call.message.message_id, reply_markup=None)
            bot.send_message(chat_id, "How then?")
            bot.register_next_step_handler(msg, get_name)


def get_name(msg):
    chat_id = msg.chat.id
    user_dict[chat_id] = User(chat_id, msg.text)
    bot.send_message(chat_id, "How old are you?")
    bot.register_next_step_handler(msg, get_age)


def get_age(msg):
    try:
        if msg.text != '/stop':
            user = user_dict[msg.chat.id]
            user.age = int(msg.text)
            if user.age < 0 or user.age > 120:
                msg = bot.send_message(user.id, 'Incorrect age')
                bot.register_next_step_handler(msg, get_age)
            else:
                phone_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                req_button = types.KeyboardButton(text="Send please your phone number", request_contact=True)
                phone_keyboard.add(req_button)
                msg = bot.send_message(user.id, 'Your phone number', reply_markup=phone_keyboard)
                bot.register_next_step_handler(msg, get_phone)

    except ValueError:
        msg = bot.send_message(user.id, 'Numbers, please. To cancel registration press /stop')
        bot.register_next_step_handler(msg, get_age)
    except KeyError:
        bot.send_message(user.id, 'Registration fail, to start again press /reg')


def get_phone(msg):
    if msg.text != '/stop':
        try:
            user = user_dict[msg.chat.id]
            user.phone = msg.contact.phone_number
            response = requestAPI.postUser(str(user.id), user.name, user.age, user.phone)
            print(response)
            if response == 500:
                bot.send_message(user.id, 'You have already registered', reply_markup=get_markup())
            else:
                bot.send_message(user.id, 'Registration was successful', reply_markup=get_markup())
        except (ValueError, AttributeError):
            msg = bot.send_message(user.id, 'Incorrect phone number. To cancel registration press /stop')
            bot.register_next_step_handler(msg, get_phone)
        except KeyError:
            bot.send_message(user.id, 'Registration fail, to start again press /reg')
    else:
        bot.send_message(msg.chat.id, 'Registration was stopped', reply_markup=get_markup())


def getData(user, title):
    t = Template('*$title* \nName: *$name* \nAge: *$age* \nPhone Number: *$phone*')
    return t.substitute({
        'title': title,
        'name': user.name,
        'age': user.age,
        'phone': user.phone
    })

def get_user_from_json(user_json):
    return User(user_json.get('telegramId'), user_json.get('name'), user_json.get('age'), user_json.get('phone'))

@bot.message_handler(regexp='You ℹ️')
def info_message(msg):
    try:
        user_json = requestAPI.getUser(str(msg.chat.id))
        user = get_user_from_json(user_json)
        bot.send_message(user.id, getData(user, 'Your info: '), parse_mode="Markdown")

    except ValueError:
        bot.send_message(msg.chat.id, 'You are not registered yet, press /reg')

@bot.message_handler(content_types=['text'])
def get_text_messages(msg):
    bot.send_message(msg.chat.id, 'Hey', reply_markup=get_markup())


# bot.enable_save_next_step_handlers(delay=2)
# bot.load_next_step_handlers()

bot.polling(none_stop=True)
