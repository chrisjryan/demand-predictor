#! /usr/bin/env python

import requests
import dataprep
import os
import argparse
import sys


# parse the terminal input:
desc = """A script for inserting timestamp data as JSON array into the demand 
predictor API."""
parser = argparse.ArgumentParser(description=desc, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('datafile', help='Name of a JSON file containing an array/list of strings containing correctly formtatted timestamps.')
args = parser.parse_args()

# load the JSON file containing login data as an array (not a JSON object):
if os.path.isfile(args.datafile):
    logindata = dataprep.load_json(args.datafile)
else:
    sys.exit('File not found.')

# post the timestamp to the API data as a comma-separated string:
r = requests.post('http://localhost:5000/api/post', data=','.join(logindata))

# print the response:
print r.text