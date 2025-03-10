from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import MySQLdb
import datetime
import yfinance as yf
app = Flask(__name__)
CORS(app)

@app.route('/stocks', methods=['GET'])
def get_stocks():
    # Connect to the MySQL database
    db = MySQLdb.connect(host='localhost', user='root', password='Aryabhav@2004', db='stock')
    cursor = db.cursor()

    # Execute the query to retrieve distinct symbols
    cursor.execute("SELECT DISTINCT symbol FROM stock_data1")

    # Fetch all the results
    results = cursor.fetchall()

    # Close the database connection
    db.close()

    # Convert the results to a list of symbols
    symbols = [row[0] for row in results]

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # If it's an AJAX request, return the JSON response
        return jsonify(symbols)
    else:
        # If it's a regular request, render the HTML template
        return render_template('stocks.html', symbols=symbols)
    
@app.route('/stocks1', methods=['GET'])
def get_stocks1():
    # Connect to the MySQL database
    db = MySQLdb.connect(host='localhost', user='root', password='Aryabhav@2004', db='stock')
    cursor = db.cursor()

    # Execute the query to retrieve distinct symbols
    cursor.execute("SELECT DISTINCT symbol FROM stock_data")

    # Fetch all the results
    results = cursor.fetchall()

    # Close the database connection
    db.close()

    # Convert the results to a list of symbols
    symbols = [row[0] for row in results]

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # If it's an AJAX request, return the JSON response
        return jsonify(symbols)
    else:
        # If it's a regular request, render the HTML template
        return render_template('stocks1.html', symbols=symbols)

@app.route('/stocks2', methods=['GET'])
def get_stocks2():
    # Connect to the MySQL database
    db = MySQLdb.connect(host='localhost', user='root', password='Aryabhav@2004', db='stock')
    cursor = db.cursor()

    # Execute the query to retrieve distinct symbols
    cursor.execute("SELECT DISTINCT symbol FROM stock_data")

    # Fetch all the results
    results = cursor.fetchall()

    # Close the database connection
    db.close()

    # Convert the results to a list of symbols
    symbols = [row[0] for row in results]

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # If it's an AJAX request, return the JSON response
        return jsonify(symbols)
    else:
        # If it's a regular request, render the HTML template
        return render_template('stocks2.html', symbols=symbols)

@app.route('/stocks3', methods=['GET'])
def get_stocks3():
    # Connect to the MySQL database
    db = MySQLdb.connect(host='localhost', user='root', password='Aryabhav@2004', db='stock')
    cursor = db.cursor()

    # Execute the query to retrieve distinct symbols
    cursor.execute("SELECT DISTINCT symbol FROM stock_data1")

    # Fetch all the results
    results = cursor.fetchall()

    # Close the database connection
    db.close()

    # Convert the results to a list of symbols
    symbols = [row[0] for row in results]

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # If it's an AJAX request, return the JSON response
        return jsonify(symbols)
    else:
        # If it's a regular request, render the HTML template
        return render_template('stocks3.html', symbols=symbols)
    

@app.route('/stocks4', methods=['GET'])
def get_stocks4():
    # Connect to the MySQL database
    db = MySQLdb.connect(host='localhost', user='root', password='Aryabhav@2004', db='stock')
    cursor = db.cursor()

    # Execute the query to retrieve distinct symbols
    cursor.execute("SELECT DISTINCT symbol FROM stock_data1")

    # Fetch all the results
    results = cursor.fetchall()

    # Close the database connection
    db.close()

    # Convert the results to a list of symbols
    symbols = [row[0] for row in results]

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # If it's an AJAX request, return the JSON response
        return jsonify(symbols)
    else:
        # If it's a regular request, render the HTML template
        return render_template('stocks4.html', symbols=symbols)


@app.route('/stock_data/<symbol>/<time_range>', methods=['GET'])
def get_stock_data(symbol, time_range):
    # Connect to the MySQL database
    db = MySQLdb.connect(host='localhost', user='root', passwd='Aryabhav@2004', db='stock')
    cursor = db.cursor()

    # Determine the start and end dates based on the time range
    today = datetime.date.today()
    if time_range == '1D':
        start_date = today 
    elif time_range == '1W':
        start_date = today - datetime.timedelta(weeks=1)
    elif time_range == '1M':
        start_date = today - datetime.timedelta(days=30)
    elif time_range == '1Y':
        start_date = today - datetime.timedelta(days=365)
    else:
        # Default to retrieving the whole data
        start_date = None

    # Construct the SQL query based on the time range
    if start_date:
        query = "SELECT symbol, adj_close, open, low, close, high, date FROM stock_data1 WHERE symbol = %s AND date >= %s"
        cursor.execute(query, (symbol, start_date))
    else:
        query = "SELECT symbol, adj_close, open, low, close, high, date FROM stock_data1 WHERE symbol = %s"
        cursor.execute(query, (symbol,))

    # Fetch all the results
    results = cursor.fetchall()

    # Close the database connection
    db.close()

    # Create a list of dictionaries containing symbol, adj_close, open, low, close, high, and date
    data = []
    for row in results:
        symbol = row[0]
        adj_close = row[1]
        open_val = row[2]
        low = row[3]
        close = row[4]
        high = row[5]
        date = row[6]
        data.append({
            'symbol': symbol,
            'adj_close': adj_close,
            'open': open_val,
            'low': low,
            'close': close,
            'high': high,
            'date': date
        })

    # Return the data as JSON
    return jsonify(data)

@app.route('/stocks40/<symbol>', methods=['GET'])
def get_stock_info(symbol):
    # Retrieve stock information based on the selected symbol
    stock_info = fetch_stock_info(symbol)
    if stock_info:
        return jsonify(stock_info)
    else:
        return jsonify({'error': 'Stock information not found.'}), 404

def fetch_stock_info(symbol):
    # Fetch stock information using yfinance library
    stock = yf.Ticker(symbol)
    
    # Extract the required information from the stock object
    stock_info = {
        'Company Name': stock.info.get('longName', ''),
        'Exchange': stock.info.get('exchange', ''),
        'Sector': stock.info.get('sector', ''),
        'Industry': stock.info.get('industry', ''),
        'Market Cap': stock.info.get('marketCap', ''),
        'Shares Outstanding': stock.info.get('sharesOutstanding', ''),
        'Dividend Yield': stock.info.get('dividendYield', ''),
        'Forward P/E Ratio': stock.info.get('forwardPE', ''),
        'EPS (Earnings Per Share)': stock.info.get('trailingEps', ''),
        'Beta': stock.info.get('beta', ''),
        '52-Week High': stock.info.get('fiftyTwoWeekHigh', ''),
        '52-Week Low': stock.info.get('fiftyTwoWeekLow', ''),
        'Website': stock.info.get('website', '')
    }
    
    return stock_info

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
