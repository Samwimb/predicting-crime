#################################################
# Import Dependencies
#################################################

import os

import numpy as np

from datetime import date

import requests

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

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
    print(np.transpose(samples).shape)
    # print(samples)
    return samples

# Returns text labels for test sample predictions
def predict(models, samples):
    prediction_list = []
    for m in models:
        region = {'label': m['label'],
                  'predictions': [],
                  'days': []
                 }
        for s in samples:
            region['days'].append(getWeekday(s[5]))                                                # <-- check index for day of week
            print(region)
            print(s)
            print(s.shape)
            with graph.as_default():
                x = labels.inverse_transform(m['model'].predict_classes(s))
            region['predictions'].append(x)
        prediction_list.append(region)
    print(prediction_list)
    return prediction_list


#################################################
# Configure Database
#################################################

# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db/bellybutton.sqlite"
# db = SQLAlchemy(app)

# reflect an existing database into a new model
# Base = automap_base()
# reflect the tables
# Base.prepare(db.engine, reflect=True)

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
    return jsonify(predict(Models, Samples))


#################################################
# Launch Scheduler & App
#################################################

if __name__ == "__main__":
    scheduler.start()
    app.run()
