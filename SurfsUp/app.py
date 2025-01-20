# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt

from sqlalchemy import desc
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from datetime import datetime, timedelta

from flask import Flask, jsonify
import json

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Start at the homepage.
# List all the available routes.
@app.route("/")
def home():
    return(
        f"<h2>Available Routes:</h2>"
        f"<h3>/api/v1.0/precipitation</h3>"
        f"<h3>/api/v1.0/stations</h3>"
        f"<h3>/api/v1.0/tobs</h3>"
        f"<h3>/api/v1.0/<start_d></h3>"
    )

# Retrieve only the last 12 months of precipitation data 
@app.route("/api/v1.0/precipitation")
def fun_precipitation():
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_date_obj = dt.datetime.strptime(last_date, "%Y-%m-%d")
    year_ago = last_date_obj - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).all()
    precip_data = []
    for date, precip in results:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["prcp"] = precip
        precip_data.append(precip_dict)

    return jsonify(precip_data)

# Retrieve a list of stations
@app.route("/api/v1.0/stations")
def fun_stations():
    results = session.query(Station.station).all()
    stations = []
    for station in results:
        station_dict = {}
        station_dict["station name"] = station[0]
        stations.append(station_dict)
    return jsonify(stations)

#  Query the dates and temperature observations of the most-active station for the previous year of data.
@app.route("/api/v1.0/tobs")
def fun_tobs():
    active_station = session.query(Measurement.station, func.count(Measurement.station))\
                                .group_by(Measurement.station)\
                                .order_by(desc(func.count(Measurement.station)))\
                                .first()
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_date_obj = dt.datetime.strptime(last_date, "%Y-%m-%d")
    year_ago = last_date_obj - dt.timedelta(days=365)
    print("Active Stations: ", active_station[0])
    results = session.query(Measurement.date, Measurement.tobs).filter((Measurement.station == active_station[0]) & (Measurement.date > year_ago)).all()
    tobs_data = []
    for date, tobs in results:
        tobs_data.append(tobs)

    return jsonify(tobs_data)

# For a specified start date, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
@app.route("/api/v1.0/<start_d>")
def fun_calculate_temp(start_d):
    start_date = dt.datetime.strptime(start_d,"%Y-%m-%d")
    query_results = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.round(func.avg(Measurement.tobs))).\
    filter(Measurement.date >= start_date).all()
    temp_dict = {}
    temp_dict["Average"] = query_results[0][0]
    temp_dict["Minimum"] = query_results[0][1]
    temp_dict["Maximum"] = query_results[0][2]
    return jsonify(temp_dict)

# For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
@app.route("/api/v1.0/<start_date>/<end_date>")
def temps_start_end(start_date=None, end_date=None):
    session = Session(engine)

    query_results = session.query(func.avg(Measurement.tobs), func.min(Measurement.tobs), func.max(Measurement.tobs)).\
        filter((Measurement.date >= start_date)&(Measurement.date <= end_date)).\
        all()
    temp_dict = {}
    temp_dict["Average"] = query_results[0][0]
    temp_dict["Minimum"] = query_results[0][1]
    temp_dict["Maximum"] = query_results[0][2]
    return jsonify(temp_dict)
    
    
if __name__ == "__main__":
    app.run(debug=True)