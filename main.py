from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import logging
import os
import json

API_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
BALANCE_FILE = "balances.json"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

def load_balances():
    try:
        with open(BALANCE_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_balances(data):
    with open(BALANCE_FILE, "w") as f:
        json.dump(data, f)

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.reply("Salam! Link göndərin və ya /balans yazaraq balansınızı yoxlayın.")

@dp.message_handler(commands=['balans'])
async def check_balance(message: types.Message):
    user_id = str(message.from_user.id)
    balances = load_balances()
    balance = balances.get(user_id, 0)
    await message.reply(f"Sizin balansınız: {balance:.2f} AZN")

@dp.message_handler(commands=['plus'])  # Admin üçün balans artırma (məs: /plus 123456789 2.5)
async def add_balance(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        parts = message.text.split()
        target_id = parts[1]
        amount = float(parts[2])
        balances = load_balances()
        balances[target_id] = balances.get(target_id, 0) + amount
        save_balances(balances)
        await message.reply(f"{target_id} üçün {amount} AZN əlavə olundu.")
    except:
        await message.reply("İstifadə: /plus [user_id] [məbləğ]")

@dp.message_handler()
async def handle_link(message: types.Message):
    if message.text and message.text.startswith("http"):
        user_id = str(message.from_user.id)
        balances = load_balances()
        user_balance = balances.get(user_id, 0)

        price = 0.5  # sabit qiymət, gələcəkdə linkə görə dəyişə bilər

        if user_balance >= price:
            balances[user_id] -= price
            save_balances(balances)
            await bot.send_message(ADMIN_ID, f"Yeni sifariş gəldi:\nLink: {message.text}\nİstifadəçi: @{message.from_user.username} ({user_id})\nQiymət: {price} AZN")
            await message.reply("Sifariş qəbul edildi! Fayl hazırlanacaq.")
        else:
            await message.reply(f"Balansınız kifayət etmir. Lazım olan: {price} AZN. Mövcud: {user_balance:.2f} AZN")
    else:
        await message.reply("Zəhmət olmasa link göndərin.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
