from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import json
import sys
import re
import random
import string
import os
import time
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Telegram Bot Token
TELEGRAM_TOKEN = "8406100668:AAEmnwiN6WPBIwwF8ZoeH4b_mSr6xsZzhUU"

# File to store approved users
APPROVED_USERS_FILE = "approved_users.json"

# Banner
bannerss = """
┌────────────────────────────────────────────────────────────────────────────┐
│                                                                            │
│         ██████╗  █████╗ ██████╗ ██╗  ██╗██████╗  ██████╗ ██╗   ██╗         │
│         ██╔══██╗██╔══██╗██╔══██╗██║ ██╔╝██╔══██╗██╔═══██╗╚██╗ ██╔╝         │
│         ██║  ██║███████║██████╔╝█████╔╝ ██████╔╝██║   ██║ ╚████╔╝          │
│         ██║  ██║██╔══██║██╔══██╗██╔═██╗ ██╔══██╗██║   ██║  ╚██╔╝           │
│         ██████╔╝██║  ██║██║  ██║██║  ██╗██████╔╝╚██████╔╝   ██║            │
│         ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝  ╚═════╝    ╚═╝            │
│                                                        Boot Script 2.0     │
└────────────────────────────────────────────────────────────────────────────┘

 | Version: 1.2
PAID VERSION!
"""

# Helper functions for approved users
def load_approved_users():
    try:
        with open(APPROVED_USERS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_approved_users(approved_users):
    with open(APPROVED_USERS_FILE, "w", encoding="utf-8") as file:
        json.dump(approved_users, file, indent=4)

def is_user_approved(chat_id):
    approved_users = load_approved_users()
    if str(chat_id) in approved_users:
        expiration_date = datetime.strptime(approved_users[str(chat_id)], "%Y-%m-%d")
        return datetime.now() < expiration_date
    return False

def approve_user(chat_id, days=30):
    approved_users = load_approved_users()
    expiration_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    approved_users[str(chat_id)] = expiration_date
    save_approved_users(approved_users)

def unapprove_user(chat_id):
    approved_users = load_approved_users()
    if str(chat_id) in approved_users:
        del approved_users[str(chat_id)]
        save_approved_users(approved_users)

# Helper functions for credit card operations
def generate_random_email(length=8, domain=None):
    common_domains = ["gmail.com"]
    if not domain:
        domain = random.choice(common_domains)
    username_characters = string.ascii_letters + string.digits
    username = ''.join(random.choice(username_characters) for _ in range(length))
    return f"{username}@{domain}"

def create_session():
    try:
        session = requests.Session()
        email = generate_random_email()
        headers = {
            'authority': 'www.thetravelinstitute.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'max-age=0',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
        }
        response = session.get('https://www.thetravelinstitute.com/register/', headers=headers, timeout=20)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        nonce = soup.find('input', {'id': 'afurd_field_nonce'})['value']
        noncee = soup.find('input', {'id': 'woocommerce-register-nonce'})['value']
        data = [
            ('afurd_field_nonce', nonce),
            ('_wp_http_referer', '/register/'),
            ('pre_page', ''),
            ('email', email),
            ('password', 'Esahatam2009@'),
            ('register', 'Register'),
        ]
        response = session.post('https://www.thetravelinstitute.com/register/', headers=headers, data=data, timeout=20)
        if response.status_code == 200:
            with open('Creds.txt', 'a', encoding="utf-8") as f:
                f.write(email + ':' + 'Esahatam2009@\n')
            return session
        else:
            return None
    except Exception:
        return None

def manage_session_file():
    session_file = "session.txt"
    if os.path.exists(session_file):
        session = load_session_from_file(session_file)
        if session:
            return session
    session = create_session()
    if session:
        save_session_to_file(session, session_file)
        return session
    return None

def save_session_to_file(session, file_path):
    with open(file_path, "w", encoding="utf-8") as file:
        cookies = session.cookies.get_dict()
        json.dump(cookies, file)

def load_session_from_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            session_data = json.load(file)
            session = requests.Session()
            session.cookies.update(session_data)
            return session
    except Exception:
        return None

def get_bin_info(card_number):
    try:
        bin_number = card_number[:6]
        response = requests.get(f"https://lookup.binlist.net/{bin_number}", headers={"Accept-Version": "3"})
        if response.status_code == 200:
            bin_data = response.json()
            return {
                "type": bin_data.get("type", "UNKNOWN"),
                "bank": bin_data.get("bank", {}).get("name", "UNKNOWN"),
                "country": bin_data.get("country", {}).get("name", "UNKNOWN"),
            }
        else:
            return {"type": "UNKNOWN", "bank": "UNKNOWN", "country": "UNKNOWN"}
    except Exception:
        return {"type": "UNKNOWN", "bank": "UNKNOWN", "country": "UNKNOWN"}

# --------- Credit Card Checking & Formatting Functions ---------
# (same as your original code; logic unchanged)
# ... code for check_credit_cards, format_response, generate_cc, generate_ccs, check_vbv ...

# Telegram Bot Handlers
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("""Welcome to the Ultimate CC Checker Bot!

✨ Features:
• Check a single card using /chk <CC|MM|YY|CVV>
• Generate 10 random cards with /gen <6-digit BIN>
• Mass check multiple cards (approved users only) with /mass
• VBV Check using /vbv <CC|MM|YY|CVV>

🔒 Mass Command Access:
Only approved users can access the mass checking feature.

💡 Admin Commands:
Use /approve <chatid> [days] and /unapprove <chatid> to manage approvals.

Enjoy using the bot and happy checking! 🚀""")

# In all handlers, replace chat_id = update.message.chat_id with:
# chat_id = update.effective_chat.id

# Remaining handlers (chk, mass, handle_file, approve, unapprove, vbv, gen)
# logic same as original code; just minor fixes for chat_id and string quotes

def main() -> None:
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    # ... add other handlers same as original code ...

    application.run_polling()

if __name__ == "__main__":
    main()
