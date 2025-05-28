"""User management module for handling user sessions and data."""

from google_sheets_helper import GoogleSheetsHelper

class UserManager:
    """Manages user sessions and interactions with the Google Sheets database."""
    
    def __init__(self):
        """Initialize user manager with Google Sheets helper."""
        self.sheets_helper = GoogleSheetsHelper()
        self.active_users = {}  # Store user session data
    
    def start_session(self, user_id):
        """Start a new session for a user."""
        if user_id not in self.active_users:
            self.active_users[user_id] = {
                "username": None,
                "logged_in": False,
                "registration_state": None,
                "registration_data": {},
                "withdraw_state": None,
                "withdraw_data": {},
                "update_profile_state": None,
                "update_field": None
            }
    
    def end_session(self, user_id):
        """End a user's session."""
        if user_id in self.active_users:
            del self.active_users[user_id]
    
    def is_logged_in(self, user_id):
        """Check if a user is logged in."""
        if user_id in self.active_users:
            return self.active_users[user_id]["logged_in"]
        return False
    
    def get_username(self, user_id):
        """Get the username of a logged-in user."""
        if self.is_logged_in(user_id):
            return self.active_users[user_id]["username"]
        return None
    
    def set_registration_state(self, user_id, state):
        """Set the registration state for a user."""
        if user_id in self.active_users:
            self.active_users[user_id]["registration_state"] = state
    
    def get_registration_state(self, user_id):
        """Get the registration state for a user."""
        if user_id in self.active_users:
            return self.active_users[user_id]["registration_state"]
        return None
    
    def set_registration_data(self, user_id, field, value):
        """Set a field in the registration data."""
        if user_id in self.active_users:
            self.active_users[user_id]["registration_data"][field] = value
    
    def get_registration_data(self, user_id):
        """Get all registration data for a user."""
        if user_id in self.active_users:
            return self.active_users[user_id]["registration_data"]
        return {}
    
    def login_user(self, user_id, username):
        """Log in a user."""
        user_data, _ = self.sheets_helper.find_user_by_username(username)
        if user_data:
            self.active_users[user_id]["username"] = username
            self.active_users[user_id]["logged_in"] = True
            return True
        return False
    
    def register_user(self, user_id):
        """Register a new user with the collected data."""
        data = self.active_users[user_id]["registration_data"]
        
        # Prepare user data row
        username = data.get("username", "")
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")
        payment_mode = data.get("payment_mode", "")
        
        user_row = [username, first_name, last_name, payment_mode]
        
        # Add UPI ID or Bank Account details based on payment mode
        if payment_mode == "UPI":
            user_row.extend([data.get("upi_id", ""), "", ""])
        elif payment_mode == "Bank Account":
            user_row.extend(["", data.get("bank_account", ""), data.get("ifsc_code", "")])
        else:
            user_row.extend(["", "", ""])
        
        # Add initial balance (0)
        user_row.append("0")
        
        # Register the user
        success, message = self.sheets_helper.register_user(user_row)
        
        if success:
            # Auto-login after registration
            self.active_users[user_id]["username"] = username
            self.active_users[user_id]["logged_in"] = True
        
        return success, message
    
    def set_withdraw_state(self, user_id, state):
        """Set the withdrawal state for a user."""
        if user_id in self.active_users:
            self.active_users[user_id]["withdraw_state"] = state
    
    def get_withdraw_state(self, user_id):
        """Get the withdrawal state for a user."""
        if user_id in self.active_users:
            return self.active_users[user_id]["withdraw_state"]
        return None
    
    def set_withdraw_data(self, user_id, field, value):
        """Set a field in the withdrawal data."""
        if user_id in self.active_users:
            self.active_users[user_id]["withdraw_data"][field] = value
    
    def get_withdraw_data(self, user_id):
        """Get all withdrawal data for a user."""
        if user_id in self.active_users:
            return self.active_users[user_id]["withdraw_data"]
        return {}
    
    def set_update_profile_state(self, user_id, state):
        """Set the profile update state for a user."""
        if user_id in self.active_users:
            self.active_users[user_id]["update_profile_state"] = state
    
    def get_update_profile_state(self, user_id):
        """Get the profile update state for a user."""
        if user_id in self.active_users:
            return self.active_users[user_id]["update_profile_state"]
        return None
    
    def set_update_field(self, user_id, field):
        """Set the field being updated in the profile."""
        if user_id in self.active_users:
            self.active_users[user_id]["update_field"] = field
    
    def get_update_field(self, user_id):
        """Get the field being updated in the profile."""
        if user_id in self.active_users:
            return self.active_users[user_id]["update_field"]
        return None