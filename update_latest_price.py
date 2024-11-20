import yfinance as yf
import sqlite3
from datetime import datetime

def update_latest_price():
    """Update the latest Bitcoin price in the database."""
    try:
        # Fetch the latest Bitcoin price
        btc = yf.download('BTC-USD', period='1d')
        if btc.empty:
            print("No data fetched for the latest Bitcoin price.")
            return False

        latest_price = round(float(btc['Close'][-1]), 2)  # Round to 2 decimal places
        date_str = datetime.now().strftime('%Y-%m-%d')
        btc_amount = 472226  # Amount of BTC that could be bought with 1% of reserves
        value_usd = round(latest_price * btc_amount, 2)  # Round to 2 decimal places

        # Connect to the database and update the price
        conn = sqlite3.connect('btc_data.db')
        cursor = conn.cursor()

        cursor.execute('''
        INSERT OR REPLACE INTO bitcoin_data (date, price_usd, value_usd)
        VALUES (?, ?, ?)
        ''', (date_str, latest_price, value_usd))

        conn.commit()
        conn.close()
        print(f"Updated latest price: ${latest_price}, Value: ${value_usd} on {date_str}")
        return True

    except Exception as e:
        print(f"Error updating latest price: {e}")
        return False

if __name__ == "__main__":
    update_latest_price()
