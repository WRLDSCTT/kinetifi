import telebot
import time
from flask import Flask
from threading import Thread
import random

# --- CONFIGURATION ---
TOKEN = "YOUR_BOT_TOKEN_FROM_BOTFATHER"
bot = telebot.TeleBot(TOKEN)
app = Flask('')

# Fake Database (Resets if bot restarts - use a file/db for permanent storage later)
users = {} 

# --- CORE LOGIC ---

def check_penalty(uid):
    """Calculates and applies the 8-hour inactivity penalty."""
    now = time.time()
    last_active = users[uid]['last_active']
    hours_passed = (now - last_active) / 3600
    
    if hours_passed > 8:
        # 10% penalty for every 8-hour block missed
        penalty_count = int(hours_passed // 8)
        reduction = users[uid]['balance'] * (0.10 * penalty_count)
        users[uid]['balance'] -= reduction
        users[uid]['last_active'] = now # Reset timer after penalty
        return round(reduction, 2)
    return 0

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if uid not in users:
        users[uid] = {'balance': 0.0, 'last_active': time.time()}
    bot.reply_to(message, "🏦 WRLDSCTT TRON BOT\n\nCommands:\n/deposit - Add funds (Min $10)\n/balance - Check wallet\n/gamble - Bet $2 on a dice roll")

@bot.message_handler(commands=['balance'])
def balance(message):
    uid = message.from_user.id
    penalty = check_penalty(uid)
    msg = f"💰 Balance: ${users[uid]['balance']:.2f}"
    if penalty > 0:
        msg += f"\n⚠️ Inactivity Penalty applied: -${penalty}"
    bot.reply_to(message, msg)

@bot.message_handler(commands=['deposit'])
def deposit(message):
    uid = message.from_user.id
    # TESTING MODE: Just giving $10 credit. 
    # Real version would require a TRX Hash check.
    users[uid]['balance'] += 10.0
    users[uid]['last_active'] = time.time()
    bot.reply_to(message, "✅ Successfully deposited $10.00 (Test Credit).\nYour timer has been reset.")

@bot.message_handler(commands=['gamble'])
def gamble(message):
    uid = message.from_user.id
    
    # Check Minimum Requirement
    if users[uid]['balance'] < 2.0:
        return bot.reply_to(message, "❌ Insufficient balance! Minimum bet is $2.")
    
    # Check Penalty first
    penalty = check_penalty(uid)
    if penalty > 0:
        bot.send_message(message.chat.id, f"⚠️ Penalty for 8h inactivity: -${penalty}")

    # The Gamble (Dice)
    msg = bot.send_dice(message.chat.id)
    dice_value = msg.dice.value
    time.sleep(3) # Wait for animation

    if dice_value >= 4:
        users[uid]['balance'] += 2.0
        bot.reply_to(message, f"🎯 WIN! You rolled a {dice_value}.\n+$2.00 added to balance.")
    else:
        users[uid]['balance'] -= 2.0
        bot.reply_to(message, f"💀 LOSS. You rolled a {dice_value}.\n-$2.00 removed from balance.")
    
    users[uid]['last_active'] = time.time() # Activity resets the 8-hour clock

# --- KEEP-ALIVE SYSTEM ---
@app.route('/')
def home(): return "WRLDSCTT Bot Online"

def run(): app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(non_stop=True)
