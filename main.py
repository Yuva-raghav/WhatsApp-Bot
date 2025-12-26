# main.py
import json
import gspread
import os
from google.oauth2.service_account import Credentials
from typing import Dict

# ---------------- CONFIG ----------------
SPREADSHEET_ID = "1WeAySjhKMjq97tefVxLIZd3NJRTmacFVhfaSBTyXA7Q"
WORKSHEET_NAME = "Sheet1"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
# --------------------------------------

# ========== MENU DATA ==========
OILS_MENU = {
    "1": "Groundnut Oil",
    "2": "Coconut Oil",
    "3": "Sunflower Oil",
    "4": "Sesame Oil"
}

SNACKS_MENU = {
    "1": "Murukulu",
    "2": "Chekkalu",
    "3": "Mixture",
    "4": "Boondi"
}

# ========== SESSION STORAGE ==========
sessions: Dict[str, Dict] = {}


# ========== GOOGLE SHEETS ==========
def get_sheet():
    """
    Local → uses service_account.json
    Render → uses GOOGLE_CREDENTIALS_JSON
    """
    creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")

    # Production (Render)
    if creds_json:
        creds = Credentials.from_service_account_info(
            json.loads(creds_json),
            scopes=SCOPES
        )
    # Local development
    else:
        creds = Credentials.from_service_account_file(
            "service_account.json",
            scopes=SCOPES
        )

    client = gspread.authorize(creds)
    return client.open_by_key(SPREADSHEET_ID).worksheet(WORKSHEET_NAME)


def save_order(data: Dict):
    sheet = get_sheet()
    sheet.append_row([
        data.get("category", ""),
        data.get("item", ""),
        data.get("quantity", ""),
        data.get("name", ""),
        data.get("mobile", ""),
        data.get("address", "")
    ])


# ========== BOT LOGIC ==========
def bot_reply(user_id: str, message: str) -> str:
    message = message.lower().strip()

    # 🔹 GLOBAL GREETING / RESET (FIX)
    if message in ["hi", "hii", "hello", "hey", "start"]:
        sessions[user_id] = {"step": "category"}
        return (
            "👋 Hello! Welcome to Home Made Foods 😊\n\n"
            "Please choose one option:\n"
            "1️⃣ Oils\n"
            "2️⃣ Snacks\n\n"
            "✍️ Reply with 1 or 2"
        )

    if user_id not in sessions:
        sessions[user_id] = {"step": "category"}

    session = sessions[user_id]

    # STEP 1: Category
    if session["step"] == "category":
        if message in ["1", "oils"]:
            session["category"] = "Oils"
            session["menu"] = OILS_MENU
        elif message in ["2", "snacks"]:
            session["category"] = "Snacks"
            session["menu"] = SNACKS_MENU
        else:
            return "❌ Invalid choice. Reply with 1 (Oils) or 2 (Snacks)."

        session["step"] = "item"

        menu_text = "\n".join(
            [f"{k}️⃣ {v}" for k, v in session["menu"].items()]
        )

        return (
            f"🛒 *{session['category']} Menu*\n\n"
            f"{menu_text}\n\n"
            "✍️ Please reply with item number"
        )

    # STEP 2: Item selection
    if session["step"] == "item":
        menu = session["menu"]

        if message not in menu:
            return "❌ Invalid item. Please select from the list."

        session["item"] = menu[message]
        session["step"] = "quantity"

        return (
            f"📦 You selected *{session['item']}*.\n"
            "Enter quantity (e.g., 1 kg / 2 liters)"
        )

    # STEP 3: Quantity
    if session["step"] == "quantity":
        session["quantity"] = message
        session["step"] = "name"
        return "👤 Please enter your name"

    # STEP 4: Name
    if session["step"] == "name":
        session["name"] = message.title()
        session["step"] = "mobile"
        return "📞 Please enter your mobile number"

    # STEP 5: Mobile
    if session["step"] == "mobile":
        if not message.isdigit() or len(message) < 10:
            return "❌ Please enter a valid 10-digit mobile number"
        session["mobile"] = message
        session["step"] = "address"
        return "🏠 Please enter your delivery address"

    # STEP 6: Address + Save
    if session["step"] == "address":
        session["address"] = message.title()

        save_order(session)
        sessions.pop(user_id, None)

        return (
            "✅ *Order Confirmed!*\n\n"
            "📦 Your order has been placed successfully.\n"
            "📞 Our team will contact you shortly.\n\n"
            "🙏 Thank you for choosing Home Made Foods!"
        )

    return "⚠️ Please type *Hi* to start again."
