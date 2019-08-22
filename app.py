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

import tensorflow
from keras.models import load_model, Sequential
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
        entry = {'date': {
                    'text': d['valid_date'],
                    'year': int(d['valid_date'].split('-')[0]),
                    'month': int(d['valid_date'].split('-')[1]),
                    'date': int(d['valid_date'].split('-')[2]),
                    'day': getWeekday(day + i)
                },
                'weather': {
                    'max_temp': d['max_temp'],
                    'min_temp': d['min_temp'],
                    'precip': d['precip'],
                    'lunar': round(d['moon_phase'], 4)
                }
            }
        forecast.append(entry)

# Creates Numpy Array of data from weather forecast for crime prediction
def generateSamples(n=16):
    if n > 16:
        n = 16
    samples = np.array([[]])
    for i in range(n):
        d = forecast[i]
        s = np.array([[d['date']['month'], d['date']['date'], d['date']['day'],
                       d['weather']['max_temp'], d['weather']['min_temp'],
                       d['weather']['precip'], d['weather']['lunar']]])
        samples = np.append(samples, s, axis=0)
    return samples

# Returns text labels for test sample predictions
def predict(model, test):
    return list(labels.inverse_transform(model.predict_classes(test)))


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

# dc_crime_model = load_model("voice_model_trained.h5")       # <--- CHANGE FILE PATH

labels = LabelEncoder()
labels.fit(['VeryLow', 'Low', 'Medium', 'High', 'VeryHigh'])

getWeather()
# testSamples = generateSamples(5)


#################################################
# Configure Routes
#################################################

@app.route("/")
def index():
    """Return the homepage"""
    return render_template("justins_playground.html")
    # return render_template("index.html")        # <--- ENSURE THIS POINTS TO THE CORRECT HOMEPAGE

@app.route("/get_forecast")
def getForecast():
    """Diagnostic Route"""
    return jsonify(forecast)

@app.route("/forecast")
def crimeForecast():
    """Return array with today's crime prediction and 5-day forecast"""
    return jsonify(list(labels.inverse_transform([0, 2, 2, 1, 4, 0])))      # <--- FOR TESTING ONLY
    # return jsonify(predict(dc_crime_model, generateSamples(6)))


#################################################
# Launch Scheduler & App
#################################################

if __name__ == "__main__":
    scheduler.start()
    app.run()
