import telebot
import sqlite3

from telebot import types
from config import token

bot = telebot.TeleBot(token)

# База данных блюд
dishes_db = {
    "breakfast": ["Омлет", "Каша", "Бутерброды"],
    "lunch": ["Суп", "Плов", "Гречка с курицей"],
    "dinner": ["Салат", "Рыба", "Овощное рагу"]
}

# Главное меню с инлайн-кнопками
def show_main_menu(chat_id, message_id=None):
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("Выбрать блюдо", callback_data="choose_meal"),
        types.InlineKeyboardButton("Список всех блюд", callback_data="all_dishes")
    )
    markup.add(types.InlineKeyboardButton("Помощь", callback_data="help"))
    
    if message_id:
        try:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="Главное меню:",
                reply_markup=markup
            )
        except:
            bot.send_message(chat_id, "Главное меню:", reply_markup=markup)
    else:
        bot.send_message(chat_id, "Главное меню:", reply_markup=markup)

# Обработка команды /start
@bot.message_handler(commands=['start'])
def start(message):
    show_main_menu(message.chat.id)

# Обработка фотографий
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "Это выглядит аппетитно 😊")

# Меню выбора приема пищи
def show_meal_types(chat_id, message_id=None):
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("Завтрак", callback_data="breakfast"),
        types.InlineKeyboardButton("Обед", callback_data="lunch"),
        types.InlineKeyboardButton("Ужин", callback_data="dinner")
    )
    markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="back_to_main"))
    
    send_message(chat_id, message_id, "Выберите тип приёма пищи:", markup)

# Меню категорий для списка блюд
def show_categories_menu(chat_id, message_id=None):
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("Завтрак", callback_data="list_breakfast"),
        types.InlineKeyboardButton("Обед", callback_data="list_lunch"),
        types.InlineKeyboardButton("Ужин", callback_data="list_dinner")
    )
    markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="back_to_main"))
    
    send_message(chat_id, message_id, "Выберите категорию для просмотра блюд:", markup)

# Список блюд с кнопками управления
def show_dishes_list(chat_id, meal_type, message_id=None, additional_text=None):
    dishes = "\n".join(f"• {dish}" for dish in dishes_db[meal_type])
    text = f"🍽️ Блюда ({meal_type}):\n{dishes}"
    if additional_text:
        text = f"{additional_text}\n\n{text}"
    
    markup = types.InlineKeyboardMarkup()
    # Основные действия в одном ряду
    markup.row(
        types.InlineKeyboardButton("➕ Добавить", callback_data=f"add_{meal_type}"),
        types.InlineKeyboardButton("➖ Удалить", callback_data=f"del_{meal_type}")
    )
    # Кнопка возврата к категориям
    markup.add(types.InlineKeyboardButton("◀️ К категориям", callback_data="back_to_categories"))
    
    send_message(chat_id, message_id, text, markup)

# Универсальная функция отправки сообщения
def send_message(chat_id, message_id, text, markup):
    try:
        if message_id:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                reply_markup=markup
            )
        else:
            bot.send_message(chat_id, text, reply_markup=markup)
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")
        bot.send_message(chat_id, text, reply_markup=markup)

# Добавление блюда
def add_dish(message, meal_type):
    if message.text.lower() == 'отмена':
        show_dishes_list(message.chat.id, meal_type, message.message_id - 1, "Добавление отменено")
        return
    
    dish = message.text.strip()
    if dish in dishes_db[meal_type]:
        show_dishes_list(message.chat.id, meal_type, message.message_id - 1, f"Блюдо '{dish}' уже есть в списке!")
    else:
        dishes_db[meal_type].append(dish)
        show_dishes_list(message.chat.id, meal_type, message.message_id - 1, f"Блюдо '{dish}' добавлено в '{meal_type}'!")

# Обработка callback-запросов
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    try:
        bot.answer_callback_query(call.id)
        
        if call.data == "back_to_main":
            show_main_menu(call.message.chat.id, call.message.message_id)
        elif call.data == "back_to_categories":
            show_categories_menu(call.message.chat.id, call.message.message_id)
        elif call.data == "choose_meal":
            show_meal_types(call.message.chat.id, call.message.message_id)
        elif call.data == "all_dishes":
            show_categories_menu(call.message.chat.id, call.message.message_id)
        elif call.data == "help":
            markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("◀️ Назад", callback_data="back_to_main"))
            send_message(call.message.chat.id, call.message.message_id, 
                       "📌 Помощь:\n\n1. Выберите 'Выбрать блюдо' для выбора по категориям\n2. Используйте 'Список всех блюд' для просмотра и управления\n3. Добавляйте свои блюда или удаляйте существующие", 
                       markup)
        elif call.data in ["breakfast", "lunch", "dinner"]:
            bot.send_message(call.message.chat.id, f"Вы выбрали {call.data}!")
        elif call.data.startswith("list_"):
            show_dishes_list(call.message.chat.id, call.data.split("_")[1], call.message.message_id)
        elif call.data.startswith("add_"):
            msg = bot.send_message(
                call.message.chat.id,
                f"Введите название блюда для добавления в '{call.data.split('_')[1]}':\n(Отправьте 'отмена' для отмены)",
                reply_markup=types.ForceReply()
            )
            bot.register_next_step_handler(msg, lambda m: add_dish(m, call.data.split('_')[1]))
        elif call.data.startswith("del_"):
            meal_type = call.data.split("_")[1]
            if not dishes_db[meal_type]:
                show_dishes_list(call.message.chat.id, meal_type, call.message.message_id, "Список блюд пуст!")
                return
                
            markup = types.InlineKeyboardMarkup()
            for dish in dishes_db[meal_type]:
                markup.add(types.InlineKeyboardButton(f"❌ {dish}", callback_data=f"confirm_del_{meal_type}_{dish}"))
            markup.add(
                types.InlineKeyboardButton("◀️ Назад", callback_data=f"list_{meal_type}"),
                types.InlineKeyboardButton("🏠 В главное меню", callback_data="back_to_main")
            )
            send_message(call.message.chat.id, call.message.message_id, "Выберите блюдо для удаления:", markup)
        elif call.data.startswith("confirm_del_"):
            _, _, meal_type, dish = call.data.split("_", 3)
            dishes_db[meal_type].remove(dish)
            show_dishes_list(call.message.chat.id, meal_type, call.message.message_id, f"Блюдо '{dish}' удалено!")
            
    except Exception as e:
        print(f"Ошибка: {e}")
        bot.send_message(call.message.chat.id, "Произошла ошибка, попробуйте еще раз")

bot.polling(non_stop=True)