# Employee Payment Telegram Bot

A Telegram bot for managing employee payments via Google Sheets integration.

## Features

- User registration and login
- Balance checking
- Fund withdrawal requests
- Channel joining
- Profile management
- Google Sheets integration for data storage

## Setup Instructions

### Prerequisites

- Python 3.7+
- A Telegram Bot Token (create using [BotFather](https://t.me/botfather))
- Google Cloud Platform account with Google Sheets API enabled
- Google Sheets service account credentials

### Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd employee-payment-bot
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file based on `.env.example`:
   ```
   cp .env.example .env
   ```

4. Fill in the required environment variables in the `.env` file:
   - `TELEGRAM_TOKEN`: Your Telegram bot token
   - `GOOGLE_CREDENTIALS_FILE`: Path to your Google service account credentials JSON file
   - `USER_SPREADSHEET_ID`: Google Sheets ID for user data
   - `PAYMENT_SPREADSHEET_ID`: Google Sheets ID for payment requests

### Google Sheets Setup

1. Create two Google Sheets:
   - One for user data with the following headers:
     ```
     Username, First Name, Last Name, Preferred Payment Mode, UPI ID, Bank Account, IFSC Code, Balance
     ```
   - One for payment requests with the following headers:
     ```
     Username, Amount, Payment Mode, UPI ID/Bank Account, IFSC Code, Request Date, Status
     ```

2. Share both sheets with the email address from your service account credentials.

### Running the Bot

```
python main.py
```

## Usage

1. Start the bot by sending `/start`
2. Choose to signup or login
3. After logging in, use the main menu to:
   - Check your balance
   - Withdraw funds
   - Join the channel
   - Update your profile

## License

MIT License