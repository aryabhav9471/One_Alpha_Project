import yfinance as yf
import pandas as pd
import mysql.connector
from datetime import datetime, timedelta
import multiprocessing as mp
from time import sleep
import time

# Specify MySQL connection details
mysql_host = 'localhost'
mysql_user = 'root'
mysql_password = 'Aryabhav@2004'
mysql_database = 'stock'

def fetch_data(args):
    symbol, start_time = args
    try:
        # Retrieve the latest data for the symbol
        data = yf.download(symbol, period='1d')

        # Check if the 'Adj Close' column exists in the DataFrame
        if 'Adj Close' in data.columns:
            # Reset the index of the DataFrame
            data.reset_index(inplace=True)

            # Filter data for unique date and symbol
            latest_date = datetime.now().date()
            filtered_data = data[data['Date'].dt.date >= latest_date]
            filtered_data = filtered_data[['Date', 'Adj Close', 'Open', 'Low', 'Close', 'High']].copy()

            # Format the date column with the current timestamp
            filtered_data['Date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Prepare the SQL query to insert the new data
            insert_query = "INSERT INTO stock_data1 (symbol, date, adj_close, open, low, close, high) VALUES (%s, %s, %s, %s, %s, %s, %s)"

            # Establish connection to MySQL
            cnx = mysql.connector.connect(
                host=mysql_host,
                user=mysql_user,
                password=mysql_password,
                database=mysql_database
            )
            cursor = cnx.cursor()

            # Check for existing data with the same timestamp
            existing_query = "SELECT COUNT(*) FROM stock_data1 WHERE symbol = %s AND date = %s"
            for _, row in filtered_data.iterrows():
                cursor.execute(existing_query, (symbol, row['Date']))
                count = cursor.fetchone()[0]
                if count == 0:
                    # Insert the new data into the table
                    values = (symbol, row['Date'], row['Adj Close'], row['Open'], row['Low'], row['Close'], row['High'])
                    cursor.execute(insert_query, values)

            # Commit the changes to the database
            cnx.commit()

            # Close the cursor and connection
            cursor.close()
            cnx.close()

            print(f"Data fetched and inserted for symbol: {symbol}")
        else:
            print(f"Error: 'Adj Close' column not found in data for symbol: {symbol}")

    except mysql.connector.Error as err:
        print("MySQL Error:", err)

    except Exception as e:
        print(f"Error: An exception occurred for symbol: {symbol}")
        print(str(e))


def fetch_and_insert_data(symbols):
    start_time = datetime.now().time()
    pool = mp.Pool(processes=mp.cpu_count())
    results = pool.map(fetch_data, [(symbol, start_time) for symbol in symbols])
    pool.close()
    pool.join()


if __name__ == '__main__':
    # Load the CSV file containing stock symbols
    df_symbols = pd.read_csv('Company_list1.csv')

    # Append ".NS" to each symbol
    df_symbols['symbol'] = df_symbols['symbol'] + '.NS'

    # Get the list of symbols
    symbols = df_symbols['symbol'].dropna().tolist()

    while True:
        fetch_and_insert_data(symbols)
        sleep(30)  # Wait for 30 seconds before fetching data again
