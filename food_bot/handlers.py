import random
from telebot import types
from telebot.apihelper import ApiTelegramException
from keyboard_utils import (
    create_main_menu,
    create_categories_menu,
    create_dishes_menu,
    create_delete_menu,
    create_random_dish_menu
)
from database import Database

db = Database()

def handle_start(bot, message):
    bot.send_message(message.chat.id, "Главное меню:", reply_markup=create_main_menu())

def handle_help(bot, message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_main"))
    bot.send_message(
        message.chat.id,
        "📌 Помощь:\n\n1. 'Выбрать блюдо' - случайное блюдо из категории\n2. 'Список блюд' - просмотр и управление\n3. Добавляйте/удаляйте блюда",
        reply_markup=markup
    )

def handle_photo(bot, message):
    bot.reply_to(message, "Это выглядит аппетитно 😊")

def handle_add_dish(bot, message, category_id):
    if message.text.lower() == 'отмена':
        dishes = db.get_dishes(get_category_name(category_id))
        dishes_text = "\n".join(f"• {dish[1]}" for dish in dishes) if dishes else "Список пуст"
        bot.send_message(
            message.chat.id,
            f"❌ Добавление отменено\n\n🍽️ Блюда ({get_category_name(category_id)}):\n{dishes_text}",
            reply_markup=create_dishes_menu(category_id)
        )
        return

    dish_name = message.text.strip()
    if not dish_name:
        bot.send_message(message.chat.id, "Название блюда не может быть пустым!")
        return

    if db.add_dish(get_category_name(category_id), dish_name):
        dishes = db.get_dishes(get_category_name(category_id))
        dishes_text = "\n".join(f"• {dish[1]}" for dish in dishes) if dishes else "Список пуст"
        bot.send_message(
            message.chat.id,
            f"✅ Блюдо '{dish_name}' добавлено!\n\n🍽️ Блюда ({get_category_name(category_id)}):\n{dishes_text}",
            reply_markup=create_dishes_menu(category_id)
        )
    else:
        bot.send_message(message.chat.id, f"❌ Блюдо '{dish_name}' уже существует!")

def get_category_name(category_id):
    cursor = db.conn.cursor()
    cursor.execute("SELECT name FROM categories WHERE id = ?", (category_id,))
    return cursor.fetchone()[0]

def get_dish_name(dish_id):
    cursor = db.conn.cursor()
    cursor.execute("SELECT name FROM dishes WHERE id = ?", (dish_id,))
    return cursor.fetchone()[0]

def handle_callback(bot, call):
    bot.answer_callback_query(call.id)
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    if call.data == "back_to_main":
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="🍽️ Главное меню:",
            reply_markup=create_main_menu()
        )

    elif call.data == "back_to_categories":
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="📋 Выберите категорию:",
            reply_markup=create_categories_menu(menu_type="list")
        )

    elif call.data == "choose_meal":
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="🍳 Выберите категорию для случайного блюда:",
            reply_markup=create_categories_menu(menu_type="random")
        )

    elif call.data == "all_dishes":
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="📋 Список блюд по категориям:",
            reply_markup=create_categories_menu(menu_type="list")
        )

    elif call.data.startswith("random_"):
        category_id = int(call.data.split("_")[1])
        category_name = get_category_name(category_id)
        dishes = db.get_dishes(category_name)

        if not dishes:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Назад", callback_data="choose_meal"))
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"🍽️ В категории '{category_name}' пока нет блюд",
                reply_markup=markup
            )
            return

        random_dish = random.choice(dishes)[1]
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"🎲 Случайное блюдо из '{category_name}':\n\n<b>{random_dish}</b>",
            parse_mode="HTML",
            reply_markup=create_random_dish_menu(category_id)
        )

    elif call.data.startswith("list_"):
        category_id = int(call.data.split("_")[1])
        category_name = get_category_name(category_id)
        dishes = db.get_dishes(category_name)
        dishes_text = "\n".join(f"• {dish[1]}" for dish in dishes) if dishes else "Список пуст"
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"🍽️ Блюда ({category_name}):\n{dishes_text}",
            reply_markup=create_dishes_menu(category_id)
        )

    elif call.data.startswith("add_"):
        category_id = int(call.data.split("_")[1])
        msg = bot.send_message(
            chat_id,
            f"Введите название блюда для добавления в '{get_category_name(category_id)}':\n(Для отмены отправьте 'отмена')",
            reply_markup=types.ForceReply()
        )
        bot.register_next_step_handler(msg, lambda m: handle_add_dish(bot, m, category_id))

    elif call.data.startswith("del_"):
        category_id = int(call.data.split("_")[1])
        category_name = get_category_name(category_id)
        dishes = db.get_dishes(category_name)

        if not dishes:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"🍽️ В категории '{category_name}' нет блюд для удаления",
                reply_markup=create_dishes_menu(category_id)
            )
            return

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"Выберите блюдо для удаления из '{category_name}':",
            reply_markup=create_delete_menu(dishes, category_id)
        )

    elif call.data.startswith("confirm_del_"):
        _, _, category_id_str, dish_id_str = call.data.split("_")
        category_id = int(category_id_str)
        dish_id = int(dish_id_str)

        category_name = get_category_name(category_id)
        dish_name = get_dish_name(dish_id)

        if db.remove_dish(category_name, dish_name):
            dishes = db.get_dishes(category_name)
            dishes_text = "\n".join(f"• {dish[1]}" for dish in dishes) if dishes else "Список пуст"
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f"✅ Блюдо '{dish_name}' удалено!\n\n🍽️ Блюда ({category_name}):\n{dishes_text}",
                reply_markup=create_dishes_menu(category_id)
            )
        else:
            bot.answer_callback_query(call.id, f"❌ Не удалось удалить блюдо '{dish_name}'", show_alert=True)

    else:
        bot.answer_callback_query(call.id, "⚠️ Неизвестная команда", show_alert=True)
