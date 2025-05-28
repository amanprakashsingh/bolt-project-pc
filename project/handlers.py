"""Telegram message handlers for the payment bot."""

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext
from config import (
    WELCOME_MESSAGE,
    MAIN_MENU,
    DEFAULT_PAYMENT_DATE,
    INVOICE_BOT_USERNAME
)
from user_manager import UserManager
from google_sheets_helper import GoogleSheetsHelper

# Initialize managers
user_manager = UserManager()
sheets_helper = GoogleSheetsHelper()

# Keyboard layouts
def get_welcome_keyboard():
    """Get keyboard for welcome message."""
    return ReplyKeyboardMarkup([['1. Signup', '2. Login']], one_time_keyboard=True)

def get_main_menu_keyboard():
    """Get keyboard for main menu."""
    return ReplyKeyboardMarkup([
        ['1. Check Balance'],
        ['2. Withdraw Funds'],
        ['3. Join Channel'],
        ['4. Update Profile'],
        ['Logout']
    ], one_time_keyboard=True)

def get_payment_mode_keyboard():
    """Get keyboard for payment mode selection."""
    return ReplyKeyboardMarkup([['UPI', 'Bank Account']], one_time_keyboard=True)

def get_yes_no_keyboard():
    """Get keyboard for yes/no questions."""
    return ReplyKeyboardMarkup([['Yes', 'No']], one_time_keyboard=True)

def get_profile_update_keyboard():
    """Get keyboard for profile update options."""
    return ReplyKeyboardMarkup([
        ['First Name', 'Last Name'],
        ['Payment Mode', 'UPI ID'],
        ['Bank Account', 'IFSC Code'],
        ['Back to Main Menu']
    ], one_time_keyboard=True)

# Command handlers
def start(update: Update, context: CallbackContext):
    """Handle the /start command."""
    user_id = update.effective_user.id
    user_manager.start_session(user_id)
    
    update.message.reply_text(
        WELCOME_MESSAGE,
        reply_markup=get_welcome_keyboard()
    )

def main_menu(update: Update, context: CallbackContext):
    """Show the main menu."""
    user_id = update.effective_user.id
    
    if not user_manager.is_logged_in(user_id):
        update.message.reply_text(
            "You need to login first.",
            reply_markup=get_welcome_keyboard()
        )
        return
    
    update.message.reply_text(
        MAIN_MENU,
        reply_markup=get_main_menu_keyboard()
    )

def logout(update: Update, context: CallbackContext):
    """Handle user logout."""
    user_id = update.effective_user.id
    user_manager.end_session(user_id)
    
    update.message.reply_text(
        "You have been logged out. Type /start to begin again.",
        reply_markup=ReplyKeyboardRemove()
    )

# Message handler - processes all incoming messages
def handle_message(update: Update, context: CallbackContext):
    """Handle all incoming messages."""
    text = update.message.text
    user_id = update.effective_user.id
    
    # Ensure user has a session
    if user_id not in user_manager.active_users:
        user_manager.start_session(user_id)
    
    # Handle welcome menu selection
    if text == "1. Signup" or text == "Signup":
        return start_registration(update, context)
    elif text == "2. Login" or text == "Login":
        return prompt_login_username(update, context)
    
    # Handle logout
    if text == "Logout":
        return logout(update, context)
    
    # Handle main menu selection for logged-in users
    if user_manager.is_logged_in(user_id):
        if text == "1. Check Balance" or text == "Check Balance":
            return check_balance(update, context)
        elif text == "2. Withdraw Funds" or text == "Withdraw Funds":
            return start_withdrawal(update, context)
        elif text == "3. Join Channel" or text == "Join Channel":
            return join_channel(update, context)
        elif text == "4. Update Profile" or text == "Update Profile":
            return start_profile_update(update, context)
        elif text == "Back to Main Menu":
            return main_menu(update, context)
    
    # Handle registration flow
    reg_state = user_manager.get_registration_state(user_id)
    if reg_state:
        return handle_registration(update, context, reg_state)
    
    # Handle login flow (when username is provided)
    if not user_manager.is_logged_in(user_id) and "login_username_provided" in context.user_data:
        return process_login(update, context)
    
    # Handle withdrawal flow
    withdraw_state = user_manager.get_withdraw_state(user_id)
    if withdraw_state:
        return handle_withdrawal(update, context, withdraw_state)
    
    # Handle profile update flow
    update_state = user_manager.get_update_profile_state(user_id)
    if update_state:
        return handle_profile_update(update, context, update_state)
    
    # Default response if nothing matches
    update.message.reply_text(
        "I didn't understand that. Please use the menu options.",
        reply_markup=get_welcome_keyboard() if not user_manager.is_logged_in(user_id) else get_main_menu_keyboard()
    )

# Registration handlers
def start_registration(update: Update, context: CallbackContext):
    """Start the registration process."""
    user_id = update.effective_user.id
    user_manager.set_registration_state(user_id, "awaiting_username")
    
    update.message.reply_text(
        "Please enter your desired username:",
        reply_markup=ReplyKeyboardRemove()
    )

def handle_registration(update: Update, context: CallbackContext, state):
    """Handle registration state machine."""
    user_id = update.effective_user.id
    text = update.message.text
    
    if state == "awaiting_username":
        # Check if username exists
        existing_user, _ = sheets_helper.find_user_by_username(text)
        if existing_user:
            update.message.reply_text("This username already exists. Please choose another username:")
            return
        
        user_manager.set_registration_data(user_id, "username", text)
        user_manager.set_registration_state(user_id, "awaiting_first_name")
        update.message.reply_text("Please enter your first name:")
    
    elif state == "awaiting_first_name":
        user_manager.set_registration_data(user_id, "first_name", text)
        user_manager.set_registration_state(user_id, "awaiting_last_name")
        update.message.reply_text("Please enter your last name:")
    
    elif state == "awaiting_last_name":
        user_manager.set_registration_data(user_id, "last_name", text)
        user_manager.set_registration_state(user_id, "awaiting_payment_mode")
        update.message.reply_text(
            "Please select your preferred payment mode:",
            reply_markup=get_payment_mode_keyboard()
        )
    
    elif state == "awaiting_payment_mode":
        if text not in ["UPI", "Bank Account"]:
            update.message.reply_text(
                "Please select a valid payment mode:",
                reply_markup=get_payment_mode_keyboard()
            )
            return
        
        user_manager.set_registration_data(user_id, "payment_mode", text)
        
        if text == "UPI":
            user_manager.set_registration_state(user_id, "awaiting_upi_id")
            update.message.reply_text(
                "Please enter your UPI ID:",
                reply_markup=ReplyKeyboardRemove()
            )
        else:  # Bank Account
            user_manager.set_registration_state(user_id, "awaiting_bank_account")
            update.message.reply_text(
                "Please enter your Bank Account Number:",
                reply_markup=ReplyKeyboardRemove()
            )
    
    elif state == "awaiting_upi_id":
        user_manager.set_registration_data(user_id, "upi_id", text)
        user_manager.set_registration_state(user_id, "awaiting_confirmation")
        
        # Show registration summary
        data = user_manager.get_registration_data(user_id)
        summary = f"""Please confirm your details:
Username: {data.get('username', '')}
Name: {data.get('first_name', '')} {data.get('last_name', '')}
Payment Mode: {data.get('payment_mode', '')}
UPI ID: {data.get('upi_id', '')}"""
        
        update.message.reply_text(
            summary + "\n\nIs this correct?",
            reply_markup=get_yes_no_keyboard()
        )
    
    elif state == "awaiting_bank_account":
        user_manager.set_registration_data(user_id, "bank_account", text)
        user_manager.set_registration_state(user_id, "awaiting_ifsc_code")
        update.message.reply_text("Please enter your IFSC Code:")
    
    elif state == "awaiting_ifsc_code":
        user_manager.set_registration_data(user_id, "ifsc_code", text)
        user_manager.set_registration_state(user_id, "awaiting_confirmation")
        
        # Show registration summary
        data = user_manager.get_registration_data(user_id)
        summary = f"""Please confirm your details:
Username: {data.get('username', '')}
Name: {data.get('first_name', '')} {data.get('last_name', '')}
Payment Mode: {data.get('payment_mode', '')}
Bank Account: {data.get('bank_account', '')}
IFSC Code: {data.get('ifsc_code', '')}"""
        
        update.message.reply_text(
            summary + "\n\nIs this correct?",
            reply_markup=get_yes_no_keyboard()
        )
    
    elif state == "awaiting_confirmation":
        if text.lower() == "yes":
            success, message = user_manager.register_user(user_id)
            
            if success:
                user_manager.set_registration_state(user_id, None)
                update.message.reply_text(
                    f"Registration successful! You are now logged in as {user_manager.get_username(user_id)}.",
                    reply_markup=get_main_menu_keyboard()
                )
            else:
                update.message.reply_text(
                    f"Registration failed: {message}. Please try again.",
                    reply_markup=get_welcome_keyboard()
                )
        else:
            user_manager.set_registration_state(user_id, None)
            update.message.reply_text(
                "Registration cancelled. Please start again if you wish to register.",
                reply_markup=get_welcome_keyboard()
            )

# Login handlers
def prompt_login_username(update: Update, context: CallbackContext):
    """Prompt for username during login."""
    update.message.reply_text(
        "Please enter your username:",
        reply_markup=ReplyKeyboardRemove()
    )
    context.user_data["login_username_provided"] = True

def process_login(update: Update, context: CallbackContext):
    """Process login with provided username."""
    user_id = update.effective_user.id
    username = update.message.text
    
    # Check if user exists
    if user_manager.login_user(user_id, username):
        del context.user_data["login_username_provided"]
        update.message.reply_text(
            f"Login successful! Welcome back, {username}.",
            reply_markup=get_main_menu_keyboard()
        )
    else:
        del context.user_data["login_username_provided"]
        update.message.reply_text(
            "Login failed. Username not found.",
            reply_markup=get_welcome_keyboard()
        )

# Balance checking
def check_balance(update: Update, context: CallbackContext):
    """Check and display user balance."""
    user_id = update.effective_user.id
    username = user_manager.get_username(user_id)
    
    if not username:
        update.message.reply_text(
            "You need to be logged in to check your balance.",
            reply_markup=get_welcome_keyboard()
        )
        return
    
    balance = sheets_helper.get_user_balance(username)
    
    update.message.reply_text(
        f"Your current balance is: ₹{balance}",
        reply_markup=get_main_menu_keyboard()
    )

# Withdrawal handlers
def start_withdrawal(update: Update, context: CallbackContext):
    """Start the withdrawal process."""
    user_id = update.effective_user.id
    username = user_manager.get_username(user_id)
    
    if not username:
        update.message.reply_text(
            "You need to be logged in to withdraw funds.",
            reply_markup=get_welcome_keyboard()
        )
        return
    
    user_manager.set_withdraw_state(user_id, "awaiting_amount")
    update.message.reply_text(
        "Please enter the amount you wish to withdraw:",
        reply_markup=ReplyKeyboardRemove()
    )

def handle_withdrawal(update: Update, context: CallbackContext, state):
    """Handle withdrawal state machine."""
    user_id = update.effective_user.id
    text = update.message.text
    username = user_manager.get_username(user_id)
    
    if state == "awaiting_amount":
        try:
            amount = float(text)
            if amount <= 0:
                update.message.reply_text("Please enter a positive amount:")
                return
            
            user_manager.set_withdraw_data(user_id, "amount", amount)
            
            # Check if user has sufficient balance
            balance = float(sheets_helper.get_user_balance(username))
            
            if amount > balance:
                user_manager.set_withdraw_state(user_id, None)
                update.message.reply_text(
                    f"Insufficient balance. Your current balance is: ₹{balance}",
                    reply_markup=get_main_menu_keyboard()
                )
                return
            
            # Get user's payment info
            payment_info = sheets_helper.get_user_payment_info(username)
            preferred_mode = payment_info.get("preferred_mode", "Unknown")
            
            user_manager.set_withdraw_state(user_id, "awaiting_payment_mode_confirmation")
            update.message.reply_text(
                f"Your default payment mode is: {preferred_mode}\nWould you like to use this payment mode?",
                reply_markup=get_yes_no_keyboard()
            )
            
        except ValueError:
            update.message.reply_text("Please enter a valid number:")
    
    elif state == "awaiting_payment_mode_confirmation":
        if text.lower() == "yes":
            # Use default payment mode
            payment_info = sheets_helper.get_user_payment_info(username)
            payment_mode = payment_info.get("preferred_mode", "Unknown")
            
            # Process withdrawal with default payment mode
            process_withdrawal_request(update, context, payment_mode)
        else:
            # Ask for new payment mode
            user_manager.set_withdraw_state(user_id, "awaiting_new_payment_mode")
            update.message.reply_text(
                "Please select your preferred payment mode for this withdrawal:",
                reply_markup=get_payment_mode_keyboard()
            )
    
    elif state == "awaiting_new_payment_mode":
        if text not in ["UPI", "Bank Account"]:
            update.message.reply_text(
                "Please select a valid payment mode:",
                reply_markup=get_payment_mode_keyboard()
            )
            return
        
        if text == "UPI":
            user_manager.set_withdraw_data(user_id, "payment_mode", "UPI")
            user_manager.set_withdraw_state(user_id, "awaiting_upi_id")
            update.message.reply_text(
                "Please enter your UPI ID:",
                reply_markup=ReplyKeyboardRemove()
            )
        else:  # Bank Account
            user_manager.set_withdraw_data(user_id, "payment_mode", "Bank Account")
            user_manager.set_withdraw_state(user_id, "awaiting_bank_account")
            update.message.reply_text(
                "Please enter your Bank Account Number:",
                reply_markup=ReplyKeyboardRemove()
            )
    
    elif state == "awaiting_upi_id":
        user_manager.set_withdraw_data(user_id, "upi_id", text)
        process_withdrawal_request(update, context, "UPI")
    
    elif state == "awaiting_bank_account":
        user_manager.set_withdraw_data(user_id, "bank_account", text)
        user_manager.set_withdraw_state(user_id, "awaiting_ifsc_code")
        update.message.reply_text("Please enter your IFSC Code:")
    
    elif state == "awaiting_ifsc_code":
        user_manager.set_withdraw_data(user_id, "ifsc_code", text)
        process_withdrawal_request(update, context, "Bank Account")

def process_withdrawal_request(update: Update, context: CallbackContext, payment_mode):
    """Process the withdrawal request."""
    user_id = update.effective_user.id
    username = user_manager.get_username(user_id)
    withdraw_data = user_manager.get_withdraw_data(user_id)
    
    amount = withdraw_data.get("amount", 0)
    
    # Create payment data
    payment_data = [username, str(amount), payment_mode]
    
    if payment_mode == "UPI":
        upi_id = withdraw_data.get("upi_id", "")
        if not upi_id:
            # Get from user profile
            payment_info = sheets_helper.get_user_payment_info(username)
            upi_id = payment_info.get("upi_id", "")
        
        payment_data.extend([upi_id, ""])
    else:  # Bank Account
        bank_account = withdraw_data.get("bank_account", "")
        ifsc_code = withdraw_data.get("ifsc_code", "")
        
        if not bank_account or not ifsc_code:
            # Get from user profile
            payment_info = sheets_helper.get_user_payment_info(username)
            bank_account = payment_info.get("bank_account", "")
            ifsc_code = payment_info.get("ifsc_code", "")
        
        payment_data.extend([bank_account, ifsc_code])
    
    # Add payment request to sheet
    success, message = sheets_helper.add_payment_request(payment_data)
    
    if success:
        # Update user balance
        current_balance = float(sheets_helper.get_user_balance(username))
        new_balance = current_balance - amount
        sheets_helper.update_user_balance(username, new_balance)
        
        # Reset withdrawal state
        user_manager.set_withdraw_state(user_id, None)
        
        # Notify user
        update.message.reply_text(
            f"Your payment request for ₹{amount} has been received. It will be processed on {DEFAULT_PAYMENT_DATE}.\n\n" +
            f"Please forward a screenshot of this chat to @{INVOICE_BOT_USERNAME} for reference.",
            reply_markup=get_main_menu_keyboard()
        )
    else:
        user_manager.set_withdraw_state(user_id, None)
        update.message.reply_text(
            f"Failed to process withdrawal: {message}",
            reply_markup=get_main_menu_keyboard()
        )

# Channel joining
def join_channel(update: Update, context: CallbackContext):
    """Handle channel joining request."""
    user_id = update.effective_user.id
    
    if not user_manager.is_logged_in(user_id):
        update.message.reply_text(
            "You need to be logged in to join the channel.",
            reply_markup=get_welcome_keyboard()
        )
        return
    
    update.message.reply_text(
        "To join our channel, please click this link: https://t.me/employeechannel\n" +
        "This is where we share important announcements and updates.",
        reply_markup=get_main_menu_keyboard()
    )

# Profile update handlers
def start_profile_update(update: Update, context: CallbackContext):
    """Start the profile update process."""
    user_id = update.effective_user.id
    
    if not user_manager.is_logged_in(user_id):
        update.message.reply_text(
            "You need to be logged in to update your profile.",
            reply_markup=get_welcome_keyboard()
        )
        return
    
    user_manager.set_update_profile_state(user_id, "selecting_field")
    update.message.reply_text(
        "Which part of your profile would you like to update?",
        reply_markup=get_profile_update_keyboard()
    )

def handle_profile_update(update: Update, context: CallbackContext, state):
    """Handle profile update state machine."""
    user_id = update.effective_user.id
    text = update.message.text
    username = user_manager.get_username(user_id)
    
    if state == "selecting_field":
        if text == "Back to Main Menu":
            user_manager.set_update_profile_state(user_id, None)
            return main_menu(update, context)
        
        field_mapping = {
            "First Name": "first_name",
            "Last Name": "last_name",
            "Payment Mode": "payment_mode",
            "UPI ID": "upi_id",
            "Bank Account": "bank_account",
            "IFSC Code": "ifsc_code"
        }
        
        if text not in field_mapping:
            update.message.reply_text(
                "Please select a valid field to update:",
                reply_markup=get_profile_update_keyboard()
            )
            return
        
        field = field_mapping[text]
        user_manager.set_update_field(user_id, field)
        
        if field == "payment_mode":
            user_manager.set_update_profile_state(user_id, "updating_payment_mode")
            update.message.reply_text(
                "Please select your new preferred payment mode:",
                reply_markup=get_payment_mode_keyboard()
            )
        else:
            user_manager.set_update_profile_state(user_id, "updating_field")
            update.message.reply_text(
                f"Please enter your new {text}:",
                reply_markup=ReplyKeyboardRemove()
            )
    
    elif state == "updating_payment_mode":
        if text not in ["UPI", "Bank Account"]:
            update.message.reply_text(
                "Please select a valid payment mode:",
                reply_markup=get_payment_mode_keyboard()
            )
            return
        
        field = user_manager.get_update_field(user_id)
        success, message = sheets_helper.update_user_profile(username, field, text)
        
        if success:
            user_manager.set_update_profile_state(user_id, None)
            update.message.reply_text(
                f"Your payment mode has been updated to {text}.\n\n" +
                "You may also want to update your UPI ID or Bank Account details.",
                reply_markup=get_main_menu_keyboard()
            )
        else:
            user_manager.set_update_profile_state(user_id, None)
            update.message.reply_text(
                f"Failed to update profile: {message}",
                reply_markup=get_main_menu_keyboard()
            )
    
    elif state == "updating_field":
        field = user_manager.get_update_field(user_id)
        success, message = sheets_helper.update_user_profile(username, field, text)
        
        if success:
            user_manager.set_update_profile_state(user_id, None)
            update.message.reply_text(
                f"Your profile has been updated successfully.",
                reply_markup=get_main_menu_keyboard()
            )
        else:
            user_manager.set_update_profile_state(user_id, None)
            update.message.reply_text(
                f"Failed to update profile: {message}",
                reply_markup=get_main_menu_keyboard()
            )