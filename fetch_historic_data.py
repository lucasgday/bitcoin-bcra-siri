import yfinance as yf
import sqlite3
import os
from datetime import datetime

def fetch_historical_data():
    print("Starting historical data fetch from 2014...")

    db_file = 'btc_data.db'

    if os.path.exists(db_file):
        try:
            os.remove(db_file)
            print(f"Existing database removed: {db_file}")
        except Exception as e:
            print(f"Error removing existing database: {e}")
            return

    btc = yf.download('BTC-USD',
                      start='2014-07-11',
                      end=datetime.now().strftime('%Y-%m-%d'))

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bitcoin_data (
        date TEXT PRIMARY KEY,
        price_usd REAL,
        value_usd REAL
    )
    ''')

    btc_amount = 472226
    records_added = 0

    for date, row in btc.iterrows():
        date_str = date.strftime('%Y-%m-%d')
        price_usd = round(float(row['Close']), 2)
        value_usd = round(price_usd * btc_amount, 2)

        try:
            cursor.execute('''
            INSERT OR REPLACE INTO bitcoin_data (date, price_usd, value_usd)
            VALUES (?, ?, ?)
            ''', (date_str, price_usd, value_usd))
            records_added += 1

            if records_added == 1:
                print(f"First record: Date={date_str}, Price=${price_usd:,.2f}, Value=${value_usd:,.2f}")

        except Exception as e:
            print(f"Error inserting data for {date_str}: {e}")
            continue

    conn.commit()
    conn.close()
    print(f"Historical data saved successfully. Added {records_added} records.")

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bitcoin_data ORDER BY date ASC LIMIT 1')
    first_record = cursor.fetchone()
    if first_record:
        print("\nVerification of first record:")
        print(f"Date: {first_record[0]}")
        print(f"Price: ${first_record[1]:,.2f}")
        print(f"Value: ${first_record[2]:,.2f}")
    conn.close()

if __name__ == "__main__":
    response = input("This will erase the existing database and create a new one. Continue? (y/n): ")
    if response.lower() == 'y':
        fetch_historical_data()
    else:
        print("Operation cancelled.")
