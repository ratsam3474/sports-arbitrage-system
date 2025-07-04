import json 
import requests 
import sqlite3
import itertools
import time
import os
import datetime  # Add datetime module

# Get the directory where the script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "arbitrage_opportunities.db")

# ========================= FILTER CONFIGURATION =========================
# Set to None or empty list to include all options

# Bookmakers to include in arbitrage search (set to None to include all)
ENABLED_BOOKMAKERS = []

# Profit margin range (percentage)
MIN_PROFIT_MARGIN = 0.5  # Minimum profit margin to consider (%)
MAX_PROFIT_MARGIN = 5.0  # Maximum profit margin to consider (%) - very high margins might indicate errors

# Sports to include (set to None to include all)
ENABLED_SPORTS = []

# Bet types to include
ENABLED_BET_TYPES = ["Moneyline", "Over/Under"]

# Time criteria for events
MAX_HOURS_UNTIL_EVENT = 24  # Only consider events within this many hours

# ====================================================================

# API Key for The-Odds-API (Replace with your actual key)
API_KEY = ""  # Replace with your The-Odds-API key
BASE_URL = "https://api.the-odds-api.com/v4/sports/{sport_key}/odds"

# List of sports and leagues to track
SPORTS = [
    # American Football
    "americanfootball_cfl", "americanfootball_ncaaf", "americanfootball_nfl", 
    "americanfootball_nfl_preseason", "americanfootball_ufl",
    
    # Aussie Rules
    #"aussierules_afl",
    
    # Baseball
    "baseball_mlb", "baseball_milb", "baseball_npb", "baseball_kbo", "baseball_ncaa",
    
    # Basketball
    "basketball_euroleague", "basketball_nba", "basketball_wnba", "basketball_ncaab", 
    "basketball_wncaab", "basketball_nbl",
    
    # Ice Hockey
    "icehockey_nhl", "icehockey_ahl", "icehockey_liiga", "icehockey_mestis",
    "icehockey_sweden_hockey_league", "icehockey_sweden_allsvenskan",
    
    # Rugby League
    "rugbyleague_nrl",
    
    # Soccer
    "soccer_argentina_primera_division", "soccer_australia_aleague", "soccer_austria_bundesliga",
    "soccer_belgium_first_div", "soccer_brazil_campeonato", "soccer_brazil_serie_b",
    "soccer_chile_campeonato", "soccer_china_superleague", "soccer_denmark_superliga",
    "soccer_efl_champ", "soccer_england_efl_cup", "soccer_england_league1",
    "soccer_england_league2", "soccer_epl", "soccer_fa_cup", "soccer_fifa_world_cup",
    "soccer_fifa_world_cup_womens", "soccer_finland_veikkausliiga", "soccer_france_ligue_one",
    "soccer_france_ligue_two", "soccer_germany_bundesliga", "soccer_germany_bundesliga2",
    "soccer_germany_liga3", "soccer_greece_super_league", "soccer_italy_serie_a",
    "soccer_italy_serie_b", "soccer_japan_j_league", "soccer_korea_kleague1",
    "soccer_league_of_ireland", "soccer_mexico_ligamx", "soccer_netherlands_eredivisie",
    "soccer_norway_eliteserien", "soccer_poland_ekstraklasa", "soccer_portugal_primeira_liga",
    "soccer_spain_la_liga", "soccer_spain_segunda_division", "soccer_spl",
    "soccer_sweden_allsvenskan", "soccer_sweden_superettan", "soccer_switzerland_superleague",
    "soccer_turkey_super_league", "soccer_uefa_europa_conference_league", "soccer_uefa_champs_league",
    "soccer_uefa_champs_league_qualification", "soccer_uefa_europa_league", 
    "soccer_uefa_european_championship", "soccer_uefa_euro_qualification",
    "soccer_conmebol_copa_america", "soccer_conmebol_copa_libertadores", "soccer_usa_mls",
    
    # Tennis
    "tennis_atp_aus_open_singles", "tennis_atp_canadian_open", "tennis_atp_china_open",
    "tennis_atp_cincinnati_open", "tennis_atp_dubai", "tennis_atp_french_open",
    "tennis_atp_indian_wells", "tennis_atp_miami_open", "tennis_atp_paris_masters",
    "tennis_atp_qatar_open", "tennis_atp_shanghai_masters", "tennis_atp_us_open",
    "tennis_atp_wimbledon", "tennis_wta_aus_open_singles", "tennis_wta_canadian_open",
    "tennis_wta_china_open", "tennis_wta_cincinnati_open", "tennis_wta_dubai",
    "tennis_wta_french_open", "tennis_wta_indian_wells", "tennis_wta_miami_open",
    "tennis_wta_qatar_open", "tennis_wta_us_open", "tennis_wta_wimbledon",
    "tennis_wta_wuhan_open"
]

MARKETS = ["totals", "h2h"]  # Supported betting markets

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
    # Delete existing database if it exists
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            print("Removed existing database file.")
        except Exception as e:
            print(f"Error removing existing database: {e}")
    
    # Create new database with updated structure
    conn = sqlite3.connect(DB_PATH)
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
                        bet1 TEXT,
                        bookmaker2 TEXT,
                        team2 TEXT,
                        odds2 REAL,
                        bookmaker2_link TEXT,
                        bet2 TEXT,
                        profit_margin REAL,
                        total_line TEXT,
                        bet_type TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )''')
    conn.commit()
    conn.close()
    print("Created new database with updated structure.")

# Function to fetch odds from The-Odds-API
def fetch_odds():
    odds_data = []
    current_time = datetime.datetime.now(datetime.timezone.utc)  # Get current time in UTC
    
    # Filter sports based on enabled sports
    sports_to_fetch = ENABLED_SPORTS if ENABLED_SPORTS else SPORTS
    
    for sport in sports_to_fetch:
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
            try:
                response = requests.get(url, params=params)
                
                if response.status_code != 200:
                    try:
                        error_response = response.json()
                        print(f"⚠️ Error fetching odds for Sport: {sport}, Market: {market}")
                        print(f"Message: {error_response.get('message', 'No message')}")
                        print(f"Error Code: {error_response.get('error_code', 'No code')}")
                        print(f"Details: {error_response.get('details_url', 'No details provided')}")
                    except Exception as e:
                        print(f"⚠️ Unexpected error fetching odds for Sport: {sport}, Market: {market}")
                        print(f"Response Content: {response.text}")
                        print(f"Error: {str(e)}")
                    continue
                
                data = response.json()
                
                for event in data:
                    try:
                        # Parse commence_time to datetime object
                        commence_time_str = event.get('commence_time')
                        commence_time = datetime.datetime.fromisoformat(commence_time_str.replace('Z', '+00:00'))
                        
                        # Calculate time difference in hours
                        time_diff = commence_time - current_time
                        hours_until_event = time_diff.total_seconds() / 3600
                        
                        # Skip events that start more than MAX_HOURS_UNTIL_EVENT hours from now
                        if hours_until_event > MAX_HOURS_UNTIL_EVENT:
                            print(f"Skipping event starting in {hours_until_event:.1f} hours: {event.get('home_team', '')} vs {event.get('away_team', '')}")
                            continue
                            
                        print(f"Processing event starting in {hours_until_event:.1f} hours: {event.get('home_team', '')} vs {event.get('away_team', '')}")
                        
                        event_name = event['sport_title'] + " - " + event['commence_time']
                        sport_name = event['sport_title']
                        league = event.get('sport_key', sport)
                        bookmakers = event.get('bookmakers', [])
                        
                        # Get team names from the event
                        home_team = event.get('home_team', '')
                        away_team = event.get('away_team', '')
                        
                        # Filter bookmakers if enabled
                        if ENABLED_BOOKMAKERS:
                            bookmakers = [bm for bm in bookmakers if bm['title'] in ENABLED_BOOKMAKERS]
                        
                        for bookmaker in bookmakers:
                            try:
                                bookmaker_name = bookmaker['title']
                                bookmaker_link = bookmaker.get('links', {}).get('event', "N/A")
                                markets = bookmaker.get('markets', [])
                                
                                for market_data in markets:
                                    try:
                                        market_key = market_data.get('key')
                                        if market_key == 'totals':
                                            # Check if Over/Under bet type is enabled
                                            if ENABLED_BET_TYPES and "Over/Under" not in ENABLED_BET_TYPES:
                                                continue
                                                
                                            outcomes = market_data.get('outcomes', [])
                                            if not outcomes:
                                                continue
                                            
                                            print(f"\nProcessing outcomes for {event_name} at {bookmaker_name}:")
                                            print(f"All outcomes: {outcomes}")
                                                
                                            # Find Over and Under options
                                            over_option = None
                                            under_option = None
                                            
                                            for outcome in outcomes:
                                                name = outcome.get('name', '')
                                                print(f"Checking outcome: {name}")
                                                if 'Over' in name:
                                                    over_option = outcome
                                                elif 'Under' in name:
                                                    under_option = outcome
                                            
                                            if over_option and under_option:
                                                try:
                                                    # Get the total line from the point field
                                                    total_line = str(over_option.get('point', ''))
                                                    print(f"Found total line from point field: {total_line}")
                                                    
                                                    if not total_line:
                                                        print("No total line found in point field")
                                                        continue
                                                    
                                                    odds_data.append((
                                                        event_name,
                                                        sport_name,
                                                        league,
                                                        market,
                                                        bookmaker_name,
                                                        home_team,  # Keep original team names
                                                        over_option['price'],
                                                        bookmaker_link,
                                                        away_team,  # Keep original team names
                                                        under_option['price'],
                                                        bookmaker_link,
                                                        total_line,  # Add total line
                                                        "Over/Under"  # Add bet type
                                                    ))
                                                    print(f"Successfully processed: Over/Under {total_line} at {bookmaker_name}")
                                                except (KeyError, IndexError) as e:
                                                    print(f"Error processing odds data for {bookmaker_name}: {e}")
                                                    print(f"Over option: {over_option}")
                                                    print(f"Under option: {under_option}")
                                                    continue
                                        elif market_key == 'h2h':
                                            # Check if Moneyline bet type is enabled
                                            if ENABLED_BET_TYPES and "Moneyline" not in ENABLED_BET_TYPES:
                                                continue
                                                
                                            outcomes = market_data.get('outcomes', [])
                                            
                                            # Ensure this is a two-way market (just home and away, no draw)
                                            if len(outcomes) != 2:
                                                print(f"Skipping h2h with {len(outcomes)} outcomes - only handling two-way markets")
                                                continue
                                                
                                            print(f"\nProcessing h2h outcomes for {event_name} at {bookmaker_name}:")
                                            print(f"All outcomes: {outcomes}")
                                            
                                            # Find odds for home and away teams
                                            home_odds = None
                                            away_odds = None
                                            
                                            for outcome in outcomes:
                                                team_name = outcome.get('name', '')
                                                if team_name == home_team:
                                                    home_odds = outcome.get('price')
                                                elif team_name == away_team:
                                                    away_odds = outcome.get('price')
                                            
                                            if home_odds and away_odds:
                                                odds_data.append((
                                                    event_name,
                                                    sport_name,
                                                    league,
                                                    market_key,
                                                    bookmaker_name,
                                                    home_team,
                                                    home_odds,
                                                    bookmaker_link,
                                                    away_team,
                                                    away_odds,
                                                    bookmaker_link,
                                                    "N/A",  # No total line for h2h
                                                    "Moneyline"  # Bet type is moneyline for h2h
                                                ))
                                                print(f"Successfully processed: Two-way H2H odds for {home_team} vs {away_team} at {bookmaker_name}")
                                    except Exception as e:
                                        print(f"Error processing market data: {e}")
                                        continue
                            except Exception as e:
                                print(f"Error processing bookmaker data: {e}")
                                continue
                    except Exception as e:
                        print(f"Error processing event data: {e}")
                        continue
            except Exception as e:
                print(f"Error making API request: {e}")
                continue
    
    return odds_data

# Function to find arbitrage opportunities
def find_arbitrage(odds_list):
    global MIN_PROFIT_MARGIN, MAX_PROFIT_MARGIN  # Ensure access to filter variables
    
    arbitrage_opportunities = []
    
    # Debug: Print filter settings
    print(f"\n=== DEBUG: Filter settings ===")
    print(f"MIN_PROFIT_MARGIN: {MIN_PROFIT_MARGIN} (type: {type(MIN_PROFIT_MARGIN)})")
    print(f"MAX_PROFIT_MARGIN: {MAX_PROFIT_MARGIN} (type: {type(MAX_PROFIT_MARGIN)})")
    
    # Ensure filter values are floats
    MIN_PROFIT_MARGIN = float(MIN_PROFIT_MARGIN) if MIN_PROFIT_MARGIN is not None else None
    MAX_PROFIT_MARGIN = float(MAX_PROFIT_MARGIN) if MAX_PROFIT_MARGIN is not None else None
    
    # Group odds by event and market type
    grouped_events = {}
    for event, sport, league, market, bookmaker, home_team, odds1, bookmaker_link, away_team, odds2, bookmaker_link2, total_line, bet_type in odds_list:
        event_market_key = f"{event} - {market}"
        
        if event_market_key not in grouped_events:
            grouped_events[event_market_key] = []
        
        grouped_events[event_market_key].append({
            'bookmaker': bookmaker,
            'home_team': home_team,
            'away_team': away_team,
            'home_odds': odds1,  # For h2h, this is home team odds; for totals, this is over odds
            'away_odds': odds2,  # For h2h, this is away team odds; for totals, this is under odds
            'link': bookmaker_link,
            'sport': sport,
            'league': league,
            'market': market,
            'total_line': total_line,
            'bet_type': bet_type
        })
    
    # Find arbitrage opportunities (two-way only)
    for event_key, bookmakers in grouped_events.items():
        # Get common information from the first bookmaker
        market = bookmakers[0]['market']
        
        if market == 'totals':
            # Process two-way totals (over/under) markets
            for bm1, bm2 in itertools.combinations(bookmakers, 2):
                # Skip if same bookmaker
                if bm1['bookmaker'] == bm2['bookmaker']:
                    continue
                    
                # Check Over (bm1) vs Under (bm2)
                implied_prob1 = 1/bm1['home_odds']  # Over odds
                implied_prob2 = 1/bm2['away_odds']  # Under odds
                total_prob = implied_prob1 + implied_prob2
                
                if total_prob < 1:  # Two-way arbitrage opportunity found
                    # FIXED: Use correct profit margin formula
                    profit_margin = ((1 - total_prob) / total_prob) * 100
                    
                    # Debug the filtering logic
                    print(f"\n=== DEBUG: Checking totals opportunity (Over vs Under) ===")
                    print(f"Event: {event_key}")
                    print(f"Bookmaker 1: {bm1['bookmaker']} (Over)")
                    print(f"Bookmaker 2: {bm2['bookmaker']} (Under)")
                    print(f"Calculated profit_margin: {profit_margin:.4f}%")
                    print(f"MIN check: {MIN_PROFIT_MARGIN is not None and profit_margin < MIN_PROFIT_MARGIN if MIN_PROFIT_MARGIN is not None else 'N/A'}")
                    print(f"MAX check: {MAX_PROFIT_MARGIN is not None and profit_margin > MAX_PROFIT_MARGIN if MAX_PROFIT_MARGIN is not None else 'N/A'}")
                    
                    # Check minimum profit margin
                    if MIN_PROFIT_MARGIN is not None and profit_margin < MIN_PROFIT_MARGIN:
                        print(f"❌ FILTERED OUT: profit_margin ({profit_margin:.4f}) < MIN_PROFIT_MARGIN ({MIN_PROFIT_MARGIN})")
                        continue
                    
                    # Check maximum profit margin
                    if MAX_PROFIT_MARGIN is not None and profit_margin > MAX_PROFIT_MARGIN:
                        print(f"❌ FILTERED OUT: profit_margin ({profit_margin:.4f}) > MAX_PROFIT_MARGIN ({MAX_PROFIT_MARGIN})")
                        continue
                    
                    print(f"✅ PASSED FILTER: Adding opportunity with {profit_margin:.4f}% profit margin")
                    
                    bet1 = f"Over {bm1['total_line']}"
                    bet2 = f"Under {bm2['total_line']}"
                    home_team = bm1['home_team']
                    away_team = bm1['away_team']
                    
                    arbitrage_opportunities.append((
                        event_key,
                        bm1['sport'],
                        bm1['league'],
                        bm1['market'],
                        bm1['bookmaker'],
                        f"{home_team} vs {away_team}",
                        bm1['home_odds'],
                        bm1['link'],
                        bet1,
                        bm2['bookmaker'],
                        f"{home_team} vs {away_team}",
                        bm2['away_odds'],
                        bm2['link'],
                        bet2,
                        profit_margin,
                        f"{bet1} / {bet2}",
                        "Over/Under"
                    ))
                
                # Check Under (bm1) vs Over (bm2)
                implied_prob1 = 1/bm1['away_odds']  # Under odds
                implied_prob2 = 1/bm2['home_odds']  # Over odds
                total_prob = implied_prob1 + implied_prob2
                
                if total_prob < 1:  # Two-way arbitrage opportunity found
                    # FIXED: Use correct profit margin formula
                    profit_margin = ((1 - total_prob) / total_prob) * 100
                    
                    # Debug the filtering logic
                    print(f"\n=== DEBUG: Checking totals opportunity (Under vs Over) ===")
                    print(f"Event: {event_key}")
                    print(f"Bookmaker 1: {bm1['bookmaker']} (Under)")
                    print(f"Bookmaker 2: {bm2['bookmaker']} (Over)")
                    print(f"Calculated profit_margin: {profit_margin:.4f}%")
                    print(f"MIN check: {MIN_PROFIT_MARGIN is not None and profit_margin < MIN_PROFIT_MARGIN if MIN_PROFIT_MARGIN is not None else 'N/A'}")
                    print(f"MAX check: {MAX_PROFIT_MARGIN is not None and profit_margin > MAX_PROFIT_MARGIN if MAX_PROFIT_MARGIN is not None else 'N/A'}")
                    
                    # Check minimum profit margin
                    if MIN_PROFIT_MARGIN is not None and profit_margin < MIN_PROFIT_MARGIN:
                        print(f"❌ FILTERED OUT: profit_margin ({profit_margin:.4f}) < MIN_PROFIT_MARGIN ({MIN_PROFIT_MARGIN})")
                        continue
                    
                    # Check maximum profit margin
                    if MAX_PROFIT_MARGIN is not None and profit_margin > MAX_PROFIT_MARGIN:
                        print(f"❌ FILTERED OUT: profit_margin ({profit_margin:.4f}) > MAX_PROFIT_MARGIN ({MAX_PROFIT_MARGIN})")
                        continue
                    
                    print(f"✅ PASSED FILTER: Adding opportunity with {profit_margin:.4f}% profit margin")
                    
                    bet1 = f"Under {bm1['total_line']}"
                    bet2 = f"Over {bm2['total_line']}"
                    home_team = bm1['home_team']
                    away_team = bm1['away_team']
                    
                    arbitrage_opportunities.append((
                        event_key,
                        bm1['sport'],
                        bm1['league'],
                        bm1['market'],
                        bm1['bookmaker'],
                        f"{home_team} vs {away_team}",
                        bm1['away_odds'],  # Under odds for bm1
                        bm1['link'],
                        bet1,
                        bm2['bookmaker'],
                        f"{home_team} vs {away_team}",
                        bm2['home_odds'],  # Over odds for bm2
                        bm2['link'],
                        bet2,
                        profit_margin,
                        f"{bet1} / {bet2}",
                        "Over/Under"
                    ))
        
        elif market == 'h2h':
            # Process two-way h2h (moneyline) markets
            for bm1, bm2 in itertools.combinations(bookmakers, 2):
                # Skip if same bookmaker
                if bm1['bookmaker'] == bm2['bookmaker']:
                    continue
                
                home_team = bm1['home_team']
                away_team = bm1['away_team']
                
                # Check Home (bm1) vs Away (bm2)
                implied_prob1 = 1/bm1['home_odds']  # Home team odds at bm1
                implied_prob2 = 1/bm2['away_odds']  # Away team odds at bm2
                total_prob = implied_prob1 + implied_prob2
                
                if total_prob < 1:  # Two-way arbitrage opportunity found
                    # FIXED: Use correct profit margin formula
                    profit_margin = ((1 - total_prob) / total_prob) * 100
                    
                    # Debug the filtering logic
                    print(f"\n=== DEBUG: Checking h2h opportunity (Home vs Away) ===")
                    print(f"Event: {event_key}")
                    print(f"Bookmaker 1: {bm1['bookmaker']} ({home_team})")
                    print(f"Bookmaker 2: {bm2['bookmaker']} ({away_team})")
                    print(f"Calculated profit_margin: {profit_margin:.4f}%")
                    print(f"MIN check: {MIN_PROFIT_MARGIN is not None and profit_margin < MIN_PROFIT_MARGIN if MIN_PROFIT_MARGIN is not None else 'N/A'}")
                    print(f"MAX check: {MAX_PROFIT_MARGIN is not None and profit_margin > MAX_PROFIT_MARGIN if MAX_PROFIT_MARGIN is not None else 'N/A'}")
                    
                    # Check minimum profit margin
                    if MIN_PROFIT_MARGIN is not None and profit_margin < MIN_PROFIT_MARGIN:
                        print(f"❌ FILTERED OUT: profit_margin ({profit_margin:.4f}) < MIN_PROFIT_MARGIN ({MIN_PROFIT_MARGIN})")
                        continue
                    
                    # Check maximum profit margin
                    if MAX_PROFIT_MARGIN is not None and profit_margin > MAX_PROFIT_MARGIN:
                        print(f"❌ FILTERED OUT: profit_margin ({profit_margin:.4f}) > MAX_PROFIT_MARGIN ({MAX_PROFIT_MARGIN})")
                        continue
                    
                    print(f"✅ PASSED FILTER: Adding opportunity with {profit_margin:.4f}% profit margin")
                    
                    bet1 = f"{home_team} (Win)"
                    bet2 = f"{away_team} (Win)"
                    
                    arbitrage_opportunities.append((
                        event_key,
                        bm1['sport'],
                        bm1['league'],
                        bm1['market'],
                        bm1['bookmaker'],
                        f"{home_team} vs {away_team}",
                        bm1['home_odds'],
                        bm1['link'],
                        bet1,
                        bm2['bookmaker'],
                        f"{home_team} vs {away_team}",
                        bm2['away_odds'],
                        bm2['link'],
                        bet2,
                        profit_margin,
                        f"{bet1} / {bet2}",
                        "Moneyline"
                    ))
                
                # Check Away (bm1) vs Home (bm2)
                implied_prob1 = 1/bm1['away_odds']  # Away team odds at bm1
                implied_prob2 = 1/bm2['home_odds']  # Home team odds at bm2
                total_prob = implied_prob1 + implied_prob2
                
                if total_prob < 1:  # Two-way arbitrage opportunity found
                    # FIXED: Use correct profit margin formula
                    profit_margin = ((1 - total_prob) / total_prob) * 100
                    
                    # Debug the filtering logic
                    print(f"\n=== DEBUG: Checking h2h opportunity (Away vs Home) ===")
                    print(f"Event: {event_key}")
                    print(f"Bookmaker 1: {bm1['bookmaker']} ({away_team})")
                    print(f"Bookmaker 2: {bm2['bookmaker']} ({home_team})")
                    print(f"Calculated profit_margin: {profit_margin:.4f}%")
                    print(f"MIN check: {MIN_PROFIT_MARGIN is not None and profit_margin < MIN_PROFIT_MARGIN if MIN_PROFIT_MARGIN is not None else 'N/A'}")
                    print(f"MAX check: {MAX_PROFIT_MARGIN is not None and profit_margin > MAX_PROFIT_MARGIN if MAX_PROFIT_MARGIN is not None else 'N/A'}")
                    
                    # Check minimum profit margin
                    if MIN_PROFIT_MARGIN is not None and profit_margin < MIN_PROFIT_MARGIN:
                        print(f"❌ FILTERED OUT: profit_margin ({profit_margin:.4f}) < MIN_PROFIT_MARGIN ({MIN_PROFIT_MARGIN})")
                        continue
                    
                    # Check maximum profit margin
                    if MAX_PROFIT_MARGIN is not None and profit_margin > MAX_PROFIT_MARGIN:
                        print(f"❌ FILTERED OUT: profit_margin ({profit_margin:.4f}) > MAX_PROFIT_MARGIN ({MAX_PROFIT_MARGIN})")
                        continue
                    
                    print(f"✅ PASSED FILTER: Adding opportunity with {profit_margin:.4f}% profit margin")
                    
                    bet1 = f"{away_team} (Win)"
                    bet2 = f"{home_team} (Win)"
                    
                    arbitrage_opportunities.append((
                        event_key,
                        bm1['sport'],
                        bm1['league'],
                        bm1['market'],
                        bm1['bookmaker'],
                        f"{home_team} vs {away_team}",
                        bm1['away_odds'],
                        bm1['link'],
                        bet1,
                        bm2['bookmaker'],
                        f"{home_team} vs {away_team}",
                        bm2['home_odds'],
                        bm2['link'],
                        bet2,
                        profit_margin,
                        f"{bet1} / {bet2}",
                        "Moneyline"
                    ))
    
    # Sort opportunities by profit margin (highest first)
    arbitrage_opportunities.sort(key=lambda x: x[14], reverse=True)
    
    # Debug: Final results
    print(f"\n=== DEBUG: Final Results ===")
    print(f"Total opportunities after filtering: {len(arbitrage_opportunities)}")
    for i, opp in enumerate(arbitrage_opportunities[:5]):  # Show first 5
        print(f"  {i+1}. Profit margin: {opp[14]:.4f}%")
    
    return arbitrage_opportunities

# Function to update database with new arbitrage opportunities
def update_arbitrage_opportunities():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    all_odds = fetch_odds()
    opportunities = find_arbitrage(all_odds)
    
    existing_opportunities = set()
    cursor.execute("SELECT event, bookmaker1, bookmaker2 FROM opportunities")
    for row in cursor.fetchall():
        existing_opportunities.add((row[0], row[1], row[2]))
    
    new_opportunities = 0
    for event, sport, league, market, bm1, team1, odds1, link1, bet1, bm2, team2, odds2, link2, bet2, profit_margin, total_line, bet_type in opportunities:
        # Get bookmaker links from the BOOKMAKER_LINKS dictionary
        bm1_link = BOOKMAKER_LINKS.get(bm1, "N/A")
        bm2_link = BOOKMAKER_LINKS.get(bm2, "N/A")
        
        if (event, bm1, bm2) in existing_opportunities:
            # Update existing opportunity
            cursor.execute('''UPDATE opportunities 
                            SET odds1 = ?, odds2 = ?, profit_margin = ?, timestamp = CURRENT_TIMESTAMP,
                                total_line = ?, bet_type = ?, bet1 = ?, bet2 = ?
                            WHERE event = ? AND bookmaker1 = ? AND bookmaker2 = ?''', 
                         (odds1, odds2, profit_margin, total_line, bet_type, bet1, bet2, event, bm1, bm2))
        else:
            # Insert new opportunity
            cursor.execute('''INSERT INTO opportunities 
                            (event, sport, league, market, bookmaker1, team1, odds1, bookmaker1_link, bet1,
                            bookmaker2, team2, odds2, bookmaker2_link, bet2, profit_margin, total_line, bet_type)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                         (event, sport, league, market, bm1, team1, odds1, bm1_link, bet1,
                          bm2, team2, odds2, bm2_link, bet2, profit_margin, total_line, bet_type))
            new_opportunities += 1
    
    # Print results to the console
    print("=== FILTER SETTINGS ===")
    print(f"Bookmakers: {ENABLED_BOOKMAKERS if ENABLED_BOOKMAKERS else 'All'}")
    print(f"Sports: {ENABLED_SPORTS if ENABLED_SPORTS else 'All'}")
    print(f"Bet Types: {ENABLED_BET_TYPES if ENABLED_BET_TYPES else 'All'}")
    print(f"Profit Range: {MIN_PROFIT_MARGIN}% - {MAX_PROFIT_MARGIN}%")
    print(f"Max Hours Until Event: {MAX_HOURS_UNTIL_EVENT}")
    print(f"Found {len(opportunities)} arbitrage opportunities matching your filters")
    
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
            time.sleep(1000)
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
