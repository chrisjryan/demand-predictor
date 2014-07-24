#!/usr/bin/enc python

from flask import Flask, jsonify, request
import os
import numpy

import dataprep
import predict


app = Flask(__name__)


@app.route('/api/predict', methods = ['GET'])
def predict_demand():
    """
    Predict the demand given some specified weekday & hour.
    """

    weekday_int, hour = (request.data).split(',')
    st = hourly_usage_stats[int(weekday_int)][int(hour)]

    return jsonify( { 'logins (predicted)': st.mean, '+/- error' : numpy.sqrt(st.var) } )



@app.route('/api/alldata', methods = ['GET'])
def get_alldata():
    """
    Return all the raw timetamp data as a JSON file.
    """
    return jsonify( { 'logins': logindata } )



@app.route('/api/post', methods = ['POST'])
def post_data():
    """
    [docstring]
    """

    # split the concatenated timestamp string into a list of strings:
    new_timestamps = (request.data).split(',')

    # bin correctly-formatted timestamps into correpsonding hour-long time windows:
    (hours, usage), skipped_timestamps = dataprep.bin_timestamp(new_timestamps, fmt, seconds_per_hour)

    # filter out misformatted timestamp strings & incorporate correct raw data:
    new_timestamps = [ts for i, ts in enumerate(new_timestamps) if i not in skipped_timestamps]
    logindata.extend(new_timestamps)

    # append to the global hours, usage counts:


    # update any stats accordingly:


    # return results:
    result = '%i of %i timstamp(s) inserted. \n(%i timestamp(s) skipped due to misformatting.)' \
            % (len(new_timestamps)-len(skipped_timestamps), len(new_timestamps), len(skipped_timestamps)) 

    return result


if __name__ == '__main__':

    # timestamp string format & time constants:
    fmt = '%Y-%m-%dT%H:%M:%S+00:00'
    seconds_per_hour = 60*60 # number of seconds in an hour

    # load pre-existing data:
    datafile = 'hourly_demand_prediction_challenge.json'
    # datafile = ''
    if os.path.isfile(datafile):
        logindata = dataprep.load_json(datafile)
    else:
        logindata = []

    # compute statistics:
    if logindata:
        hours, usage = dataprep.prepare(datafile)

        # necessary? maybe just do this on request:
        hours = dataprep.convert_timezone_eastern(hours)

        weekhour_agg = predict.weekday_hour_grouping(hours, usage)
        hourly_usage_stats = predict.average_all_hours(weekhour_agg, 'exp-downweight')


    # run the API:
    app.run(debug = True)



