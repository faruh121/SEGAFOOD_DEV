import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Токен бота
BOT_TOKEN = "8198367761:AAGAuZTsAK03Zori95Lxv36uhuMjSCis3mA"

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Глобальные переменные
ADMIN_ID = 1186792039  # ID администратора
users = {}  # Данные пользователей {user_id: {"role": "buyer/seller/admin", "name": "", "contact": ""}}
menu =  menu_data = [ 
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
seller_id = None  # ID продавца, который будет получать уведомления


# Команда /start
@dp.message(Command("start"))
async def start_handler(message: Message):
    user_id = message.from_user.id
    if user_id not in users:
        role = "admin" if user_id == ADMIN_ID else "buyer"  # Назначаем администратора по умолчанию
        users[user_id] = {"role": role, "name": "", "contact": ""}
    role = users[user_id]["role"]

    if role == "admin":
        await message.answer("Вы вошли как администратор. Выберите действие:", reply_markup=create_admin_menu())
    elif role == "seller":
        await message.answer("Вы вошли как продавец. Ожидайте уведомлений о заказах.")
    else:
        await message.answer("Добро пожаловать! Выберите действие:", reply_markup=create_main_menu())


# Главное меню
def create_main_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="🍽️ Посмотреть меню", callback_data="menu")
    builder.button(text="📞 Оставить контакт", callback_data="set_contact")
    return builder.as_markup()


# Администраторское меню
def create_admin_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="📋 Посмотреть меню", callback_data="menu")
    builder.button(text="➕ Добавить товар", callback_data="add_item")
    builder.button(text="📝 Удалить товар", callback_data="delete_item")
    builder.button(text="👥 Назначить продавца", callback_data="set_seller")
    return builder.as_markup()


# Кнопки меню
def create_menu_keyboard():
    builder = InlineKeyboardBuilder()
    for index, item in enumerate(menu):
        builder.adjust(1)
        builder.button(
            text=f"{item['name']} ({item['price_100g']} руб/100г)",
            callback_data=f"order_{index}"
        )
    builder.button(text="⬅️ Назад", callback_data="main_menu")
    return builder.as_markup()

@dp.callback_query(lambda call: call.data == "menu")
async def show_menu(call: CallbackQuery):
    await call.message.edit_text("📋 *Меню товаров:*\nВыберите нужный товар из списка:", 
                                 parse_mode="Markdown", 
                                 reply_markup=create_menu_keyboard())


# Возврат в главное меню
@dp.callback_query(lambda call: call.data == "main_menu")
async def main_menu_handler(call: CallbackQuery):
    role = users[call.from_user.id]["role"]
    if role == "admin":
        await call.message.edit_text("Вы вернулись в администраторское меню:", reply_markup=create_admin_menu())
    else:
        await call.message.edit_text("Вы вернулись в главное меню:", reply_markup=create_main_menu())


# Обработка заказа
@dp.callback_query(lambda call: call.data.startswith("order_"))
async def order_handler(call: CallbackQuery):
    index = int(call.data.split("_")[1])
    item = menu[index]
    user_id = call.from_user.id

    if not users[user_id]["contact"]:
        await call.message.answer("⚠️ Пожалуйста, оставьте свои контактные данные командой /set_contact, чтобы сделать заказ.")
        return

    contact = users[user_id]["contact"]
    seller_message = f"🛒 *Новый заказ!*\n\n" \
                     f"📦 Товар: {item['name']}\n" \
                     f"💰 Цена за 100г: {item['price_100g']} руб\n\n" \
                     f"👤 Покупатель:\n" \
                     f"Имя: {users[user_id]['name']}\n" \
                     f"Контакт: {contact}"

    if seller_id:
        await bot.send_message(chat_id=seller_id, text=seller_message, parse_mode="Markdown")
        await call.message.answer("✅ Ваш заказ отправлен продавцу. Ожидайте подтверждения!")
    else:
        await call.message.answer("⚠️ Продавец пока не назначен. Попробуйте позже.")


# Установка контакта пользователя
@dp.callback_query(lambda call: call.data == "set_contact")
async def set_contact_handler(call: CallbackQuery):
    await call.message.answer("Введите ваши контактные данные (например, Имя и телефон):")


@dp.message()
async def save_contact(message: Message):
    user_id = message.from_user.id
    if user_id in users and not users[user_id]["contact"]:
        users[user_id]["name"] = message.text.split()[0]
        users[user_id]["contact"] = message.text
        await message.answer("✅ Контактные данные сохранены! Теперь вы можете заказывать товары.")
    else:
        await message.answer("Ваши данные уже сохранены или вы не зарегистрированы.")


# Администратор добавляет товар
@dp.callback_query(lambda call: call.data == "add_item")
async def add_item_handler(call: CallbackQuery):
    if users[call.from_user.id]["role"] != "admin":
        await call.answer("У вас нет прав для выполнения этого действия!", show_alert=True)
        return
    await call.message.answer("Введите данные нового товара в формате:\n`Название;Цена за 500г;Цена за 100г`", parse_mode="Markdown")


@dp.message()
async def process_new_item(message: Message):
    if users[message.from_user.id]["role"] == "admin" and ";" in message.text:
        try:
            name, price_500g, price_100g = message.text.split(";")
            menu.append({"name": name.strip(), "price_500g": float(price_500g), "price_100g": float(price_100g)})
            await message.answer(f"✅ Товар {name.strip()} успешно добавлен в меню.")
        except ValueError:
            await message.answer("Ошибка! Убедитесь, что формат правильный: Название;Цена за 500г;Цена за 100г")


# Администратор удаляет товар
@dp.callback_query(lambda call: call.data == "delete_item")
async def delete_item_handler(call: CallbackQuery):
    if users[call.from_user.id]["role"] != "admin":
        await call.answer("У вас нет прав для выполнения этого действия!", show_alert=True)
        return

    builder = InlineKeyboardBuilder()
    for index, item in enumerate(menu):
        builder.button(text=f"Удалить: {item['name']}", callback_data=f"delete_{index}")
    builder.button(text="🔙 Вернуться", callback_data="main_menu")

    await call.message.edit_text("Выберите товар для удаления:", reply_markup=builder.as_markup())


@dp.callback_query(lambda call: call.data.startswith("delete_"))
async def confirm_delete_item(call: CallbackQuery):
    if users[call.from_user.id]["role"] != "admin":
        await call.answer("У вас нет прав для выполнения этого действия!", show_alert=True)
        return

    index = int(call.data.split("_")[1])
    item = menu.pop(index)
    await call.message.edit_text(f"✅ Товар '{item['name']}' успешно удалён.")


# Назначение продавца
@dp.callback_query(lambda call: call.data == "set_seller")
async def set_seller_handler(call: CallbackQuery):
    if users[call.from_user.id]["role"] != "admin":
        await call.answer("У вас нет прав для выполнения этого действия!", show_alert=True)
        return
    await call.message.answer("Введите ID пользователя, которого хотите назначить продавцом:")


@dp.message()
async def process_set_seller(message: Message):
    if users[message.from_user.id]["role"] == "admin":
        try:
            global seller_id
            seller_id = int(message.text)
            if seller_id not in users:
                users[seller_id] = {"role": "seller", "name": "", "contact": ""}
            else:
                users[seller_id]["role"] = "seller"
            await message.answer(f"✅ Пользователь с ID {seller_id} назначен продавцом.")
        except ValueError:
            await message.answer("Ошибка! Убедитесь, что вы ввели корректный ID.")


# Запуск бота
async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
@dp.message(Command("info"))
async def info_handler(message: Message):
    commands_list = """
📋 *Список доступных команд:*
/start - Начать работу с ботом
/info - Показать список всех команд
/set_admin <ID> - Назначить пользователя администратором (только для админа)
/set_seller <ID> - Назначить пользователя продавцом (только для админа)
/set_buyer <ID> - Назначить пользователя покупателем (только для админа)
/menu - Показать меню
/contact - Оставить контактные данные
"""
    await message.answer(commands_list, parse_mode="Markdown")
