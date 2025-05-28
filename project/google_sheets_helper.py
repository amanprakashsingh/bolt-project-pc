"""Google Sheets API integration for managing user and payment data."""

import os
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2 import service_account
from config import (
    GOOGLE_CREDENTIALS_FILE,
    USER_SPREADSHEET_ID, 
    PAYMENT_SPREADSHEET_ID,
    USER_SHEET_NAME,
    PAYMENT_SHEET_NAME,
    USER_HEADERS,
    PAYMENT_HEADERS
)

class GoogleSheetsHelper:
    """Helper class for Google Sheets operations."""
    
    def __init__(self):
        """Initialize the Google Sheets API client."""
        self.creds = None
        self.users_sheet = None
        self.payments_sheet = None
        self._setup_credentials()
        
    def _setup_credentials(self):
        """Set up Google Sheets API credentials."""
        try:
            scopes = ['https://www.googleapis.com/auth/spreadsheets']
            
            if os.path.exists(GOOGLE_CREDENTIALS_FILE):
                self.creds = service_account.Credentials.from_service_account_file(
                    GOOGLE_CREDENTIALS_FILE, scopes=scopes
                )
                
                # Create service
                service = build('sheets', 'v4', credentials=self.creds)
                self.users_sheet = service.spreadsheets()
                self.payments_sheet = service.spreadsheets()
            else:
                print(f"Credentials file not found: {GOOGLE_CREDENTIALS_FILE}")
        except Exception as e:
            print(f"Error setting up Google Sheets API: {e}")
    
    def ensure_headers(self, spreadsheet_id, sheet_name, headers):
        """Ensure headers are present at the top of the sheet."""
        try:
            # Get the first row
            result = self.users_sheet.values().get(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet_name}!A1:Z1"
            ).execute()
            
            values = result.get('values', [])
            
            # If no values or headers don't match, update headers
            if not values or values[0] != headers:
                self.users_sheet.values().update(
                    spreadsheetId=spreadsheet_id,
                    range=f"{sheet_name}!A1",
                    valueInputOption="RAW",
                    body={"values": [headers]}
                ).execute()
                return True
            return True
        except Exception as e:
            print(f"Error ensuring headers: {e}")
            return False
    
    def get_all_users(self):
        """Get all users from the spreadsheet."""
        try:
            # Ensure headers are present
            self.ensure_headers(USER_SPREADSHEET_ID, USER_SHEET_NAME, USER_HEADERS)
            
            # Get all rows except header
            result = self.users_sheet.values().get(
                spreadsheetId=USER_SPREADSHEET_ID,
                range=f"{USER_SHEET_NAME}!A2:Z"
            ).execute()
            
            values = result.get('values', [])
            return values
        except Exception as e:
            print(f"Error getting users: {e}")
            return []
    
    def find_user_by_username(self, username):
        """Find a user by username."""
        users = self.get_all_users()
        for i, user in enumerate(users, start=2):  # Start from row 2 (after header)
            if user and user[0] == username:
                return user, i
        return None, None
    
    def register_user(self, user_data):
        """Register a new user."""
        try:
            # Ensure headers are present
            self.ensure_headers(USER_SPREADSHEET_ID, USER_SHEET_NAME, USER_HEADERS)
            
            # Check if user already exists
            existing_user, _ = self.find_user_by_username(user_data[0])
            if existing_user:
                return False, "Username already exists"
            
            # Append the new user
            self.users_sheet.values().append(
                spreadsheetId=USER_SPREADSHEET_ID,
                range=f"{USER_SHEET_NAME}!A2",
                valueInputOption="RAW",
                body={"values": [user_data]}
            ).execute()
            
            return True, "User registered successfully"
        except Exception as e:
            print(f"Error registering user: {e}")
            return False, f"Error: {str(e)}"
    
    def get_user_balance(self, username):
        """Get the balance of a user."""
        user_data, _ = self.find_user_by_username(username)
        if user_data and len(user_data) >= 8:
            return user_data[7]  # Balance is the 8th column (index 7)
        return "0"  # Default balance if not found or no balance set
    
    def update_user_balance(self, username, new_balance):
        """Update the balance of a user."""
        try:
            user_data, row_index = self.find_user_by_username(username)
            if not user_data:
                return False, "User not found"
            
            # Update the balance (8th column, index 7)
            self.users_sheet.values().update(
                spreadsheetId=USER_SPREADSHEET_ID,
                range=f"{USER_SHEET_NAME}!H{row_index}",
                valueInputOption="RAW",
                body={"values": [[str(new_balance)]]}
            ).execute()
            
            return True, "Balance updated successfully"
        except Exception as e:
            print(f"Error updating balance: {e}")
            return False, f"Error: {str(e)}"
    
    def get_user_payment_info(self, username):
        """Get the payment information of a user."""
        user_data, _ = self.find_user_by_username(username)
        if not user_data:
            return None
        
        payment_info = {
            "preferred_mode": user_data[3] if len(user_data) > 3 else None,
            "upi_id": user_data[4] if len(user_data) > 4 else None,
            "bank_account": user_data[5] if len(user_data) > 5 else None,
            "ifsc_code": user_data[6] if len(user_data) > 6 else None
        }
        
        return payment_info
    
    def update_user_profile(self, username, field, value):
        """Update a specific field in the user's profile."""
        try:
            user_data, row_index = self.find_user_by_username(username)
            if not user_data:
                return False, "User not found"
            
            # Map field names to column indices
            field_map = {
                "first_name": 1,
                "last_name": 2,
                "preferred_payment_mode": 3,
                "upi_id": 4,
                "bank_account": 5,
                "ifsc_code": 6
            }
            
            if field not in field_map:
                return False, f"Invalid field: {field}"
            
            column_index = field_map[field]
            column_letter = chr(65 + column_index)  # Convert to A, B, C, etc.
            
            # Update the field
            self.users_sheet.values().update(
                spreadsheetId=USER_SPREADSHEET_ID,
                range=f"{USER_SHEET_NAME}!{column_letter}{row_index}",
                valueInputOption="RAW",
                body={"values": [[value]]}
            ).execute()
            
            return True, f"{field.replace('_', ' ').title()} updated successfully"
        except Exception as e:
            print(f"Error updating profile: {e}")
            return False, f"Error: {str(e)}"
    
    def add_payment_request(self, payment_data):
        """Add a new payment request."""
        try:
            # Ensure headers are present
            self.ensure_headers(PAYMENT_SPREADSHEET_ID, PAYMENT_SHEET_NAME, PAYMENT_HEADERS)
            
            # Add timestamp and pending status
            payment_data.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            payment_data.append("Pending")
            
            # Append the payment request
            self.payments_sheet.values().append(
                spreadsheetId=PAYMENT_SPREADSHEET_ID,
                range=f"{PAYMENT_SHEET_NAME}!A2",
                valueInputOption="RAW",
                body={"values": [payment_data]}
            ).execute()
            
            return True, "Payment request added successfully"
        except Exception as e:
            print(f"Error adding payment request: {e}")
            return False, f"Error: {str(e)}"