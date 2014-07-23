#! /usr/bin/env python


import requests
import dataprep
import os





# load the JSON file containing login data:
datafile = 'hourly_demand_prediction_challenge.json'

if os.path.isfile(datafile):
    logindata = dataprep.load_json(datafile)
else:
    logindata = []


# post the data to the server via the Flask API:
# for ld in logindata[:5]:
# 	r = requests.post('http://localhost:5000/api/post', data=ld)

# it seems like the data kwarg in requests can handle strings and dictionaries, but not lists of strings. Maybe that's because this cannot be unambiguously formatted in a URL.
r = requests.post('http://localhost:5000/api/post', data=logindata)

