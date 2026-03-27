import telebot
import time
from flask import Flask
from threading import Thread
import random

# --- CONFIGURATION ---
TOKEN = "8666581687:AAEeAyy33mjDhgdKQ-SY2uyrlURhC5YHCsc"
bot = telebot.TeleBot(TOKEN)
app = Flask('')

# Fake Database
users = {}

# --- CORE LOGIC ---

def check_penalty(uid):
    """Calculates and applies the 8-hour inactivity penalty."""
    now = time.time()
    last_active = users[uid]['last_active']
    hours_passed = (now - last_active) / 3600

    if hours_passed > 8:
        penalty_count = int(hours_passed // 8)
        reduction = users[uid]['balance'] * (0.10 * penalty_count)
        users[uid]['balance'] -= reduction
        users[uid]['last_active'] = now
        return round(reduction, 2)
    return 0

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if uid not in users:
        users[uid] = {'balance': 0.0, 'last_active': time.time()}
    
    welcome_text = (
        "🏠 WRLDSCTT TRON BOT\n\n"
        "Commands:\n"
        "/deposit - Add funds (Min 10 TRX)\n"
        "/balance - Check your wallet\n"
        "/gamble - Bet $2.00 on a dice roll\n\n"
        "⚠️ Warning: 10% penalty every 8 hours of inactivity!"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['balance'])
def balance(message):
    uid = message.from_user.id
    if uid not in users:
        return bot.reply_to(message, "Please type /start first.")
    
    penalty = check_penalty(uid)
    msg = f"💰 Balance: ${users[uid]['balance']:.2f}"
    if penalty > 0:
        msg += f"\n⚠️ Inactivity Penalty applied: -${penalty}"
    bot.reply_to(message, msg)

@bot.message_handler(commands=['deposit'])
def deposit(message):
    uid = message.from_user.id
    if uid not in users: users[uid] = {'balance': 0.0, 'last_active': time.time()}
    
    # Simulating a deposit for testing
    users[uid]['balance'] += 10.0
    users[uid]['last_active'] = time.time()
    bot.reply_to(message, "✅ Test Deposit of $10.00 successful!")

@bot.message_handler(commands=['gamble'])
def gamble(message):
    uid = message.from_user.id
    if uid not in users or users[uid]['balance'] < 2:
        return bot.reply_to(message, "❌ Insufficient funds (Need $2.00)")

    users[uid]['balance'] -= 2.0
    users[uid]['last_active'] = time.time()
    
    roll = random.randint(1, 6)
    if roll >= 4:
        users[uid]['balance'] += 4.0
        bot.reply_to(message, f"🎲 You rolled a {roll}. YOU WIN $4.00! 🎉")
    else:
        bot.reply_to(message, f"🎲 You rolled a {roll}. You lost $2.00. Try again!")

# --- KEEP-ALIVE SYSTEM ---

@app.route('/')
def home():
    return "WRLDSCTT Bot Online"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

if __name__ == "__main__":
    keep_alive()
    print("Bot is running...")
    bot.infinity_polling()
