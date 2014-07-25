# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

# A list of datetime obects that specify atypical days (holidays, etc) that 
# should not be averaged into normal weekdays for demand prediction.
# (to be updated manually):
special_dates = []

# note that we're considering each hour to correspond to be a random variable

import datetime
from collections import namedtuple
import numpy

import dataprep


Stats = namedtuple('Stats', ['mean','var'])


def exp_downweight_avg(dates_counts, s = 0.97):

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
    # eventially take time to consider the unbiased one.
    counts = zip(*dates_counts)[1]
    running_var = 0
    for weight, count in zip(weight_list, counts):
        running_var += (count-m)**2.0*weight
    v = running_var/norm_const
        
    return Stats(mean = m, var = v)



def weekday_hour_grouping(hours, usage, filter_holidays = False):
    """
    [doctest]
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
    [doctest]
    """

    if method == 'average-plain':
        usagecounts = zip(*weekhour)[1]
        return Stats(mean = numpy.mean(usagecounts), \
                     var  = numpy.var(usagecounts, ddof=1))

    if method == 'exp-downweight':
        return exp_downweight_avg(weekhour)
        
        

def average_all_hours(weekhour_agg, method='average-plain'):
    """
    Note, we're calculating the unbiased sample variance here.
    [doctest]
    """
    
    hourly_usage_stats = [[Stats(mean=None, var=None) for _ in range(24)] for _ in range (7)]
    for wd in range(7):
        for hr in range(24):
            hourly_usage_stats[wd][hr] = average_hour(weekhour_agg[wd][hr], method)

    return hourly_usage_stats


if __name__ == '__main__':

    # load the JSON file (throw sensible error if it doesn't exist):
    # (each member of the hours, usage lists corresponds to a unique hour on a unique date.)
    hours, usage = dataprep.prepare("hourly_demand_prediction_challenge.json")
    
    # perform the hourly grouping & averaging:
    # (add here a method to group MTWR data together, if needed)
    weekhour_agg = weekday_hour_grouping(hours, usage)
    method='average-plain'
    hourly_usage_stats = average_all_hours(weekhour_agg, method)


    
    

# <codecell>


