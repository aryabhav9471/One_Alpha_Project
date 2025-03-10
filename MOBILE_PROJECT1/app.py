import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import MySQLdb
import datetime
import yfinance as yf

app = Flask(__name__)
CORS(app)

# Fetch environment variables for security
MYSQL_HOST = os.getenv('MYSQL_HOST', 'sql12.freesqldatabase.com')
MYSQL_USER = os.getenv('MYSQL_USER', 'sql12766961')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'VKqi5BgQpv')
MYSQL_DB = os.getenv('MYSQL_DB', 'sql12766961')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))

def get_db_connection():
    """Establish and return a database connection."""
    try:
        return MySQLdb.connect(
            host=MYSQL_HOST, user=MYSQL_USER, passwd=MYSQL_PASSWORD, db=MYSQL_DB, port=MYSQL_PORT
        )
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def fetch_symbols(table_name):
    """Fetch distinct stock symbols from a given table."""
    db = get_db_connection()
    if not db:
        return jsonify({"error": "Database connection failed"})
    
    try:
        cursor = db.cursor()
        cursor.execute(f"SELECT DISTINCT symbol FROM {table_name}")
        results = cursor.fetchall()
        db.close()
        return [row[0] for row in results]
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/stocks', methods=['GET'])
def get_stocks():
    symbols = fetch_symbols("stock_data1")
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(symbols)
    return render_template('stocks.html', symbols=symbols)

@app.route('/stocks2', methods=['GET'])
def get_stocks2():
    symbols = fetch_symbols("stock_data")
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(symbols)
    return render_template('stocks2.html', symbols=symbols)

@app.route('/stock_data/<symbol>/<time_range>', methods=['GET'])
def get_stock_data(symbol, time_range):
    db = get_db_connection()
    if not db:
        return jsonify({"error": "Database connection failed"})
    
    try:
        cursor = db.cursor()
        today = datetime.date.today()
        time_deltas = {'1D': 0, '1W': 7, '1M': 30, '1Y': 365}
        start_date = today - datetime.timedelta(days=time_deltas.get(time_range, 0)) if time_range in time_deltas else None
        query = "SELECT symbol, adj_close, open, low, close, high, date FROM stock_data1 WHERE symbol = %s"
        params = (symbol,) if not start_date else (symbol, start_date)
        cursor.execute(query + (" AND date >= %s" if start_date else ""), params)
        results = cursor.fetchall()
        db.close()
        return jsonify([{ 'symbol': row[0], 'adj_close': row[1], 'open': row[2], 'low': row[3], 'close': row[4], 'high': row[5], 'date': row[6] } for row in results])
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/stocks40/<symbol>', methods=['GET'])
def get_stock_info(symbol):
    try:
        stock = yf.Ticker(symbol)
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
        return jsonify(stock_info)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
