from string import Template

import telebot
from telebot import types

bot = telebot.TeleBot('2037001514:AAGj5hIXM7nrsKd_2H6PKqBsGowFhWpzypE')


class User:
    def __init__(self, name):
        self.name = name
        data = ['fullname', 'age', 'phoneNumber', 'event']
        for d in data:
            self.d = None


@bot.message_handler(commands=['start'])
def start_message(msg):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    about = types.KeyboardButton('/about')
    reg = types.KeyboardButton('/reg')
    info = types.KeyboardButton('/info')
    markup.add(about, reg, info)
    bot.send_message(msg.chat.id, 'Добро пожаловать', reply_markup=markup)


@bot.message_handler(commands=['about'])
def about_message(msg):
    bot.send_message(msg.chat.id, "О нас: TODO.")

user_dict = {}

@bot.message_handler(commands=['reg'])
def reg_message(msg):
    question = 'Приступим к регистрации! Вас зовут ' \
               + msg.from_user.first_name + ' ' \
               + msg.from_user.last_name + '?'
    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')
    keyboard.add(key_yes)
    key_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(key_no)
    bot.send_message(msg.chat.id, text=question, reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: True)
    def callback_worker(call):
        if call.data == "yes":
            chat_id = msg.chat.id
            user_dict[chat_id] = User(msg.from_user.first_name + ' ' + msg.from_user.last_name)
            bot.send_message(msg.chat.id, "Сколько вам лет?")
            bot.register_next_step_handler(msg, get_age)
        else:
            bot.send_message(msg.chat.id, "А как тогда?")
            bot.register_next_step_handler(msg, get_name)


def get_name(msg):
    chat_id = msg.chat.id
    user_dict[chat_id] = User(msg.text)
    bot.send_message(msg.chat.id, "Сколько вам лет?")
    bot.register_next_step_handler(msg, get_age)

def get_age(msg):
    try:
        user = user_dict[msg.chat.id]
        user.age = int(msg.text)
        if user.age < 0 or user.age > 120:
            msg = bot.send_message(msg.chat.id, 'Некорректный возраст')
        else:
            msg = bot.send_message(msg.chat.id, 'Ваш номер телефона:')
            bot.register_next_step_handler(msg, get_phone)

    except ValueError:
        msg = bot.send_message(msg.chat.id, 'Цифрами, пожалуйста')
        bot.register_next_step_handler(msg, get_age)
    except KeyError:
        bot.send_message(msg.chat.id, 'Ошибка регистрации, начните заново /reg')


def get_phone(msg):
    try:
        user=user_dict[msg.chat.id]
        user.phoneNumber = int(msg.text)

        msg = bot.send_message(msg.chat.id, 'Регистрация прошла успешно')
    except ValueError:
        msg = bot.send_message(msg.chat.id, 'Неверный номер телефона')
        bot.register_next_step_handler(msg, get_phone)
    except KeyError:
        bot.send_message(msg.chat.id, 'Ошибка регистрации, начните заново /reg')


def getData(user, title):
    t = Template('*$title* \nИмя: *$name* \nВозраст: *$age* \nНомер телефона: *$phoneNumber*')
    return t.substitute({
        'title': title,
        'name': user.name,
        'age': user.age,
        'phoneNumber': user.phoneNumber
    })

@bot.message_handler(commands=['info'])
def info_message(msg):
    try:
        user = user_dict[msg.chat.id]
        bot.send_message(msg.chat.id, getData(user,'Ваши данные: '),parse_mode="Markdown")

    except Exception:
        bot.send_message(msg.chat.id, 'Вы еще не зарегистрированы, напишите /reg')


@bot.message_handler(content_types=['text'])
def get_text_messages(msg):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    about = types.KeyboardButton('/about')
    start = types.KeyboardButton('/start')
    markup.add(start, about)
    bot.send_message(msg.chat.id, 'хей', reply_markup=markup)


bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()

bot.polling(none_stop=True)
