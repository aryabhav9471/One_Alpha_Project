import yfinance as yf
import pandas as pd
import mysql.connector
import multiprocessing
import numpy as np
import time

def fetch_and_insert_data(symbols):
    # Specify MySQL connection details
    mysql_host = 'localhost'
    mysql_user = 'root'
    mysql_password = 'Aryabhav@2004'
    mysql_database = 'stock'

    # Establish connection to MySQL
    cnx = mysql.connector.connect(
        host=mysql_host,
        user=mysql_user,
        password=mysql_password,
        database=mysql_database
    )
    cursor = cnx.cursor()

    try:
        for symbol in symbols:
            # Get the start time for the symbol
            start_time = time.time()

            # Retrieve the historical data for the symbol
            data = yf.download(symbol, start='2020-01-01', end='2023-06-01')

            # Check if the required columns exist in the DataFrame
            if all(col in data.columns for col in ['Open', 'High', 'Low', 'Close', 'Adj Close']):
                # Reset the index of the DataFrame
                data.reset_index(inplace=True)

                # Extract the required columns (date, open, high, low, close, adj_close)
                filtered_data = data[['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close']].copy()

                # Format the date column
                filtered_data['Date'] = filtered_data['Date'].dt.strftime('%Y-%m-%d %H:%M:%S')

                # Rename the columns
                filtered_data.rename(columns={'Date': 'date', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Adj Close': 'adj_close'}, inplace=True)

                # Prepare the SQL query to insert the new data
                insert_query = "INSERT INTO stock_data1 (symbol, date, open, high, low, close, adj_close) VALUES (%s, %s, %s, %s, %s, %s, %s)"

                # Define the batch size for insertion
                batch_size = 100

                # Batch insert the data into the table
                for i in range(0, len(filtered_data), batch_size):
                    batch_data = filtered_data.iloc[i:i+batch_size]
                    values = [(symbol, row['date'], row['open'], row['high'], row['low'], row['close'], row['adj_close']) for _, row in batch_data.iterrows()]
                    cursor.executemany(insert_query, values)

                # Commit the changes to the database
                cnx.commit()

                # Get the end time for the symbol
                end_time = time.time()

                # Calculate the time taken to fetch data for the symbol
                time_taken = end_time - start_time

                print(f"Data fetched and inserted for symbol: {symbol} (Time taken: {time_taken:.2f} seconds)")
            else:
                print(f"Error: Required columns not found in data for symbol: {symbol}")

    except Exception as e:
        print(f"Error: An exception occurred for symbols: {symbols}")
        print(str(e))

    # Close the cursor and connection
    cursor.close()
    cnx.close()

if __name__ == '__main__':
    # Load the CSV file containing stock symbols
    df_symbols = pd.read_csv('Company_list1.csv')

    # Append ".NS" to each symbol
    df_symbols['symbol'] = df_symbols['symbol'] + '.NS'

    # Define the chunk size for multiprocessing
    chunk_size = 100

    # Split the symbols into chunks
    symbol_chunks = [symbols.tolist() for symbols in np.array_split(df_symbols['symbol'].dropna(), chunk_size)]

    # Create a multiprocessing pool
    num_processes = 6
    pool = multiprocessing.Pool(num_processes)

    # Map symbol chunks to the fetch_and_insert_data function
    pool.map(fetch_and_insert_data, symbol_chunks)

    # Close the pool
    pool.close()
    pool.join()
