"""Configuration settings for the Telegram bot."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Telegram Bot Token
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Google Sheets Configuration
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
USER_SPREADSHEET_ID = os.getenv("USER_SPREADSHEET_ID")
PAYMENT_SPREADSHEET_ID = os.getenv("PAYMENT_SPREADSHEET_ID")
USER_SHEET_NAME = os.getenv("USER_SHEET_NAME", "Users")
PAYMENT_SHEET_NAME = os.getenv("PAYMENT_SHEET_NAME", "Payments")

# User sheet headers
USER_HEADERS = [
    "Username", 
    "First Name", 
    "Last Name", 
    "Preferred Payment Mode", 
    "UPI ID", 
    "Bank Account", 
    "IFSC Code", 
    "Balance"
]

# Payment sheet headers
PAYMENT_HEADERS = [
    "Username", 
    "Amount", 
    "Payment Mode", 
    "UPI ID/Bank Account", 
    "IFSC Code", 
    "Request Date", 
    "Status"
]

# Bot messages
WELCOME_MESSAGE = """Welcome to the Employee Payment System!
Choose an option:
1. Signup
2. Login"""

MAIN_MENU = """Main Menu:
1. Check Balance
2. Withdraw Funds
3. Join Channel
4. Update Profile"""

# Payment settings
DEFAULT_PAYMENT_DATE = "15th of the month"
INVOICE_BOT_USERNAME = "invoice_earnifybot"