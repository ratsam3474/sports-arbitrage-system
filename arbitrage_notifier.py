import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

# Email configuration
EMAIL_SENDER = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password"
EMAIL_RECEIVER = "recipient@email.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Profit margin filter settings
MIN_PROFIT = 0.1
MAX_PROFIT = 0.2

def send_arbitrage_email(opportunities):
    if not opportunities:
        return
    
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = f"Arbitrage Opportunities Alert ({len(opportunities)} matches)"
    
    body = "Current arbitrage opportunities:\n\n"
    for opp in opportunities:
        body += f"""
Event: {opp[1]}
Sport: {opp[2]}
League: {opp[3]}
Bookmaker 1: {opp[5]} ({opp[6]} @ {opp[7]:.2f})
Bookmaker 2: {opp[9]} ({opp[10]} @ {opp[11]:.2f})
Profit Margin: {opp[13]:.2f}%
Bookmaker 1 Link: {opp[8]}
Bookmaker 2 Link: {opp[12]}
Timestamp: {opp[14]}
------------------------
"""
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        print(f"Email sent successfully with {len(opportunities)} opportunities")
    except Exception as e:
        print(f"Failed to send email: {e}")
    finally:
        server.quit()

def check_opportunities():
    try:
        conn = sqlite3.connect("arbitrage_opportunities.db")
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT *
            FROM opportunities
            WHERE profit_margin BETWEEN ? AND ?
            ORDER BY profit_margin DESC
        """, (MIN_PROFIT, MAX_PROFIT))
        
        opportunities = cursor.fetchall()
        
        if opportunities:
            print(f"Found {len(opportunities)} opportunities within profit range {MIN_PROFIT}% - {MAX_PROFIT}%")
            send_arbitrage_email(opportunities)
        else:
            print("No opportunities found in the specified profit range")
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

def main():
    print(f"Starting arbitrage notification service...")
    print(f"Monitoring for opportunities with profit between {MIN_PROFIT}% and {MAX_PROFIT}%")
    
    while True:
        try:
            check_opportunities()
            print("\nWaiting 5 minutes before next check...")
            time.sleep(300)  # Check every 5 minutes
        except KeyboardInterrupt:
            print("\nStopping the notification service...")
            break
        except Exception as e:
            print(f"Error occurred: {e}")
            print("Waiting 1 minute before retry...")
            time.sleep(60)

if __name__ == "__main__":
    main() 