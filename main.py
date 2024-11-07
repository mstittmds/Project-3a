from flask import Flask, render_template, request, redirect, url_for, flash
import pygal
from data_fetcher import fetch_stock_data
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/', methods=['GET', 'POST'])
def index():
    stock_symbols = ["Select a Symbol", "AAPL", "MSFT", "GOOGL"]
    chart_types = ["Select a Chart","Bar", "Line"]
    time_series_types = ["Select a Time Series","Intraday", "Daily", "Weekly", "Monthly"]

    if request.method == 'POST':
        stock_symbol = request.form.get('stock_symbol')
        chart_type = request.form.get('chart_type')
        time_series_type = request.form.get('time_series_type')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        
        if time_series_type == "Daily":
            time_series_type = "TIME_SERIES_DAILY"
        if time_series_type == "Weekly":
            time_series_type = "TIME_SERIES_WEEKLY"
        if time_series_type == "Monthly":
            time_series_type = "TIME_SERIES_MONTHLY"

        if not (stock_symbol and chart_type and time_series_type and start_date and end_date):
            flash("All fields are required!", "error")
            return render_template('index.html', stock_symbols=stock_symbols,
                                   chart_types=chart_types, time_series_types=time_series_types)

        if start_date >= end_date:
            flash("Start date must be before end date.", "error")
            return render_template('index.html', stock_symbols=stock_symbols,
                                   chart_types=chart_types, time_series_types=time_series_types)

        try:
            stock_data = fetch_stock_data(stock_symbol, time_series_type, start_date, end_date)
            print("Stock Data: ",stock_data)
            if stock_data is None or stock_data.empty:
                flash("No data available for the selected parameters.", "error")
                return render_template('index.html', stock_symbols=stock_symbols,
                                       chart_types=chart_types, time_series_types=time_series_types)
        except Exception as e:
            flash(f"An error occurred while fetching stock data: {e}", "error")
            return render_template('index.html', stock_symbols=stock_symbols,
                                   chart_types=chart_types, time_series_types=time_series_types)

        try:
            chart = pygal.Bar() if chart_type == 'Bar' else pygal.Line()
            chart.title = f'{stock_symbol} Stock Prices'
            chart.x_labels = stock_data.index.strftime('%Y-%m-%d')
            chart.add('Prices', stock_data['4. close'])

            chart_file = "static/chart.svg"
            chart.render_to_file(chart_file)

            return render_template('index.html', stock_symbols=stock_symbols,
                                   chart_types=chart_types, time_series_types=time_series_types,
                                   chart_file=chart_file)
        except Exception as e:
            flash(f"An error occurred while generating the chart: {e}", "error")

    return render_template('index.html', stock_symbols=stock_symbols,
                           chart_types=chart_types, time_series_types=time_series_types)
app.run(port=5000)