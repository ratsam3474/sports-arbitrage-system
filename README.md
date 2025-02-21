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

## Supported Sports
- NFL (American Football)
- NBA (Basketball)
- MLB (Baseball)
- NHL (Ice Hockey)
- EPL (Soccer)
- UEFA Champions League
- Tennis (ATP/WTA)

## Setup
1. Configure API key in arbb.py
2. Set up email notifications in arbitrage_notifier.py
3. Run both scripts:
   - arbb.py to fetch and analyze odds
   - arbitrage_notifier.py to receive notifications

## Requirements
- Python 3.6+
- The-Odds-API key
- Gmail account with App Password enabled
- SQLite database
