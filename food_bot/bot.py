import telebot
from config import TOKEN
from handlers import handle_start, handle_help, handle_photo, handle_callback

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    handle_start(bot, message)

@bot.message_handler(func=lambda msg: msg.text == "Помощь")
def help(message):
    handle_help(bot, message)

@bot.message_handler(content_types=['photo'])
def photo(message):
    handle_photo(bot, message)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    handle_callback(bot, call)

if __name__ == '__main__':
    print("Бот запущен...")
    bot.polling(none_stop=True)