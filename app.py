# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, distinct

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return (
        f"Hawaii Weather Data:<br/><br>"
        f"Last Years Hawaiian Precipatation Totals (Daitly) <a href=\"/api/v1.0/precipitation\">/api/v1.0/precipitation<a><br/>"
        f"Active Weather Stations <a href=\"/api/v1.0/stations\">/api/v1.0/stations<a><br/>"
        f"Station USC00519281 Daily Temperature Observations <a href=\"/api/v1.0/tobs\">/api/v1.0/tobs<a><br/>"
        f"Minimum, Maximum, and Average Temperatures /api/v1.0/hawaii/yyyy-mm-dd/yyyy-mm-dd<br>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    
    prior_date = '2016-08-23'
    sel = [measurement.date, 
        func.sum(measurement.prcp)]
    precipitation = session.query(*sel).\
            filter(measurement.date >= prior_date).\
            group_by(measurement.date).\
            order_by(measurement.date).all()
   
    session.close()

    precipitation_dates = []
    precipitation_totals = []

    for date, dailytotal in precipitation:
        precipitation_dates.append(date)
        precipitation_totals.append(dailytotal)
    
    precipitation_dict = dict(zip(precipitation_dates, precipitation_totals))

    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    sel = [measurement.station]
    active_stations = session.query(*sel).\
        group_by(measurement.station).all()
    session.close()

    stations_list = list(np.ravel(active_stations)) 
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    prior_date = '2016-08-23'
    sel = [measurement.date, 
        measurement.tobs]
    temps_station = session.query(*sel).\
            filter(measurement.date >= prior_date, measurement.station == 'USC00519281').\
            group_by(measurement.date).\
            order_by(measurement.date).all()

    session.close()

    observation_dates = []
    temperature_observations = []

    for date, observation in station_temps:
        observation_dates.append(date)
        temperature_observations.append(observation)
    
    most_active_tobs_dict = dict(zip(observation_dates, temperature_observations))

    return jsonify(most_active_tobs_dict)

@app.route("/api/v1.0/hawaii/<start_date>")
def hawaii1(prior_date, end_date='2017-08-23'):
    session = Session(engine)
    query_result = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()
    session.close()

    trip_stats = []
    for min, avg, max in query_result:
        Hawaii_dict = {}
        Hawaii_dict["Min"] = min
        Hawaii_dict["Average"] = avg
        Hawaii_dict["Max"] = max
        Hawaii_stats.append(Hawaii_dict)

    if Hawaii_dict['Min']: 
        return jsonify(trip_stats)
    else:
        return jsonify({"error": f"Date {start_date} is not formatted as YYYY-MM-DD or found."}), 404
  
@app.route("/api/v1.0/hawaii/<start_date>/<end_date>")
def hawaii2(prior_date, end_date='2017-08-23'):
    session = Session(engine)
    query_result = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= prior_date).filter(measurement.date <= end_date).all()
    session.close()

    Hawaii_stats = []
    for min, avg, max in query_result:
        Hawaii_dict = {}
        Hawaii_dict["Min"] = min
        Hawaii_dict["Average"] = avg
        Hawaii_dict["Max"] = max
        Hawaii_stats.append(Hawaii_dict)


    if Hawaii_dict['Min']: 
        return jsonify(trip_stats)
    else:
        return jsonify({"error": f"Looks like the date you selected is either typed incorrectly or is an invalid date range or dates."}), 404
  

if __name__ == '__main__':
    app.run(debug=True)