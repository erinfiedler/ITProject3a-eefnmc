import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, abort
import csv
import matplotlib.pyplot as plt
import numpy as np
import requests
from datetime import datetime
from io import BytesIO
import pandas as pd
import base64
import requests
import pygal


app = Flask(__name__)
app.config["DEBUG"] = True  # allows us to update app w/out restarting
app.config['SECRET_KEY'] = 'your secret key'
api_key = "O3VHGQEVCW40YRTI"

# Load stock symbols from the CSV file
stocks_df = pd.read_csv('stocks.csv')
stock_symbols = sorted(stocks_df['Symbol'].tolist())

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get form data
        selected_stock = request.form.get('stock_symbol')
        time_series = request.form.get('time_series')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        chart_type = request.form.get('chart_type')

        #gets AlphaVintage API data from stock_data
        stock_data = get_stock_data(selected_stock, time_series, start_date, end_date)
        
        # Create a plot based on the user's choice of chart type
        if stock_data:
            # Create a plot based on the user's choice of chart type
            plot = create_plot(stock_data, chart_type)

    # Render the template with stock symbols for the dropdown
    return render_template('index.html', stock_symbols=stock_symbols)

def get_stock_data(symbol, time_series, start_date, end_date):
    api_key = "O3VHGQEVCW40YRTI"
    url = f"https://www.alphavantage.co/query?function=LISTING_STATUS&apikey={api_key}"

    params = {
        'function': 'TIME_SERIES_' + time_series.upper(),
        'symbol': symbol,
        'apikey': api_key,
    }

    # Check if start_date is provided and less than end_date
    if start_date and end_date and start_date >= end_date:
        flash("Error: Start date must be before end date.")
        return None

    if start_date:
        params['start_date'] = start_date
    if end_date:
        params['end_date'] = end_date

    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()

                # Check if the response contains an error message
        if 'Error Message' in data:
            print(f"Error: {data['Error Message']}")
            return None

        # Extract the relevant stock data from the response
        if 'Time Series' in data:
            stock_data = data['Time Series']
            return stock_data
        else:
            return None
    else:
        # Print an error message if the request was not successful
        print(f"Error: {response.status_code}")
        return None



def create_plot(stock_data, chart_type):
    #get dates and prices from stock_data
    dates = list(stock_data.keys())
    closing_prices = [float(stock_data[date]['4. close']) for date in dates]

    # Convert dates to datetime objects
    dates = [datetime.strptime(date, '%Y-%m-%d') for date in dates]

    #PLOT DATA
    fig = Figure()
    ax = fig.subplots()
    plt.style.use('seaborn')
    #fig, ax = plt.subplots()
    ax.plot(dates, closing_prices, label='Closing Prices', color='blue')

    #FORMAT PLOT
    ax.set_title('Stock Data Graph', fontsize=24)
    ax.set_xlabel('Date', fontsize=16)
    fig.autofmt_xdate()
    ax.set_ylabel('Price USD', fontsize=16)
    ax.legend()
    
    buf = BytesIO()
    #fig.savefig(buf, format="png")
    # Embed the result in the html output.
    FigureCanvas(fig).print_png(buf)
    return Response(buf.getvalue(), mimetype = 'image/png')
    #image_path = 'static/plot.png'
    #plt.savefig(image_path, format='png')
    

    # Encode the plot in base64
    #return image_path.render_in_browser()


app.run(host="0.0.0.0")


