import telebot
import sqlite3

from telebot import types

from food_bot.config import token

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def start(message):
    # Подключение базы данных
    conn = sqlite3.connect('database_old.sql')
    cur = conn.cursor()

    cur.execute(
        'CREATE TABLE IF NOT EXISTS users (id int auto_increment primary key, name varchar(50), pass varchar(50))')
    conn.commit()
    cur.close()
    conn.close()

    bot.send_message(message.chat.id, 'Происходит регистрация..., Введите логин')
    bot.register_next_step_handler(message, user_name)

    markup = types.ReplyKeyboardMarkup()

    btn_1 = types.KeyboardButton('Выбрать блюдо')
    btn_2 = types.KeyboardButton('Список всех блюд')
    markup.row(btn_1, btn_2)
    btn_3 = types.KeyboardButton('Помощь')
    markup.row(btn_3)

    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}, я бот который поможет тебе выбрать какое блюдо приготовить.', reply_markup=markup)
    bot.register_next_step_handler(message, on_click)

def user_name(message):
    name = message.text.strip()
    bot.send_message(message.chat.id, 'Введите пароль:')
    bot.register_next_step_handler(message, user_pass, name)

def user_pass(message, name):
    password = message.text.strip()

    conn = sqlite3.connect('database.sql')
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO users (name, pass) VALUES('%s', '%s ')" % (name, password))
    conn.commit()
    cur.close()
    conn.close()

    markup = types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton('Список пользователей', callback_data = 'users'))
    bot.send_message(message.chat.id, 'Пользователь зарегистрирован!', reply_markup = markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    conn = sqlite3.connect('database.sql')
    cur = conn.cursor()

    cur.execute(
        'SELECT * FROM users')
    users = cur.fetchall()

    info = ''
    for el in users:
        info += f'Имя: {el[1]}, пароль: {el[2]}\n'

    cur.close()
    conn.close()

    bot.send_message(call.message.chat.id, info)

def on_click(message):
    if message.text == "Список всех блюд":
        bot.send_message(message.chat.id, "Список блюд:")

@bot.message_handler(commands=['help'])
def main(message):
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}, я бот который поможет тебе выбрать какое блюдо приготовить.')


@bot.message_handler()
def info(message):
    bot.send_message(message.chat.id, "Такой команды не существует /help")

bot.polling(non_stop=True)