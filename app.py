#################################################
# Import Dependencies
#################################################

import os

import numpy as np

from datetime import date

import requests

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Float, func

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

class Config(object):
    SCHEDULER_API_ENABLED = True

app = Flask(__name__)
app.config.from_object(Config())

scheduler = APScheduler()
scheduler.init_app(app)

# Retrieve API Keys from environment
M_KEY = os.environ.get('m_key', "")
W_KEY = os.environ.get('w_key', "aa2739ba803749f08d1691ee4f04d27a")       # <--- ADD KEYS TO HEROKU CONFIG

# Intialize empty list for weather forecast
forecast = []

bins = [ {
    'verylow': 62,
    'low': 83,
    'medium': 104,
    'high': 125,
    'veryhigh': 163
},
{
    'verylow': 5,
    'low': 10,
    'medium': 15,
    'high': 20,
    'veryhigh': 36
},
{
    'verylow': 7,
    'low': 13,
    'medium': 19,
    'high': 25,
    'veryhigh': 45
},
{
    'verylow': 7,
    'low': 13,
    'medium': 19,
    'high': 25,
    'veryhigh': 42
},
{
    'verylow': 4,
    'low': 9,
    'medium': 14,
    'high': 19,
    'veryhigh': 33
},
{
    'verylow': 4,
    'low': 9,
    'medium': 14,
    'high': 19,
    'veryhigh': 31
},
{
    'verylow': 4,
    'low': 9,
    'medium': 14,
    'high': 19,
    'veryhigh': 29
},
{
    'verylow': 3,
    'low': 7,
    'medium': 11,
    'high': 15,
    'veryhigh': 25
}]

# def insertRow(x):
#     date = forecast[1]['text']
#     for i, d in enumerate(districts):
        # check to to see ifn row for date exists
        # if it does, overwrite it (update)
        # if it doesnt', insert data

# def updateRow():
    # call api
    # count records for last day that doesn't have entry for actual_count
    # compare to prediction and assign value

    


# Get Day of the Week for today - Sunday=1
def getToday():
    d = date.today().isoweekday() + 1
    if d == 8:
        d = 1
    return d

# Day of the Week calculation for forecast
def getWeekday(num):
    return num - (((num-1)//7) * 7)

# Query WeatherBit API and return list of weather forecasts
# Scheduled to run automatically every day at 3am
@scheduler.task('cron', id='getWeather', hour='3')
def getWeather():
    weatherURL = f"https://api.weatherbit.io/v2.0/forecast/daily?city=Washington,DC&units=I&key={W_KEY}"
    data = requests.get(weatherURL).json()

    day = getToday()

    forecast.clear()
    forecast.append(date.today().strftime("%A, %d %B, %Y"))   # <--- USED FOR DEBUGGING
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

# Returns text labels for test sample predictions
def predict(models, samples):
    prediction_list = []
    for m in models:
        region = {'label': m['label'],
                  'predictions': np.array([]),
                  'days': []
                 }
        for s in samples:
            region['days'].append(getWeekday(s[5]))                                                # <-- check index for day of week
            with graph.as_default():
                region['predictions'] = np.append(region['predictions'],
                    labels.inverse_transform(m['model'].predict_classes(np.reshape(s, (-1, 10)))))
            region['predictions'] = region['predictions'].tolist()
        prediction_list.append(region)
    return prediction_list


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

districts=[allDistricts, District1, District2, District3,
 District4, District5, District6, District7]

# Save references to each table
# Samples_Metadata = Base.classes.sample_metadata
# Samples = Base.classes.samples


#################################################
# Load ML Model & Initialize Test Data
#################################################

global graph
graph = tf.get_default_graph()

# Load models for each region
with CustomObjectScope({'GlorotUniform': glorot_uniform()}):
    with open('./static/models/model_architecture_alldistricts.json', 'r') as f:
        DCmodel = model_from_json(f.read())
    DCmodel.load_weights('./static/models/alldistricts_weights.h5')

    with open('./static/models/model_architecture_district1.json', 'r') as f:
        D1model = model_from_json(f.read())
    D1model.load_weights('./static/models/district1_weights.h5')

    with open('./static/models/model_architecture_district2.json', 'r') as f:
        D2model = model_from_json(f.read())
    D2model.load_weights('./static/models/district2_weights.h5')

    with open('./static/models/model_architecture_district3.json', 'r') as f:
        D3model = model_from_json(f.read())
    D3model.load_weights('./static/models/district3_weights.h5')

    with open('./static/models/model_architecture_district4.json', 'r') as f:
        D4model = model_from_json(f.read())
    D4model.load_weights('./static/models/district4_weights.h5')

    with open('./static/models/model_architecture_district5.json', 'r') as f:
        D5model = model_from_json(f.read())
    D5model.load_weights('./static/models/district5_weights.h5')

    with open('./static/models/model_architecture_district6.json', 'r') as f:
        D6model = model_from_json(f.read())
    D6model.load_weights('./static/models/district6_weights.h5')

    with open('./static/models/model_architecture_district7.json', 'r') as f:
        D7model = model_from_json(f.read())
    D7model.load_weights('./static/models/district7_weights.h5')

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
labels = LabelEncoder()
labels.fit(['VeryLow', 'Low', 'Medium', 'High', 'VeryHigh'])

# Initialize weather forecast
getWeather()

# Generate test samples for today + n-days (1 + 5)
Samples = generateSamples(6)


#################################################
# Configure Routes
#################################################

@app.route("/")
def index():
    """Return the homepage"""
    return render_template("justins_playground.html")
    # return render_template("index.html")        # <--- ENSURE THIS POINTS TO THE CORRECT HOMEPAGE

@app.route("/get_weather")
def getForecast():
    """Diagnostic Route"""
    return jsonify(forecast)

@app.route("/crime_forecast")
def crimeForecast():
    """Return array with today's crime prediction and 5-day forecast"""
    # return jsonify(list(labels.inverse_transform([0, 2, 2, 1, 4, 0])))      # <--- FOR TESTING ONLY
    x = predict(Models, Samples)
    insertRow(x)
    return jsonify(x)


#################################################
# Launch Scheduler & App
#################################################

if __name__ == "__main__":
    scheduler.start()
    app.run()
