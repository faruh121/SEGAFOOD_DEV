import asyncio 
import sqlite3 
from aiogram import Bot, Dispatcher 
from aiogram.types import Message, CallbackQuery 
from aiogram.filters import Command 
from aiogram.utils.keyboard import InlineKeyboardBuilder 
# Токен бота 
BOT_TOKEN = "8198367761:AAGAuZTsAK03Zori95Lxv36uhuMjSCis3mA"   
# Инициализация бота и диспетчера 
bot = Bot(token=BOT_TOKEN) 
dp = Dispatcher() 
# Подключение к базе данных 
conn = sqlite3.connect("shop.db") 
cursor = conn.cursor() 
# Создание таблиц (если их ещё нет) 
cursor.execute(""" 
CREATE TABLE IF NOT EXISTS users ( 
    user_id INTEGER PRIMARY KEY, 
    role TEXT DEFAULT 'buyer'  -- 'admin', 'seller', 'buyer' 
) 
""") 
cursor.execute(""" 
CREATE TABLE IF NOT EXISTS menu ( 
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    name TEXT NOT NULL, 
    price_500g REAL NOT NULL, 
    price_100g REAL NOT NULL 
) 
""") 
conn.commit() 
# Инициализация меню 
def initialize_menu(): 
    menu_data = [ 
        {"name": "Чебуреки с говядиной", "price_500g": 280, "price_100g": 56}, 
        {"name": "Чебуреки с курицей", "price_500g": 260, "price_100g": 52}, 
        {"name": "Манты с говядиной", "price_500g": 330, "price_100g": 66}, 
        {"name": "Манты говядина с тыквой", "price_500g": 300, "price_100g": 60}, 
        {"name": "Манты мясо с картошкой", "price_500g": 300, "price_100g": 60}, 
        {"name": "Тефтели говядина", "price_500g": 350, "price_100g": 70}, 
        {"name": "Голубцы", "price_500g": 350, "price_100g": 70}, 
        {"name": "Долма", "price_500g": 380, "price_100g": 76}, 
        {"name": "Самса говядина", "price_500g": 370, "price_100g": 74}, 
        {"name": "Самса с курицей", "price_500g": 340, "price_100g": 68}, 
        {"name": "Хинкали говядина", "price_500g": 350, "price_100g": 70}, 
        {"name": "Хинкали говядина свинина", "price_500g": 330, "price_100g": 66}, 
        {"name": "Вареники с картошкой", "price_500g": 240, "price_100g": 48}, 
        {"name": "Вареники с творогом", "price_500g": 250, "price_100g": 50}, 
        {"name": "Вареники с капустой", "price_500g": 250, "price_100g": 50}, 
        {"name": "Пельмени с курицей", "price_500g": 310, "price_100g": 62}, 
        {"name": "Пельмени с говядиной", "price_500g": 350, "price_100g": 70}, 
        {"name": "Блины", "price_500g": 200, "price_100g": 40}, 
        {"name": "Блины с творогом", "price_500g": 350, "price_100g": 70}, 
        {"name": "Блины с джемом", "price_500g": 390, "price_100g": 78}, 
        {"name": "Блины с мясом", "price_500g": 350, "price_100g": 70}, 
        {"name": "Блины с варёной сгущёнкой", "price_500g": 350, "price_100g": 70}, 
        {"name": "Пирожки с картошкой", "price_500g": 300, "price_100g": 60}, 
        {"name": "Пирожки с луком и яйцом", "price_500g": 350, "price_100g": 70}, 
        {"name": "Пирожки с мясом", "price_500g": 350, "price_100g": 70}, 
    ] 
    cursor.executemany(""" 
    INSERT OR IGNORE INTO menu (name, price_500g, price_100g) VALUES (?, ?, ?) 
    """, [(item["name"], item["price_500g"], item["price_100g"]) for item in menu_data]) 
    conn.commit() 
# Вызов функции при запуске программы (один раз) 
initialize_menu() 
# Добавить пользователя в базу при первом запуске 
def add_user(user_id, role="buyer"): 
    cursor.execute("INSERT OR IGNORE INTO users (user_id, role) VALUES (?, ?)", (user_id, role)) 
    conn.commit() 
# Проверить роль пользователя 
def get_user_role(user_id): 
    cursor.execute("SELECT role FROM users WHERE user_id = ?", (user_id,)) 
    result = cursor.fetchone() 
    return result[0] if result else None 
# Команда /set_admin 
@dp.message(Command("set_admin")) 
async def set_admin_handler(message: Message): 
    role = get_user_role(message.from_user.id) 
    if role != "admin": 
        await message.answer("У вас нет прав для выполнения этого действия!") 
        return 
    # Проверяем, что в сообщении есть ID пользователя 
    if len(message.text.split()) != 2: 
        await message.answer("Используйте формат: /set_admin <user_id>") 
        return 
    user_id = int(message.text.split()[1]) 
    cursor.execute("INSERT OR IGNORE INTO users (user_id, role) VALUES (?, 'admin')", (user_id,)) 
    conn.commit() 
    await message.answer(f"Пользователь с ID {user_id} теперь является администратором.") 
# Команда /start 
@dp.message(Command("start")) 
async def start_handler(message: Message): 
    add_user(message.from_user.id)  # Добавляем пользователя в базу 
    role = get_user_role(message.from_user.id) 
    if role == "admin": 
        await message.answer("Вы вошли как админ. Выберите действие:", reply_markup=create_admin_menu()) 
    elif role == "seller": 
        await message.answer("Вы вошли как продавец. Ожидайте уведомлений о заказах.") 
    else: 
        await message.answer("Добро пожаловать! Выберите действие:", reply_markup=create_main_menu()) 
# Главное меню покупателя 
def create_main_menu(): 
    builder = InlineKeyboardBuilder() 
    builder.button(text="📋 Меню", callback_data="menu") 
    builder.button(text="🛒 Корзина", callback_data="cart") 
    return builder.as_markup() 
# Меню админа 
def create_admin_menu(): 
    builder = InlineKeyboardBuilder() 
    builder.button(text="➕ Добавить товар", callback_data="add_item") 
    builder.button(text="📝 Удалить товар", callback_data="delete_item") 
    builder.button(text="👥 Управление пользователями", callback_data="manage_users") 
    builder.button(text="📋 Посмотреть меню", callback_data="menu") 
    return builder.as_markup() 
# Меню пользователя 
@dp.callback_query(lambda call: call.data == "menu") 
async def show_menu(call: CallbackQuery): 
    items = get_menu() 
    if not items: 
        await call.message.edit_text("Меню пусто.") 
        return 
    text = "📋 *Меню:*\n\n" 
    builder = InlineKeyboardBuilder() 
    for item in items: 
        text += f"{item[1]} - {item[2]} руб/500г ({item[3]} руб/100г)\n" 
        builder.button(text=f"Выбрать: {item[1]}", callback_data=f"item_{item[0]}") 
    builder.button(text="⬅ Назад", callback_data="main_menu") 
    await call.message.edit_text(text, parse_mode="Markdown", reply_markup=builder.as_markup()) 
# Админ добавляет товар 
@dp.callback_query(lambda call: call.data == "add_item") 
async def add_item_handler(call: CallbackQuery): 
    role = get_user_role(call.from_user.id) 
    if role != "admin": 
        await call.answer("У вас нет прав для выполнения этого действия!", show_alert=True) 
        return 
    await call.message.answer("Введите данные для нового товара в формате:\n\nНазвание;Цена за 500г;Цена за 100г") 
@dp.message() 
async def process_admin_input(message: Message): 
    role = get_user_role(message.from_user.id) 
    if role == "admin" and ";" in message.text: 
        try: 
            name, price_500g, price_100g = message.text.split(";") 
            add_menu_item(name.strip(), float(price_500g), float(price_100g)) 
            await message.answer(f"Товар {name.strip()} успешно добавлен в меню.") 
        except ValueError: 
            await message.answer("Ошибка! Убедитесь, что формат правильный: Название;Цена за 500г;Цена за 100г") 
# Удаление товара (админ) 
@dp.callback_query(lambda call: call.data == "delete_item") 
async def delete_item_handler(call: CallbackQuery): 
    role = get_user_role(call.from_user.id) 
    if role != "admin": 
        await call.answer("У вас нет прав для выполнения этого действия!", show_alert=True) 
        return 
    items = get_menu() 
    if not items: 
        await call.message.edit_text("Меню пусто.") 
        return 
    builder = InlineKeyboardBuilder() 
    for item in items: 
        builder.button(text=f"Удалить: {item[1]}", callback_data=f"delete_{item[0]}") 
    builder.button(text="⬅ Назад", callback_data="main_menu") 
    await call.message.edit_text("Выберите товар для удаления:", reply_markup=builder.as_markup()) 
@dp.callback_query(lambda call: call.data.startswith("delete_")) 
async def delete_item_confirm(call: CallbackQuery): 
    role = get_user_role(call.from_user.id) 
    if role != "admin": 
        await call.answer("У вас нет прав для выполнения этого действия!", show_alert=True) 
        return 
    item_id = int(call.data.split("_")[1]) 
    delete_menu_item(item_id) 
    await call.message.edit_text("Товар успешно удалён.") 
# Получить всё меню 
def get_menu(): 
    cursor.execute("SELECT * FROM menu") 
    return cursor.fetchall() 
# Добавить новый товар 
def add_menu_item(name, price_500g, price_100g): 
    cursor.execute("INSERT INTO menu (name, price_500g, price_100g) VALUES (?, ?, ?)", (name, price_500g, price_100g)) 
    conn.commit() 
# Удалить товар из меню 
def delete_menu_item(item_id): 
    cursor.execute("DELETE FROM menu WHERE id = ?", (item_id,)) 
    conn.commit() 
# Запуск бота 
async def main(): 
    print("Бот запущен...") 
    await dp.start_polling(bot) 
if __name__ == "__main__": 
    asyncio.run(main())