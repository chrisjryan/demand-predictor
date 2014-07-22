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



import datetime

# def predict_demand(time = datetime.datetime.)

import dataprep


# def average_hours():


if __name__ == '__main__':

    # load the JSON file (throw sensible error if it doesn't exist):
    hours, usage = dataprep.prepare("hourly_demand_prediction_challenge.json")

    
    # perform the hourly grouping (share this method in a neat way with the eda.ipynb file)
    
    


# <codecell>


