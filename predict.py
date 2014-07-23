# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

# Hourly Demand Prediction Challenge
# (Predict future hourly demand based on past data)
# 
# 1) Average data based on weekday
#        - holidays will be outliers (Easter, ...?)
#        - discuss outliers (sports games, etc), even though uou might not account for each
#
#
#
# [cross validate]
#
#
# useful functions:
#     calendar.weekday(year, month, day)      retruns day of week [0-6]
#     datetime.datetime.now()                 now, date + time
#     datetime.datetime.now().time()          now, only time
#     time.gmtime()                           convert time since epoch -> UTC
#     time.localime()                         convert time since epoch -> local time
#     time.timegm()                           convert UTC -> time since epoch
#     time.strftime(format[, t])              convert a formatted string toe a 

# TASKS:
#     GET a prediction, given a time
#     PUT more another time stamp (or a number of timestamps?)
#     GET timestamps form MIN to MAX (maybe?)
    


    
# A list of datetime obects that specify atypical days (holidays, etc) that 
# should not be averaged into normal weekdays for demand prediction.
# (to be updated manually):
special_dates = []

# note that we're considering each hour to correspond to be a random variable

import datetime
from collections import namedtuple
import numpy

# def predict_demand(time = datetime.datetime.)

import dataprep


def weekday_hour_grouping(hours, usage):
    """
    [doctest]
    """
    # for the dataset, aggregate data on the same hour of the same weekday:
    weekhour_agg = [[[] for _ in range(24)] for _ in range (7)]

#     print len(weekhour_agg)
#     print len(weekhour_agg[0])
#     print len(weekhour_agg[0][0])

    # NOTE: if the hours array is ordered, you could do this without reaching into each datetime object
    for h, u in zip(hours, usage):
        wd = h.weekday()
        hr = h.timetuple().tm_hour
        weekhour_agg[wd][hr].append(u)
        

    return weekhour_agg



def average_hours(weekhour_agg):
    """
    Note, we're calculating the unbiased sample variance here.
    [doctest]
    """
    
    
    Stats = namedtuple('Stats', ['mean','var'])
    hourly_usage_stats = [[Stats(mean=None, var=None) for _ in range(24)] for _ in range (7)]
    for wd in range(7):
        for hr in range(24):
            hourly_usage_stats[wd][hr] = Stats(mean = numpy.mean(weekhour_agg[wd][hr]), \
                                               var  = numpy.var(weekhour_agg[wd][hr], ddof=1))

    return hourly_usage_stats


if __name__ == '__main__':

    # load the JSON file (throw sensible error if it doesn't exist):
    hours, usage = dataprep.prepare("hourly_demand_prediction_challenge.json")
    
    # perform the hourly grouping & averaging:
    hourly_usage_stats = average_hours(weekday_hour_grouping(hours, usage))


    
    

# <codecell>


