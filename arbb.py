import json 
import requests 
import sqlite3
import itertools
import time

# API Key for The-Odds-API (Replace with your actual key)
API_KEY = "your_api_key_here"  # Replace with your The-Odds-API key
BASE_URL = "https://api.the-odds-api.com/v4/sports/{sport_key}/odds"

# List of sports and leagues to track
SPORTS = [
    "americanfootball_nfl", "basketball_nba", "baseball_mlb", "icehockey_nhl", 
    "soccer_epl", "soccer_uefa_champs_league",  
    "tennis_atp_wimbledon", "tennis_wta_us_open"
]

MARKETS = ["h2h"]  # Supported betting markets

BOOKMAKER_LINKS = {
    "BetOnline.ag": "https://www.betonline.ag",
    "BetMGM": "https://sports.nj.betmgm.com",
    "BetRivers": "https://www.betrivers.com",
    "BetUS": "https://www.betus.com.pa",
    "Bovada": "https://www.bovada.lv",
    "Caesars": "https://www.williamhill.com",
    "DraftKings": "https://draftkings.com",
    "Fanatics": "https://sportsbook.fanatics.com",
    "FanDuel": "https://sportsbook.fanduel.com",
    "LowVig.ag": "https://www.lowvig.ag",
    "MyBookie.ag": "https://mybookie.ag",
    "Bally Bet": "https://play.ballybet.com",
    "BetAnySports": "https://betanysports.eu",
    "betPARX": "https://betparx.com",
    "ESPN BET": "https://espnbet.com",
    "Fliff": "https://www.getfliff.com",
    "Hard Rock Bet": "https://app.hardrock.bet",
    "Wind Creek (Betfred PA)": "https://play.windcreekcasino.com",
    "888sport": "https://www.888sport.com",
    "Betfair Exchange": "https://www.betfair.com",
    "Betfair Sportsbook": "https://www.betfair.com",
    "Bet Victor": "https://www.betvictor.com",
    "Betway": "https://betway.com",
    "BoyleSports": "https://boylesports.com",
    "Casumo": "https://casumo.com",
    "Coral": "https://sports.coral.co.uk",
    "Grosvenor": "https://www.grosvenorcasinos.com",
    "Ladbrokes": "https://www.ladbrokes.com",
    "LeoVegas": "https://www.leovegas.com",
    "LiveScore Bet": "https://www.livescorebet.com",
    "Matchbook": "https://www.matchbook.com",
    "Paddy Power": "https://www.paddypower.com",
    "Sky Bet": "https://m.skybet.com",
    "Smarkets": "https://smarkets.com",
    "Unibet": "https://www.unibet.co.uk",
    "Virgin Bet": "https://www.virginbet.com",
    "William Hill (UK)": "https://www.williamhill.com",
    "1xBet": "https://1xbet.com",
    "Betclic": "https://www.betclic.com"
}


# Database setup
def setup_database():
    conn = sqlite3.connect("arbitrage_opportunities.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS opportunities (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        event TEXT,
                        sport TEXT,
                        league TEXT,
                        market TEXT,
                        bookmaker1 TEXT,
                        team1 TEXT,
                        odds1 REAL,
                        bookmaker1_link TEXT,
                        bookmaker2 TEXT,
                        team2 TEXT,
                        odds2 REAL,
                        bookmaker2_link TEXT,
                        profit_margin REAL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )''')
    conn.commit()
    conn.close()

# Function to fetch odds from The-Odds-API
def fetch_odds():
    odds_data = []
    for sport in SPORTS:
        for market in MARKETS:
            url = BASE_URL.format(sport_key=sport)
            params = {
                "apiKey": API_KEY,
                "regions": "us",
                "markets": market,
                "oddsFormat": "decimal",
                "includeLinks": "true"
            }
            print(f"Fetching odds for Sport: {sport}, Market: {market}")
            response = requests.get(url, params=params)
            
            if response.status_code != 200:
                 try:
                    error_response = response.json()  # Parse error message
                    print(f"⚠️ Error fetching odds for Sport: {sport}, Market: {market}")
                    print(f"Message: {error_response.get('message', 'No message')}")
                    print(f"Error Code: {error_response.get('error_code', 'No code')}")
                    print(f"Details: {error_response.get('details_url', 'No details provided')}")
                 except Exception as e:
                    print(f"⚠️ Unexpected error fetching odds for Sport: {sport}, Market: {market}")
                    print(f"Response Content: {response.text}")  # Print raw response if JSON decoding fails
                    print(f"Error: {str(e)}")
                 continue
            
            data = response.json()
            
            for event in data:
                event_name = event['sport_title'] + " - " + event['commence_time']
                sport_name = event['sport_title']
                league = event.get('sport_key', sport)  # Extract league from API response
                bookmakers = event.get('bookmakers', [])
                
                for bookmaker in bookmakers:
                    bookmaker_name = bookmaker['title']
                    bookmaker_link = bookmaker.get('links', {}).get('event', "N/A")
                    for market_data in bookmaker.get('markets', []):
                        if market_data['key'] == market:
                            outcomes = market_data['outcomes']
                            if len(outcomes) >= 2:
                                team1, odds1 = outcomes[0]['name'], outcomes[0]['price']
                                team2, odds2 = outcomes[1]['name'], outcomes[1]['price']
                                odds_data.append((event_name, sport_name, league, market, bookmaker_name, team1, odds1, bookmaker_link, team2, odds2, bookmaker_link))
    
    return odds_data

# Function to find arbitrage opportunities
def find_arbitrage(odds_list):
    arbitrage_opportunities = []
    grouped_events = {}
    
    # Group odds by event
    for event, sport, league, market, bookmaker, team1, odds1, bookmaker_link, team2, odds2, bookmaker_link2 in odds_list:
        if event not in grouped_events:
            grouped_events[event] = []
        grouped_events[event].append({
            'bookmaker': bookmaker,
            'team1': team1,
            'odds1': odds1,
            'link1': bookmaker_link,
            'team2': team2,
            'odds2': odds2,
            'link2': bookmaker_link2,
            'sport': sport,
            'league': league,
            'market': market
        })
    
    # Find arbitrage opportunities
    for event, bookmakers in grouped_events.items():
        for bm1, bm2 in itertools.combinations(bookmakers, 2):
            # Check team1 (bm1) vs team2 (bm2)
            implied_prob1 = 1/bm1['odds1']
            implied_prob2 = 1/bm2['odds2']
            total_prob = implied_prob1 + implied_prob2
            
            if total_prob < 1:  # Arbitrage opportunity found
                profit_margin = (1 - total_prob) * 100
                arbitrage_opportunities.append((
                    event,
                    bm1['sport'],
                    bm1['league'],
                    bm1['market'],
                    bm1['bookmaker'],
                    bm1['team1'],
                    bm1['odds1'],
                    bm1['link1'],
                    bm2['bookmaker'],
                    bm2['team2'],
                    bm2['odds2'],
                    bm2['link2'],
                    profit_margin
                ))
            
            # Check team2 (bm1) vs team1 (bm2)
            implied_prob1 = 1/bm1['odds2']
            implied_prob2 = 1/bm2['odds1']
            total_prob = implied_prob1 + implied_prob2
            
            if total_prob < 1:  # Arbitrage opportunity found
                profit_margin = (1 - total_prob) * 100
                arbitrage_opportunities.append((
                    event,
                    bm1['sport'],
                    bm1['league'],
                    bm1['market'],
                    bm1['bookmaker'],
                    bm1['team2'],
                    bm1['odds2'],
                    bm1['link1'],
                    bm2['bookmaker'],
                    bm2['team1'],
                    bm2['odds1'],
                    bm2['link2'],
                    profit_margin
                ))
    
    return arbitrage_opportunities

# Update database with new arbitrage opportunities
def update_arbitrage_opportunities():
    conn = sqlite3.connect("arbitrage_opportunities.db")
    cursor = conn.cursor()
    
    all_odds = fetch_odds()
    opportunities = find_arbitrage(all_odds)
    
    existing_opportunities = set()
    cursor.execute("SELECT event, bookmaker1, bookmaker2 FROM opportunities")
    for row in cursor.fetchall():
        existing_opportunities.add((row[0], row[1], row[2]))
    
    for event, sport, league, market, bm1, team1, odds1, link1, bm2, team2, odds2, link2, profit_margin in opportunities:
        # Get bookmaker links from the BOOKMAKER_LINKS dictionary
        bm1_link = BOOKMAKER_LINKS.get(bm1, "N/A")
        bm2_link = BOOKMAKER_LINKS.get(bm2, "N/A")
        
        if (event, bm1, bm2) in existing_opportunities:
            # Update existing opportunity
            cursor.execute('''UPDATE opportunities 
                            SET odds1 = ?, odds2 = ?, profit_margin = ?, timestamp = CURRENT_TIMESTAMP
                            WHERE event = ? AND bookmaker1 = ? AND bookmaker2 = ?''', 
                         (odds1, odds2, profit_margin, event, bm1, bm2))
        else:
            # Insert new opportunity
            cursor.execute('''INSERT INTO opportunities 
                            (event, sport, league, market, bookmaker1, team1, odds1, bookmaker1_link, 
                            bookmaker2, team2, odds2, bookmaker2_link, profit_margin)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                         (event, sport, league, market, bm1, team1, odds1, bm1_link, 
                          bm2, team2, odds2, bm2_link, profit_margin))
    
    # Remove old opportunities
    cursor.execute("DELETE FROM opportunities WHERE timestamp < DATETIME('now', '-5 minutes')")
    
    conn.commit()
    conn.close()
    print(f"Stored {len(opportunities)} arbitrage opportunities in database.")
if __name__ == "__main__":
    setup_database()
    max_retries = 3
    retry_count = 0
    
    while True:
        try:
            update_arbitrage_opportunities()
            print("Waiting 5 minutes before next update...")
            retry_count = 0  # Reset counter on successful run
            time.sleep(300)
        except requests.RequestException as e:
            print(f"API Request Error: {e}")
            retry_count += 1
        except sqlite3.Error as e:
            print(f"Database Error: {e}")
            retry_count += 1
        except Exception as e:
            print(f"Unexpected Error: {e}")
            retry_count += 1
        
        if retry_count >= max_retries:
            print("Maximum retry attempts reached. Exiting...")
            break
        
        print(f"Retrying in 320 seconds... (Attempt {retry_count}/{max_retries})")
        time.sleep(320)
