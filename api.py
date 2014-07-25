#!/usr/bin/enc python

from flask import Flask, jsonify, request, make_response
import os
import numpy
import datetime
import pytz

import dataprep
import predict


app = Flask(__name__)


def find(lst, a):
    """
    A quick function for returning a list of indices of a list that match some element.
    Can return more than 1 index in principle, but that shouldn't happen in this API.
    >>> find([1,2,3,4], 3)
    [2]
    >>> find(['A','B','C','D'], 'D')
    [3]
    >>> find(['A','B','C','D'], 'E')
    
    >>> find(None, 'E')
    
    >>> find([1,2,3,3,3,4], 3)
    [2, 3, 4]
    """
    if lst:
        match_idx = [i for i, x in enumerate(lst) if x==a]
        if match_idx:
            return match_idx
    else:
        return


@app.route('/api/predict-daterange-utc', methods = ['GET'])
def predict_demand_daterange_utc():
    """
    Predict the demand for each hour within the specified date range. Note: 
    assumes that all users are using UTC time in their request. The two dates 
    must be specified as '%Y-%m-%d'.
    """
    if logindata:
        assert hourly_usage_stats # should always exist if logindata does.
        date_min, date_max = (request.data).split(',')
        fmt_day = '%Y-%m-%d'

        # get a list of datetime objects for the range specified:
        utc = pytz.utc
        dt_min, dt_max = (utc.localize(datetime.datetime.strptime(dt,fmt_day)) for dt in (date_min,date_max))

        if dt_min > dt_max:
            # return make_response('Error: min date greater than max date.'), 204
            return make_response('Error: min date greater than max date.')

        if not dt_min > max(hours) or not dt_max > max(hours):
            return make_response('Error: choose a date range in the future.')

        date_list = [dt_min+datetime.timedelta(days=x) for x in range((dt_max-dt_min).days+1)]

        # output a list of predicted login counts:
        fmt_out = '%Y-%m-%dT%H:%M:%S'
        weekday_list = [dt.weekday() for dt in date_list]
        predictions = [((d+datetime.timedelta(hours=hr)).strftime(fmt_out), \
                         hourly_usage_stats[wd][hr].mean) \
                        for d, wd in zip(date_list, weekday_list) \
                        for hr in range(24)]

        # convert to a CSV delimited string, as directed:
        outstr = ''
        for datehour, logins in predictions:
            outstr += datehour + ' ,%.2f,\n' % logins

        return outstr, 200

    else:
        return 'No login data has been inserted yet.', 204


@app.route('/api/predict', methods = ['GET'])
def predict_demand():
    """
    Predict the demand given some specified weekday & hour. Assumes that 
    users are using UTC Time in their request. The predicted time is the 
    computed using past data as specified by predict.average_all_hours(). This 
    is currently hardcoded as the expoential downweighted average of past usage 
    counts for this hour on this weekday.
    This function is unit tested by helper.predictor().
    """
    if logindata:
        assert hourly_usage_stats # should always exist if logindata does.
        weekday_int, hour = (request.data).split(',')
        st = hourly_usage_stats[int(weekday_int)][int(hour)]

        return jsonify( { 'logins (predicted)': st.mean, '+/- error' : numpy.sqrt(st.var) } ), 200

    else:
        return 'No login data has been inserted yet.', 204


@app.route('/api/alldata', methods = ['GET'])
def get_alldata():
    """
    Returns all the raw timetamp data as a JSON file.
    """
    return jsonify( { 'logins': logindata } )


@app.route('/api/post', methods = ['POST'])
def post_data():
    """
    This POST method allows API users to add timestamp data to the web app. 
    These data are expected to be comma delimited and formatted as 
    '%Y-%m-%dT%H:%M:%S+00:00'. Misformatted data are handled by 
    predict.bin_timestamp().
    Both raw timestamp data and binned hourlong usage counts are updated and 
    maintained. Averages are recalculated from scratch at the end of this method, 
    however eventually these will be updated without computing everything anew. 
    This function is unit tested by helper.add_datafile().
    """
    # Note: updating global variables endangers threadsafety, improve this 
    # later (see below).
    global logindata, hours, usage, hourly_usage_stats 

    # split the concatenated timestamp string into a list of strings:
    new_timestamps = (request.data).split(',')

    # bin correctly-formatted timestamps into correpsonding hour-long time windows:
    (hours_new, usage_new), skipped_timestamps = dataprep.bin_timestamp(new_timestamps, fmt, seconds_per_hour)

    # filter out misformatted timestamp strings & incorporate correct raw data:
    new_timestamps = [ts for i, ts in enumerate(new_timestamps) if i not in skipped_timestamps]
    logindata.extend(new_timestamps)

    # append to the global hours, usage counts:
    for h,u in zip(hours_new, usage_new):
        match_idx = find(hours, h)
        if match_idx:
            usage[match_idx[0]] += u
        else:
            hours.append(h)
            usage.append(u)

    # update any stats accordingly:
    # hours_et = dataprep.convert_timezone_eastern(hours)
    weekhour_agg = predict.weekday_hour_grouping(hours, usage)
    hourly_usage_stats = predict.average_all_hours(weekhour_agg, 'exp-downweight')

    # return results:
    result = '%i of %i timestamp(s) inserted. \n(%i timestamp(s) skipped due to misformatting.)' \
            % (len(new_timestamps)-len(skipped_timestamps), len(new_timestamps), len(skipped_timestamps)) 

    return result


if __name__ == '__main__':
    """
    This will check that the bundle data file exists, load the file of timestamp
    strings (skipping any misfomatted strings), bin these timestamps into hourlong
    windows specified by datetime objects, & average all data that falls within 
    the same hour of the same weekday.
    """

    # timestamp string format & time constants:
    fmt = '%Y-%m-%dT%H:%M:%S+00:00'
    seconds_per_hour = 60*60 # number of seconds in an hour

    # load pre-existing data:
    datafile = 'hourly_demand_prediction_challenge.json'
    # datafile = ''

    # TODO: logindata, hours, usage, and hourly_usage_stats are currently globals 
    # that are updated by HTTP requests. Store them in a cache or database to 
    # ensure thread safety.
    if os.path.isfile(datafile):
        logindata = dataprep.load_json(datafile)

        # bin the timestamps into hourlong windows:
        hours, usage = dataprep.prepare(datafile)

        weekhour_agg = predict.weekday_hour_grouping(hours, usage)
        hourly_usage_stats = predict.average_all_hours(weekhour_agg, 'exp-downweight')

    else:
        print 'Warning: No pre-existing data file found. Initializing empty data set.'
        logindata = []
        hours = []
        usage = []
        hourly_usage_stats = []

    # run the API:
    app.run(debug = True)