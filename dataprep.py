# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

# Hourly Demand Prediction Challenge
# (Exploratory data analysis)
# 
# metadata: 
#     - JSON file consisting of login times, only
#     - UTC timestamps from March 1 to May 1
#     - Washington DC
#
# Note: when binning by hour, note that there are some hours where no 
#       login was made.
# 
# 
# 

# <codecell>

# Bin the data to visualize hourly demand.

import itertools
import datetime
import calendar
import time
import json


def load_json(filename):
    """
    [add docstring]
    """
    with open(filename) as infile:
        data = json.load(infile)
    return data


def bin_timestamp(timestamp_strings, fmt, binsize = 3600):
    """
    Returns a list of lists, with each sub-list containing a datetime 
    object corresponding to an hour and a integer count of timestamps 
    within that hour. as a ___ object. Assumes timestamp string is UTC 
    (Greenwich mean time) formatted as '%Y-%m-%dT%H:%M:%S+00:00'. 
    This returned list will not, in general, contain a 'bin' for each
    hour between the min and max timestamp in the dataset (i.e., hour 
    windows that have 0 timestamps will _not_ be contained in the list 
    with a timestamp count == 0).
    [doctest]
    """

    # convert timestamp string -> datetime objects:
    dt = [datetime.datetime.strptime(t, fmt) for t in timestamp_strings]

    # bin each timestamp into the specified time windows:
    binned_times = [[datetime.datetime(*time.gmtime(d*binsize)[:6]), len(list(g))] \
                    for d,g in itertools.groupby(dt, \
                        lambda di: int(calendar.timegm(di.timetuple()))/binsize)]

    # return an list of lists, unzipped from binned_times:
    return [list(t) for t in zip(*binned_times)]


def prepare(jsonfile):
    """
    [docstring]
    """
    # Load a list of user login times (UTC timestamp):
    logins = load_json(jsonfile)

    # timestamp string format & time constants:
    fmt = '%Y-%m-%dT%H:%M:%S+00:00'
    seconds_per_hour = 60*60 # number of seconds in an hour
    hours_per_week = 24*7

    # bin the timestamp strings into hour-spanning windows:
    hours, usage = bin_timestamp(logins, fmt, seconds_per_hour)

    # fill in any hours without logins to be zero:
    starthour = hours[0]
    total_hours = (calendar.timegm(max(hours).timetuple()) - calendar.timegm(min(hours).timetuple()))/60/60
    allhours = [starthour + datetime.timedelta(hours = x) for x in range(total_hours)]
    for dt in allhours:
        if dt not in hours:# and dt < last_timestamp:
            hours.append(dt)
            usage.append(0)

    # sort the list by hour & unzip:
    hours, usage = zip(*sorted(zip(hours, usage), key = lambda hu:hu[0]))

    return hours, usage

# <codecell>

