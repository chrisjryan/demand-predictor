# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

#!/usr/bin/env python

import datetime
from collections import namedtuple
import numpy
import os
import sys

import dataprep

Stats = namedtuple('Stats', ['mean','var'])


def exp_downweight_avg(dates_counts, s = 0.97):
    """
    Average the timestamp counts for a particular hour of a particular 
    weekday. Older data are downweighted exponentially, so newer data can 
    have more influence on the average. At the moment the parameter for this 
    scheme is simply read in as an optional argument.
    """

    # dividing by the sum of the weights will normalize our statistics.
    # (note: in the limit of lots of data this will = 1-s. But we can't 
    # guarantee that yet.)
    date_most_recent = max(zip(*dates_counts)[0])
    weight_list = []
    norm_const = 0
    running_mean = 0    
    for date, count in dates_counts:
        weight = s**((date_most_recent - date).days/7)
        running_mean += count*weight
        norm_const += weight
        weight_list.append(weight)
    m = running_mean/norm_const

    # TODO: this is a biased weighted sample variance, for now, which is close.
    # eventually take time to consider the unbiased one.
    counts = zip(*dates_counts)[1]
    running_var = 0
    for weight, count in zip(weight_list, counts):
        running_var += (count-m)**2.0*weight
    v = running_var/norm_const
        
    return Stats(mean = m, var = v)


def weekday_hour_grouping(hours, usage, filter_holidays = False):
    """
    This function groups the 1d arrays of binned timestamps count data with 
    other data on the same weekday and hour, but on different dates.
    The output, 'weekhour_agg', is a 2d list with each element correpsonding 
    to an hour of a week day (hence the 2 dimensions). Each of these elements 
    contains a list of 2-tuples, where 2-tuple contains this hour window for 
    some specific date and the number of timestamps binned in this window on 
    this date. Maintaining the data at this point helps keep the age of the 
    data before averaging, so this can be weighted properly using, e.g., the 
    exponential downweighting method.
    """
    
    # filter out "special days"
#     if (filter_holidays):
#         hours, usage = filter_special_days(hours, usage)
    
    # for the dataset, aggregate data on the same hour of the same weekday:
    weekhour_agg = [[[] for _ in range(24)] for _ in range (7)]

    # NOTE: if the hours array is ordered, you could do this without reaching into each datetime object
    for h, u in zip(hours, usage):
        wd = h.weekday()
        hr = h.timetuple().tm_hour
        weekhour_agg[wd][hr].append((h,u))

    return weekhour_agg


def average_hour(weekhour, method='average-plain'):
    """
    Average the timestamp counts for a particular hour of a particular 
    weekday. At the moment, counts may be averaged normally or older data 
    can be exponentially downweighted in favor of newer data. (See docstring 
    for exp_downweight_avg().)
    """

    if method == 'average-plain':
        usagecounts = zip(*weekhour)[1]
        return Stats(mean = numpy.mean(usagecounts), \
                     var  = numpy.var(usagecounts, ddof=1))

    elif method == 'exp-downweight':
        return exp_downweight_avg(weekhour)
    
    else:
        sys.exit('Invalid averaging method specified.')
        
        
def average_all_hours(weekhour_agg, method='average-plain'):
    """
    Compute the average and variance, using the method specified as an 
    argument (passed on to average_hour()), for each hour on each weekday.
    """
    
    hourly_usage_stats = [[Stats(mean=None, var=None) for _ in range(24)] for _ in range (7)]
    for wd in range(7):
        for hr in range(24):
            hourly_usage_stats[wd][hr] = average_hour(weekhour_agg[wd][hr], method)

    return hourly_usage_stats


if __name__ == '__main__':
    """
    Load the JSON file containing timestamp data and compute average usage 
    statistics for each hour in a week.
    """
    # A list of datetime obects that specify atypical days (holidays, etc) 
    # (to be updated manually):
#     special_dates = []

    # load the JSON file (throw sensible error if it doesn't exist):
    # (each member of the hours, usage lists corresponds to a unique hour on a unique date.)
    datafile = "hourly_demand_prediction_challenge.json"
    if os.path.isfile(datafile):
        hours, usage = dataprep.prepare(datafile)

        # perform the hourly grouping & averaging:
        # (add here a method to group MTWR data together, if needed)
        weekhour_agg = weekday_hour_grouping(hours, usage)
        method='average-plain'
        hourly_usage_stats = average_all_hours(weekhour_agg, method)
    else:
        print 'Error: No data file found.'


# <codecell>


