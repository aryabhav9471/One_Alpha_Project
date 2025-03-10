import yfinance as yf
import pandas as pd
import mysql.connector
import os
import multiprocessing as mp
from datetime import datetime
from time import sleep

# Fetch database credentials from environment variables
MYSQL_HOST = os.getenv("DB_HOST", "sql12.freesqldatabase.com")
MYSQL_USER = os.getenv("DB_USER", "sql12766961")
MYSQL_PASSWORD = os.getenv("DB_PASSWORD", "VKqi5BgQpv")  # Change before deployment
MYSQL_DATABASE = os.getenv("DB_NAME", "sql12766961")
MYSQL_PORT = int(os.getenv("DB_PORT", 3306))

# Function to establish a MySQL connection
def get_db_connection():
    try:
        return mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
            port=MYSQL_PORT
        )
    except mysql.connector.Error as err:
        print(f"❌ Database connection error: {err}")
        return None

# Function to fetch stock data and insert into MySQL
def fetch_data(symbol):
    try:
        print(f"📡 Fetching data for {symbol}...")
        data = yf.download(symbol, period='1d')

        if 'Adj Close' not in data.columns:
            print(f"⚠️ Skipping {symbol}: No 'Adj Close' column in data.")
            return

        data.reset_index(inplace=True)
        latest_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Filter required columns
        filtered_data = data[['Date', 'Adj Close', 'Open', 'Low', 'Close', 'High']].copy()
        filtered_data['Date'] = latest_date  # Use the current timestamp

        # Prepare SQL query
        insert_query = """
        INSERT INTO stock_data1 (symbol, date, adj_close, open, low, close, high)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        # Connect to MySQL
        cnx = get_db_connection()
        if not cnx:
            return  # Skip if no connection

        cursor = cnx.cursor()

        # Check for existing data
        existing_query = "SELECT COUNT(*) FROM stock_data1 WHERE symbol = %s AND date = %s"
        for _, row in filtered_data.iterrows():
            cursor.execute(existing_query, (symbol, row['Date']))
            if cursor.fetchone()[0] == 0:  # Insert only if not exists
                values = (symbol, row['Date'], row['Adj Close'], row['Open'], row['Low'], row['Close'], row['High'])
                cursor.execute(insert_query, values)

        cnx.commit()
        cursor.close()
        cnx.close()

        print(f"✅ Updated {symbol} at {latest_date}")

    except mysql.connector.Error as err:
        print(f"❌ MySQL Error for {symbol}: {err}")

    except Exception as e:
        print(f"❌ Error fetching {symbol}: {e}")

# Function to handle multiprocessing
def fetch_and_insert_data(symbols):
    with mp.Pool(processes=mp.cpu_count()) as pool:
        pool.map(fetch_data, symbols)

if __name__ == '__main__':
    try:
        # Load stock symbols from CSV
        df_symbols = pd.read_csv('Company_list1.csv')
        df_symbols['symbol'] = df_symbols['symbol'] + '.NS'
        symbols = df_symbols['symbol'].dropna().tolist()

        while True:
            fetch_and_insert_data(symbols)
            sleep(30)  # Fetch data every 30 seconds

    except Exception as e:
        print(f"❌ Error in main loop: {e}")
