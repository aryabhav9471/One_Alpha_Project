import yfinance as yf
import pandas as pd
import mysql.connector
from datetime import datetime
import multiprocessing as mp
from time import sleep

# Database Credentials
mysql_host = 'sql12.freesqldatabase.com'
mysql_user = 'sql12766961'
mysql_password = 'VKqi5BgQpv'
mysql_database = 'sql12766961'

# Function to fetch stock data and insert into MySQL
def fetch_data(symbol):
    try:
        print(f"📡 Fetching data for {symbol}...")

        # Retrieve 1-day stock data
        data = yf.download(symbol, period='1d')

        if 'Adj Close' not in data.columns:
            print(f"⚠️ Skipping {symbol}: No 'Adj Close' data.")
            return

        data.reset_index(inplace=True)
        latest_date = datetime.now().date()  # Today's date

        # Filter only today's stock data
        filtered_data = data[data['Date'].dt.date == latest_date]
        if filtered_data.empty:
            print(f"⚠️ No new data for {symbol} today.")
            return

        # Convert 'Date' column to string format
        filtered_data['Date'] = filtered_data['Date'].dt.strftime('%Y-%m-%d %H:%M:%S')

        # SQL Insert Query
        insert_query = """
        INSERT INTO stock_data1 (symbol, date, adj_close, open, low, close, high)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        # Connect to MySQL
        cnx = mysql.connector.connect(
            host=mysql_host,
            user=mysql_user,
            password=mysql_password,
            database=mysql_database
        )
        cursor = cnx.cursor()

        # Check if data already exists
        existing_query = "SELECT COUNT(*) FROM stock_data1 WHERE symbol = %s AND date = %s"
        for _, row in filtered_data.iterrows():
            cursor.execute(existing_query, (symbol, row['Date']))
            if cursor.fetchone()[0] == 0:  # Insert only if not exists
                values = (symbol, row['Date'], row['Adj Close'], row['Open'], row['Low'], row['Close'], row['High'])
                cursor.execute(insert_query, values)
                print(f"✅ Inserted data for {symbol}")

        cnx.commit()
        cursor.close()
        cnx.close()

    except mysql.connector.Error as err:
        print(f"❌ MySQL Error for {symbol}: {err}")

    except Exception as e:
        print(f"❌ Error fetching {symbol}: {e}")

# Function to fetch and insert stock data using multiprocessing
def fetch_and_insert_data(symbols):
    with mp.Pool(processes=mp.cpu_count()) as pool:
        pool.map(fetch_data, symbols)

if __name__ == '__main__':
    # Load stock symbols from CSV
    df_symbols = pd.read_csv(r"D:\USERS HP\Desktop\DC_PROJECT\One_Alpha_Project\MOBILE_PROJECT1\Company_list1.csv")

    # Append ".NS" to each symbol
    df_symbols['symbol'] = df_symbols['symbol'] + '.NS'

    # Get the list of symbols
    symbols = df_symbols['symbol'].dropna().tolist()

    while True:
        fetch_and_insert_data(symbols)
        sleep(30)  # Fetch data every 30 seconds
