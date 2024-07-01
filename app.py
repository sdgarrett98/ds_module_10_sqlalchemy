# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import datetime as dt # suggested by claude
import numpy as np



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

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
@app.route("/")
def home():
    """List all available routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end<br/>;"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the last year"""
    # calculate date 1 year ago
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    # Query for the last 12 months of precipitation data
    precipitation = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_year).all()
    
    session.close()
    precipitation_dict = {date: prcp for date, prcp in precipitation}
    
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""
    results = session.query(Station.station).all()
    
    session.close()
    stations_list = list(np.ravel(results))
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def temp_monthly():
    """Return the temperature observations (tobs) for previous year."""
    # Query the primary station for all tobs from the last year
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= '2016-08-23').all()
    
    # Unravel results into a 1D array and convert to a list
    session.close()
    temps = list(np.ravel(results))
    return jsonify(temps)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""
    
    # Select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    
    if not end:
        # Calculate TMIN, TAVG, TMAX for dates greater than or equal to start
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
    else:
        # Calculate TMIN, TAVG, TMAX for dates between start and end inclusive
        results = session.query(*sel).\
            filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()
    
    # Unravel results into a 1D array and convert to a list
    session.close()
    temps = list(np.ravel(results))
    return jsonify({"TMIN": temps[0], "TAVG": temps[1], "TMAX": temps[2]})

if __name__ == '__main__':
    app.run(debug=True)