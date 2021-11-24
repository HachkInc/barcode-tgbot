import datetime

from telebot import types

from tools import User, get_user_from_json, get_markup, texts, requestAPI, bot, getData, getEvent


@bot.message_handler(commands=['start'])
def start_message(msg):
    bot.send_message(msg.chat.id, 'Welcome', reply_markup=get_markup(msg.chat.id))


@bot.message_handler(regexp=texts.get('about'))
def about_message(msg):
    bot.send_message(msg.chat.id, "TODO")


user_dict = {}

queryHandlerId=0

@bot.message_handler(regexp=texts.get('change'))
def change_info_message(msg):
    keyboard = types.ReplyKeyboardRemove()
    bot.send_message(msg.chat.id, 'Changing the info', reply_markup=keyboard)
    keyboard = types.InlineKeyboardMarkup()
    key_name = types.InlineKeyboardButton(text='Name', callback_data='name')
    keyboard.add(key_name)
    key_age = types.InlineKeyboardButton(text='Age', callback_data='age')
    keyboard.add(key_age)
    key_exit = types.InlineKeyboardButton(text='Cancel', callback_data='exit')
    keyboard.add(key_exit)
    question = 'What do you want to change?'
    bot.send_message(msg.chat.id, question, reply_markup=keyboard)
    @bot.callback_query_handler(func=lambda call: call.message.chat.id == msg.chat.id)
    def callback_worker(call):
        chat_id = call.message.chat.id
        bot.edit_message_text(text=question, chat_id=chat_id, message_id=call.message.message_id, reply_markup=None)
        user = get_user_from_json(requestAPI.getUser(str(chat_id)).json().get('user'))
        if call.data == 'name':
            bot.send_message(chat_id, "What is your new name? or /stop")
            bot.register_next_step_handler(msg, change_name, user)
        elif call.data == 'age':
            bot.send_message(chat_id, "What is your age? or /stop")
            bot.register_next_step_handler(msg, change_age, user)
        elif call.data == 'exit':
            bot.send_message(chat_id, 'Exiting the change form', reply_markup=get_markup(chat_id))


def change_name(msg, user):
    if msg.text != '/stop':
        requestAPI.changeUser(user.id, msg.text, user.age, user.phone)
        bot.send_message(msg.chat.id, 'Your name has been changed', reply_markup=get_markup(user.id))
    else:
        bot.send_message(msg.chat.id, 'Your name has not been changed', reply_markup=get_markup(user.id))


def change_age(msg, user):
    if msg.text != '/stop':
        try:
            requestAPI.changeUser(user.id, user.name, int(msg.text), user.phone)
            bot.send_message(msg.chat.id, 'Your age has been changed', reply_markup=get_markup(user.id))
        except ValueError:
            msg = bot.send_message(user.id, 'Numbers, please. To cancel registration press /stop')
            bot.register_next_step_handler(msg, change_age, user)
    else:
        bot.send_message(msg.chat.id, 'Your age has not been changed', reply_markup=get_markup(user.id))


@bot.message_handler(commands=['reg'])
@bot.message_handler(regexp=texts.get('reg'))
def reg_message(msg):
    keyboard = types.ReplyKeyboardRemove()
    bot.send_message(msg.chat.id, 'Great', reply_markup=keyboard)
    question = 'Is your name ' + msg.from_user.full_name + '?'
    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text='Yes', callback_data='yes1')
    keyboard.add(key_yes)
    key_no = types.InlineKeyboardButton(text='No', callback_data='no1')
    keyboard.add(key_no)
    bot.send_message(msg.chat.id, text=question, reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: call.message.chat.id == msg.chat.id)
    def callback_worker(call):
        chat_id = call.message.chat.id
        if call.data == "yes1":
            bot.edit_message_text(text=question, chat_id=chat_id, message_id=call.message.message_id, reply_markup=None)
            user_dict[chat_id] = User(chat_id, msg.from_user.full_name)
            bot.send_message(chat_id, "How old are you?")
            bot.register_next_step_handler(msg, get_age)
        elif call.data == 'no1':
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
                bot.send_message(user.id, 'You have already registered', reply_markup=get_markup(msg.chat.id))
            else:
                bot.send_message(user.id, 'Registration was successful', reply_markup=get_markup(msg.chat.id))
        except (ValueError, AttributeError):
            msg = bot.send_message(user.id, 'Incorrect phone number. To cancel registration press /stop')
            bot.register_next_step_handler(msg, get_phone)
        except KeyError:
            bot.send_message(user.id, 'Registration fail, to start again press /reg')
    else:
        bot.send_message(msg.chat.id, 'Registration was stopped', reply_markup=get_markup(msg.chat.id))


@bot.message_handler(regexp=texts.get('me'))
def info_message(msg):
    try:
        user_json = requestAPI.getUser(str(msg.chat.id)).json().get('user')
        user = get_user_from_json(user_json)
        bot.send_message(user.id, getData(user, 'Your info: '), parse_mode="Markdown")
    except Exception:
        bot.send_message(msg.chat.id, 'You are not registered yet, press /reg')


def get_next_events(keyboard, i):
    response = requestAPI.getEvents().json()
    key_first = types.InlineKeyboardButton(text=response.get('results')[i].get('name'),
                                           callback_data='first')
    keyboard.add(key_first)
    if response.get('count') != i+1:
        key_second = types.InlineKeyboardButton(text=response.get('results')[i + 1].get('name'),
                                                callback_data='second')
        keyboard.add(key_second)
    key_next = types.InlineKeyboardButton(text='Next', callback_data='next')
    keyboard.add(key_next)
    key_prev = types.InlineKeyboardButton(text='Prev', callback_data='prev')
    keyboard.add(key_prev)
    return keyboard


@bot.message_handler(regexp=texts.get('events'))
def get_events(msg):
    response = requestAPI.getEvents()
    keyboard = types.ReplyKeyboardRemove()
    bot.send_message(msg.chat.id, 'Great', reply_markup=keyboard)
    question = 'What event do you want to go?'
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    page = 0
    get_next_events(keyboard, page)
    bot.send_message(msg.chat.id, text=question, reply_markup=keyboard)
    @bot.callback_query_handler(func=lambda call: call.message.chat.id == msg.chat.id)
    def callback_worker(call):
        nonlocal page
        chat_id = call.message.chat.id
        if call.data == 'first':
            bot.edit_message_text(text=question, chat_id=chat_id, message_id=call.message.message_id, reply_markup=None)
            temp = page
            page = 0
            register_to_event(msg, response.json().get('results')[temp].get('id'))
            # bot.send_message(msg.chat.id, getEvent(response.json().get('results')[page]), parse_mode="Markdown")
        elif call.data == 'second':
            bot.edit_message_text(text=question, chat_id=chat_id, message_id=call.message.message_id, reply_markup=None)
            temp = page
            page = 0
            register_to_event(msg, response.json().get('results')[temp + 1].get('id'))
            # bot.send_message(msg.chat.id, getEvent(response.json().get('results')[page + 1]), parse_mode="Markdown")
        elif call.data == 'next':
            if page + 2 < response.json().get('count'):
                page += 2
                keyboard = types.InlineKeyboardMarkup(row_width=2)
                bot.edit_message_text(text=question, chat_id=chat_id, message_id=call.message.message_id,
                                      reply_markup=get_next_events(keyboard, page))
        elif call.data == 'prev':
            if page - 2 >= 0:
                keyboard = types.InlineKeyboardMarkup(row_width=2)
                page -= 2
                bot.edit_message_text(text=question, chat_id=chat_id, message_id=call.message.message_id,
                                      reply_markup=get_next_events(keyboard, page))


def register_to_event(msg, eventId):
    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text='Yes', callback_data='yes')
    keyboard.add(key_yes)
    key_no = types.InlineKeyboardButton(text='No', callback_data='no')
    keyboard.add(key_no)
    response = requestAPI.getEventById(eventId)
    bot.send_message(msg.chat.id, getEvent(response.json()), parse_mode="Markdown")
    question = 'Do you want to register to this event?'
    bot.send_message(msg.chat.id, text=question , reply_markup=keyboard)
    @bot.callback_query_handler(func=lambda call: call.message.chat.id == msg.chat.id)
    def callback_worker(call):
        chat_id = call.message.chat.id
        bot.edit_message_text(text=question, chat_id=call.message.chat.id, message_id=call.message.message_id,
                              reply_markup=None)
        if call.data == 'yes':
            bot.send_message(msg.chat.id, "ok")
        elif call.data == 'no':
            # bot.edit_message_text(text=question, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
            bot.send_message(msg.chat.id, "not ok")

@bot.message_handler(content_types=['text'])
def get_text_messages(msg):
    bot.send_message(msg.chat.id, 'Hey, go to the menu or press any of these buttons 😊\n⬇️',
                     reply_markup=get_markup(msg.chat.id))


# bot.enable_save_next_step_handlers(delay=2)
# bot.load_next_step_handlers()

bot.polling(none_stop=True)
