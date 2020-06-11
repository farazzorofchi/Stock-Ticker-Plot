from flask import Flask, render_template, request, redirect, flash
import pandas as pd
from math import pi
from bokeh.plotting import figure, output_file, save, show
from tempfile import mkdtemp
from flask_session import Session
import requests
import json
import os


app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route('/')
def index():
	return render_template("Home.html")
	
@app.route('/Home', methods=["GET", "POST"])
def Home():
	if request.method == "POST":
		start_date = request.form.get("startdate")	
		end_date = request.form.get("enddate")		
		if (not int(start_date[:4]+start_date[5:7]+start_date[8:10])) or (start_date[4] != '-') or (start_date[7] != '-') or (len(start_date) != 10) or (int(start_date[5:7]) > 12) or (int(start_date[8:10]) > 31):
			message = "start date should be in the format of YYYY--MM--DD"
			return render_template("apology.html", top=400, bottom=message), 400
			
		elif (not int(end_date[:4]+end_date[5:7]+end_date[8:10])) or (end_date[4] != '-') or (end_date[7] != '-') or (len(end_date) != 10) or (int(end_date[5:7]) > 12) or (int(end_date[8:10]) > 31):
			message = "end date should be in the format of YYYY--MM--DD"
			return render_template("apology.html", top=400, bottom=message), 400
			
		elif int(start_date[:4]+start_date[5:7]+start_date[8:10]) >= int(end_date[:4]+end_date[5:7]+end_date[8:10]):
			message = "end date should be later than start date"
			return render_template("apology.html", top=400, bottom=message), 400
		
		ticker = request.form.get("ticker")
		link = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=' + ticker + '&outputsize=full&apikey=QWWKZD8Y3KV3MRIC'
		r = requests.get(link)
		data = r.json()
		try:
			panel_data = pd.DataFrame.from_dict(data['Time Series (Daily)'], orient='index')
		except:
			message = "There is no information for this ticker"
			return render_template("apology.html", top=400, bottom=message), 400
		
		panel_data = panel_data[end_date:start_date]
		panel_data.sort_index(inplace=True)
		panel_data = panel_data.reset_index()
		panel_data.columns = ['date', 'open', 'high','low','close','adj close', 'volume', 'div amount', 'split coef']
		panel_data["date"] = pd.to_datetime(panel_data["date"])
		plot = figure()
		inc = panel_data['close'] > panel_data['open'] 
		dec = panel_data['close'] < panel_data['open'] 
		w = 12*60*60*1000 # half day in ms
		TOOLS = "pan,wheel_zoom,box_zoom,reset,save"
		p = figure(x_axis_type="datetime", tools=TOOLS, plot_width=1000, title = ticker+" Candlestick Plot")
		p.xaxis.major_label_orientation = pi/4
		p.grid.grid_line_alpha=0.3
		p.segment(panel_data['date'], panel_data['high'], panel_data['date'], panel_data['low'], color="black")
		p.vbar(panel_data['date'][inc], w, panel_data['open'][inc], panel_data['close'][inc], fill_color="#00FF00", line_color="black")
		p.vbar(panel_data['date'][dec], w, panel_data['open'][dec], panel_data['close'][dec], fill_color="#FF0000", line_color="black")
		output_file("templates/candlestick.html", title="candlestick.py example")
		save(p)
		return render_template("candlestick.html")
	else:
		return render_template("Home.html")

@app.route('/About', methods=["GET", "POST"])		
def About():
	return render_template("about.html")

if __name__ == '__main__':
	port = int(os.environ.get("PORT", 33507))
	#app.run(host='0.0.0.0', port = port)
	app.run(port=port)
