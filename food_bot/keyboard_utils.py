from telebot import types
from database import Database

db = Database()

def create_main_menu():
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("🍳 Выбрать блюдо", callback_data="choose_meal"),
        types.InlineKeyboardButton("📋 Список блюд", callback_data="all_dishes")
    )
    markup.row(types.InlineKeyboardButton("ℹ️ Помощь", callback_data="help"))
    return markup

def create_categories_menu(menu_type="list"):
    markup = types.InlineKeyboardMarkup()
    categories = db.get_all_categories()

    for category_id, name in categories:
        if menu_type == "random":
            callback_data = f"random_{category_id}"
        else:
            callback_data = f"list_{category_id}"
        markup.add(types.InlineKeyboardButton(name, callback_data=callback_data))

    markup.add(types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_main"))
    return markup

def create_dishes_menu(category_id: int):
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("➕ Добавить", callback_data=f"add_{category_id}"),
        types.InlineKeyboardButton("➖ Удалить", callback_data=f"del_{category_id}")
    )
    markup.add(types.InlineKeyboardButton("🔙 К категориям", callback_data="back_to_categories"))
    return markup

def create_delete_menu(dishes, category_id: int):
    markup = types.InlineKeyboardMarkup()
    for dish_id, dish_name in dishes:
        markup.add(types.InlineKeyboardButton(
            f"❌ {dish_name}",
            callback_data=f"confirm_del_{category_id}_{dish_id}"
        ))
    markup.add(types.InlineKeyboardButton(
        "🔙 Назад",
        callback_data=f"list_{category_id}"
    ))
    return markup

def create_random_dish_menu(category_id: int):
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("🎲 Ещё раз", callback_data=f"random_{category_id}"),
        types.InlineKeyboardButton("📋 Все блюда", callback_data=f"list_{category_id}")
    )
    markup.row(types.InlineKeyboardButton("🔙 К категориям", callback_data="choose_meal"))
    return markup
