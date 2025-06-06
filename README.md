# Sports Arbitrage System

A Python-based system that monitors sports betting odds across multiple bookmakers to find arbitrage opportunities and sends notifications when profitable opportunities are found.

## Components

### 1. Arbitrage Finder (arbb.py)
- Fetches odds from The-Odds-API
- Analyzes odds to find arbitrage opportunities
- Stores opportunities in SQLite database
- Supports multiple sports and bookmakers
- Includes automated retry mechanism

### 2. Arbitrage Notifier (arbitrage_notifier.py)
- Monitors the database for profitable opportunities
- Sends email notifications for opportunities with 0.1% - 0.2% profit margin
- Includes detailed betting information and bookmaker links

## Detailed Setup Guide

### Prerequisites
1. Python 3.6 or higher installed on your system
2. The-Odds-API key (get it from https://the-odds-api.com/)
3. Gmail account with 2FA enabled for notifications

### Step-by-Step Installation
1. Clone this repository:
   \\\ash
   git clone https://github.com/ratsam3474/sports-arbitrage-system.git
   cd sports-arbitrage-system
   \\\

2. Install required Python packages:
   \\\ash
   pip install requests sqlite3 smtplib
   \\\

3. Configure API Key:
   - Open arbb.py
   - Replace 'your_api_key_here' with your actual The-Odds-API key:
     \\\python
     API_KEY = 'your_api_key_here'
     \\\

4. Set up Email Notifications:
   - Enable 2-Step Verification in your Google Account
   - Generate an App Password:
     - Go to Google Account Settings
     - Security
     - 2-Step Verification
     - App Passwords
     - Generate new app password for 'Mail'
   - Open arbitrage_notifier.py and update:
     \\\python
     EMAIL_SENDER = 'your_gmail@gmail.com'
     EMAIL_PASSWORD = 'your_16_char_app_password'
     EMAIL_RECEIVER = 'recipient@email.com'
     \\\

### Running the System

1. Start the Odds Fetcher:
   \\\ash
   python arbb.py
   \\\
   This will:
   - Create the SQLite database
   - Start fetching odds every 5 minutes
   - Find and store arbitrage opportunities

2. Start the Notifier:
   \\\ash
   python arbitrage_notifier.py
   \\\
   This will:
   - Monitor the database for opportunities
   - Send email notifications for profitable bets
   - Check every 5 minutes

### Customization

1. Adjust Profit Margins:
   In arbitrage_notifier.py:
   \\\python
   MIN_PROFIT = 0.1  # Minimum profit percentage
   MAX_PROFIT = 0.2  # Maximum profit percentage
   \\\

2. Modify Sports List:
   In arbb.py, edit the SPORTS list:
   \\\python
   SPORTS = [
       'americanfootball_nfl',
       'basketball_nba',
       # Add or remove sports as needed
   ]
   \\\

### Supported Sports
- NFL (American Football)
- NBA (Basketball)
- MLB (Baseball)
- NHL (Ice Hockey)
- EPL (Soccer)
- UEFA Champions League
- Tennis (ATP/WTA)

### Troubleshooting

1. Database Issues:
   - Delete the .db file and restart arbb.py to recreate
   - Check file permissions

2. Email Notification Issues:
   - Verify App Password is correct
   - Ensure 2FA is enabled
   - Check spam folder

3. API Issues:
   - Verify API key is valid
   - Check remaining API credits
   - Monitor rate limits

## Requirements
- Python 3.6+
- The-Odds-API key
- Gmail account with App Password enabled
- SQLite database

## Notes
- The system uses The-Odds-API free tier by default
- Email notifications are sent via Gmail SMTP
- Database is automatically cleaned every 5 minutes
- Retry mechanism handles API failures

## Contributing
Feel free to fork, submit PRs, or report issues!

## License
This project is licensed under the MIT License - see the LICENSE file for details
