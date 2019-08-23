#################################################
# Import Dependencies
#################################################

import os

import numpy as np

from datetime import date as Date, timedelta

import requests

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, desc, func
from sqlalchemy import Column, Integer, String, Float

from flask import Flask, jsonify, render_template
from flask_apscheduler import APScheduler
from flask_sqlalchemy import SQLAlchemy

import tensorflow as tf
import keras
from keras.utils import CustomObjectScope
from keras.initializers import glorot_uniform
from keras.models import load_model, Sequential, model_from_json
from keras.layers import Dense, Dropout
from sklearn.preprocessing import LabelEncoder


#################################################
# Configure Variables & Helper Functions
#################################################

# Initialize Flask app and Scheduler for API calls
class Config(object):
    SCHEDULER_API_ENABLED = True

app = Flask(__name__)
app.config.from_object(Config())

scheduler = APScheduler()
scheduler.init_app(app)


# Retrieve API Keys from environment
M_KEY = os.environ.get('m_key', "")
W_KEY = os.environ.get('w_key', "aa2739ba803749f08d1691ee4f04d27a")       # <--- ADD KEYS TO HEROKU CONFIG


# Intialize empty lists for weather forecast and crime prediction
forecast = []
prediction_list = []
Samples = None


# List of bin bounds for each district
# [VeryLow, Low, Medium, High, VeryHigh]
bins = [[62, 83, 104, 125, 163],    # All of DC
        [5, 10, 15, 20, 36],        # District 1
        [7, 13, 19, 25, 45],        # District 2
        [7, 13, 19, 25, 42],        # District 3
        [4, 9, 14, 19, 33],         # District 4
        [4, 9, 14, 19, 31],         # District 5
        [4, 9, 14, 19, 29],         # District 6
        [3, 7, 11, 15, 25]]         # District 7


# Get Day of the Week for today - Sunday=1
def getToday():
    d = Date.today().isoweekday() + 1
    if d == 8:
        d = 1
    return d


# Day of the Week calculation for forecast
def getWeekday(num):
    return num - (((num-1)//7) * 7)


#################################################
# Configure Database
#################################################

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data/database.sqlite"
db = SQLAlchemy(app)

# reflect an existing database into a new model
Base = declarative_base()

class allDistricts(Base):
    __tablename__ = 'alldistricts'
    Date = Column(String(30), primary_key=True)
    Prediction = Column(String(30))
    Actual = Column(String(30))
    Correct = Column(String(30))
    
class District1(Base):
    __tablename__ = 'district1'
    Date = Column(String(30), primary_key=True)
    Prediction = Column(String(30))
    Actual = Column(String(30))
    Correct = Column(String(30))

class District2(Base):
    __tablename__ = 'district2'
    Date = Column(String(30), primary_key=True)
    Prediction = Column(String(30))
    Actual = Column(String(30))
    Correct = Column(String(30))

class District3(Base):
    __tablename__ = 'district3'
    Date = Column(String(30), primary_key=True)
    Prediction = Column(String(30))
    Actual = Column(String(30))
    Correct = Column(String(30))

class District4(Base):
    __tablename__ = 'district4'
    Date = Column(String(30), primary_key=True)
    Prediction = Column(String(30))
    Actual = Column(String(30))
    Correct = Column(String(30))

class District5(Base):
    __tablename__ = 'district5'
    Date = Column(String(30), primary_key=True)
    Prediction = Column(String(30))
    Actual = Column(String(30))
    Correct = Column(String(30))

class District6(Base):
    __tablename__ = 'district6'
    Date = Column(String(30), primary_key=True)
    Prediction = Column(String(30))
    Actual = Column(String(30))
    Correct = Column(String(30))

class District7(Base):
    __tablename__ = 'district7'
    Date = Column(String(30), primary_key=True)
    Prediction = Column(String(30))
    Actual = Column(String(30))
    Correct = Column(String(30))

# Store all tables in list for easy iterating
districts = [
    allDistricts,
    District1,
    District2,
    District3,
    District4,
    District5,
    District6,
    District7
]


#################################################
# Load Models & Initialize Samples
#################################################

# Initialize graph to avoid threading issues
global graph
graph = tf.get_default_graph()

# absolute path to this file
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
# absolute path to this file's root directory
PATH = os.path.join(FILE_DIR, os.pardir)

# Load models for each region
with CustomObjectScope({'GlorotUniform': glorot_uniform()}):
    with open(os.path.join(PATH, '/static/models/model_architecture_alldistricts.json'), 'r') as f:
        DCmodel = model_from_json(f.read())
    DCmodel.load_weights(os.path.join(PATH, '/static/models/alldistricts_weights.h5'))

    with open(os.path.join(PATH, '/static/models/model_architecture_district1.json'), 'r') as f:
        D1model = model_from_json(f.read())
    D1model.load_weights(os.path.join(PATH, '/static/models/district1_weights.h5'))

    with open(os.path.join(PATH, '/static/models/model_architecture_district2.json'), 'r') as f:
        D2model = model_from_json(f.read())
    D2model.load_weights(os.path.join(PATH, '/static/models/district2_weights.h5'))

    with open(os.path.join(PATH, '/static/models/model_architecture_district3.json'), 'r') as f:
        D3model = model_from_json(f.read())
    D3model.load_weights(os.path.join(PATH, '/static/models/district3_weights.h5'))

    with open(os.path.join(PATH, '/static/models/model_architecture_district4.json'), 'r') as f:
        D4model = model_from_json(f.read())
    D4model.load_weights(os.path.join(PATH, '/static/models/district4_weights.h5'))

    with open(os.path.join(PATH, '/static/models/model_architecture_district5.json'), 'r') as f:
        D5model = model_from_json(f.read())
    D5model.load_weights(os.path.join(PATH, '/static/models/district5_weights.h5'))

    with open(os.path.join(PATH, '/static/models/model_architecture_district6.json'), 'r') as f:
        D6model = model_from_json(f.read())
    D6model.load_weights(os.path.join(PATH, '/static/models/district6_weights.h5'))

    with open(os.path.join(PATH, '/static/models/model_architecture_district7.json'), 'r') as f:
        D7model = model_from_json(f.read())
    D7model.load_weights(os.path.join(PATH, '/static/models/district7_weights.h5'))

# Store models with label
Models = [
    {'label': 0, 'model': DCmodel},
    {'label': 1, 'model': D1model},
    {'label': 2, 'model': D2model},
    {'label': 3, 'model': D3model},
    {'label': 4, 'model': D4model},
    {'label': 5, 'model': D5model},
    {'label': 6, 'model': D6model},
    {'label': 7, 'model': D7model}
]

# Initialize reverse encoding
bin_labels = ['VeryLow', 'Low', 'Medium', 'High', 'VeryHigh']
labels = LabelEncoder()
labels.fit(bin_labels)


#################################################
# Core Code & Functionality
#################################################

# Query WeatherBit API and return list of weather forecasts
# Scheduled to run automatically every day at 3am
@scheduler.task('cron', id='getWeather', hour='4')
def getWeather():
    weatherURL = f"https://api.weatherbit.io/v2.0/forecast/daily?city=Washington,DC&units=I&key={W_KEY}"
    data = requests.get(weatherURL).json()

    day = getToday()

    forecast.clear()
    forecast.append(Date.today().strftime("%A, %d %B, %Y"))
    for i, d in enumerate(data['data']):
        entry = {
                    'text': d['valid_date'],
                    'year': int(d['valid_date'].split('-')[0]),
                    'month': int(d['valid_date'].split('-')[1]),
                    'date': int(d['valid_date'].split('-')[2]),
                    'day': getWeekday(day + i),
                    'max_temp': d['max_temp'],
                    'min_temp': d['min_temp'],
                    'precip': d['precip'],
                    'lunar': round(d['moon_phase'], 4),
                    'wind': d['wind_spd'],
                    'snow': d['snow'],
                    'snow_depth': d['snow_depth']
                }
        forecast.append(entry)
    
    # Create Samples from weather forecast
    Samples = generateSamples(6)


# Creates Numpy Array of data from weather forecast for crime prediction
def generateSamples(n=16):
    if n > 16:
        n = 16
    d = forecast[1]
    samples = np.array([[d['wind'], d['snow'], d['snow_depth'], d['max_temp'], d['min_temp'],
                       d['day'], d['date'], d['month'], d['year'], d['lunar']]])
    for i in range(2, n+1):
        d = forecast[i]
        s = np.array([[d['wind'], d['snow'], d['snow_depth'], d['max_temp'], d['min_temp'],
                       d['day'], d['date'], d['month'], d['year'], d['lunar']]])
        samples = np.append(samples, s, axis=0)
    return samples


# Initialize weather forecast
getWeather()

# Generate test samples for today + n-days (1 + 5)
Samples = generateSamples(6)


# Returns text labels for test sample predictions
@scheduler.task('cron', id='makePrediction', hour='4', minute='15')
def predict():
    prediction_list.clear()
    for m in Models:
        region = {'label': m['label'],
                  'predictions': np.array([]),
                  'days': []
                 }
        for s in Samples:
            region['days'].append(getWeekday(s[5]))                                                # <-- check index for day of week
            with graph.as_default():
                region['predictions'] = np.append(region['predictions'],
                    labels.inverse_transform(m['model'].predict_classes(np.reshape(s, (-1, 10)))))
            region['predictions'] = region['predictions'].tolist()
        prediction_list.append(region)


@scheduler.task('cron', id='insertDB', hour='4', minute='30')
def insertRow():
    date = forecast[1]['text']

    # iterate through district tables and add entry with today's prediction
    for i, d in enumerate(districts):
        sel = [
            d.Date,
            d.Prediction,
            d.Actual,
            d.Correct
        ]

        result = db.session.query(*sel).filter_by(Date = date).first()

        # If there is already an entry for today, make sure it is up-to-date
        # Otherwise, add an entry
        if not result:
            db.session.add(d(Date = date, Prediction = prediction_list[i]['predictions'][0]))
            db.session.commit()


@scheduler.task('cron', id='updateDB', hour='4', minute='45')
def updateRow():
    # Get 'YYYY-MM-DD' for yesterday's date
    date = forecast[1]['text']
    t = timedelta(days=1)
    d = date.split('-')
    date = Date(int(d[0]), int(d[1]), int(d[2]))
    date -= t

    # Get Crime data for yesterday from DC OpenData
    crimeURL = f"https://maps2.dcgis.dc.gov/dcgis/rest/services/FEEDS/MPD/MapServer/1/query?where=START_DATE>DATE'{date} 00:00:01'&outFields=CCN,START_DATE,DISTRICT&outSR=4326&f=json"
    response = requests.get(crimeURL).json()['features']

    # Create list with count of crimes in DC and each district
    crimeCount = [0] * 8
    for r in response:
        crimeCount[0] += 1
        crimeCount[int(r['attributes']['DISTRICT'])] += 1
    
    # Labels the crimeCount for each district for easy database comparison
    cBin = [''] * 8
    for i, c in enumerate(crimeCount):
        cBin[i] = bin_labels[0]
        for j, b in enumerate(bins[i]):
            if c >= b:
                try:
                    cBin[i] = bin_labels[j+1]
                except:
                    cBin[i] = bin_labels[j]

    # Iterate through district tables, updating actual crime
    # and whether or not our prediction was accurate
    for i, d in enumerate(districts):
        sel = [
            d.Date,
            d.Prediction,
            d.Actual,
            d.Correct
        ]
        
        # If there is an entry for yesterday, update it, otherwise do nothing
        result = db.session.query(*sel).filter_by(Date = date).first()
        if result:
            p = result.Prediction
            a = crimeCount[i]
            if p == cBin[i]:
                c = 'Yes'
            else:
                c = 'No'
            db.session.query(*sel).filter_by(Date = date).delete()
            db.session.add(d(Date = date, Prediction = p, Actual = a, Correct = c))
            db.session.commit()


# Make predictions for n-Samples
predict()

# Insert prediction for today into DB
insertRow()

# Update yesterday's prediction with actual crime count
updateRow()

#################################################
# Configure Routes
#################################################

@app.route("/")
def index():
    """Return the homepage"""
    return render_template("index.html")

@app.route("/get_weather")
def getForecast():
    """Diagnostic Route"""
    return jsonify(forecast)

@app.route("/crime_forecast")
def crimeForecast():
    """Return array with today's crime prediction and 5-day forecast"""
    return jsonify(prediction_list)

@app.route("/get_tables")
def getTableNames():
    """Return a list of all of our tbale names to build the selector"""
    names = []
    for t in districts:
        names.append(t.__tablename__)
    
    return jsonify(names)

@app.route("/<table>")
def getTable(table):
    """Return data for selected table"""
    for d in districts:
        if d.__tablename__ == table.lower():
            table = d
            break

    sel = [
        table.Date,
        table.Prediction,
        table.Actual,
        table.Correct
    ]

    results = db.session.query(*sel).order_by(desc(table.Date)).all()

    tableData = []

    for r in results:
        tableData.append([r[0], r[1], r[2], r[3]])

    return jsonify(tableData)


#################################################
# Launch Scheduler & App
#################################################

if __name__ == "__main__":
    scheduler.start()
    app.run()
