#!/user/bin/env python

import argparse
import requests
import sys
import os
import datetime

import dataprep


def add_datafile(datafile):
	"""
	Add data to the we app from a JSON file containing an array of timestamps. 
	datafile is a string correpsonding to the name of this file. 
	Assumes that the API is running on http://localhost:5000
	>>> add_datafile('hourly_demand_prediction_challenge.json')
	u'22447 of 22447 timstamp(s) inserted. \\n(0 timestamp(s) skipped due to misformatting.)'
	>>> add_datafile('foo_bar.json')
	Traceback (most recent call last):
	...
	SystemExit: File not found.
	"""
	# load the JSON file containing login data as an array (not a JSON object):
	if os.path.isfile(datafile):
	    logindata = dataprep.load_json(datafile)
	else:
	    sys.exit('File not found.')

	# post the timestamp to the API data as a comma-separated string:
	r = requests.post('http://localhost:5000/api/post', data=','.join(logindata))

	# print the text response:
	return r.text


def predictor(weekday, hour):
	"""
	Uses the hourly-demand API to return a predicted usage at some 
	weekday and hour. Weekdays should be specified by a 3 letter 
	string, and hours should be specified as an int between 0 an 23.
	Assumes that the API is running on http://localhost:5000.
	>>> r = predictor('mon', 13)
	>>> r.status_code
	200
	>>> r = predictor('tue', 36)
	Traceback (most recent call last):
	...
	SystemExit: Error: please specify an hour between 0 and 23.
	>>> r = predictor('xro', 13)
	Traceback (most recent call last):
	...
	SystemExit: Error: please choose a weekday by specifying the first 3 letters of one.
	"""
	daylist = ['sun','mon','tue','wed','thu','fri','sat']

	if weekday.lower() not in daylist:
		sys.exit('Error: please choose a weekday by specifying the first 3 letters of one.')

	if hour <= 0 or hour >= 23:
		sys.exit('Error: please specify an hour between 0 and 23.')

	day_idx = {d:idx for idx,d in enumerate(daylist)}
	d = str(day_idx[weekday.lower()]) + ',' +str(hour)
	r = requests.get('http://localhost:5000/api/predict', data=d)

	return r


def predictor_daterange(datestr1, datestr2):
	"""
	This function returns the predicted hourly usage for each hour in the date 
	range specified. These predictions are returned as a comma-separated string 
	with linebreaks suitable for file output. Date strings must be formatted as 
	'%Y-%m-%d'. Assumes that the API is running on http://localhost:5000
	>>> r = predictor_daterange('2012-05-01','2012-05-15')
	>>> r.status_code
	200
	>>> r = predictor_daterange('2012-5-1','2012-5-15')
	>>> r.status_code
	200
	>>> r = predictor_daterange('2011-05-01','2011-05-15')
	>>> r.content
	'Error: choose a date range in the future.'
	>>> r = predictor_daterange('2012-05-15','2012-05-01')
	>>> r.content
	'Error: min date greater than max date.'
	"""

	# check to make sure each string is formatted correctly:
	fmt = '%Y-%m-%d'
	for ds in [datestr1, datestr2]:
		try:
			datetime.datetime.strptime(ds, fmt)
		except:
			sys.exit('Please format strings as YEAR-MONTH-DAY (e.g., 2012-05-01)')

	d = datestr1 + ',' + datestr2
	r = requests.get('http://localhost:5000/api/predict-daterange-utc', data=d)

	return r


def main(args):
	"""
	Executes the helper functions accoring to the user's specifications.
	>>> from argparse import Namespace
	>>> main(Namespace(filename=None, hour=None, mode='insert', weekday=None))
	Traceback (most recent call last):
	...
	SystemExit: Error: for 'insert' mode, please specify a filename.
	>>> main(Namespace(filename=None, hour=None, mode='predict', weekday=None))
	Traceback (most recent call last):
	...
	SystemExit: Error: for 'predict' mode, please specify a weekday and hour.
	>>> main(Namespace(filename=None, hour=None, mode=None, weekday=None))
	Traceback (most recent call last):
	...
	SystemExit: Error: please specify either 'insert' or 'predict' (or use -h for usage instructions).
	"""

	if args.mode == 'predict':
		if args.weekday and args.hour:
			r = predictor(args.weekday, int(args.hour))	
			try:
				for k,v in r.json().iteritems():
					print '%-25s %f' % (k,v)
			except:
				print r.content
		else:
			sys.exit("Error: for 'predict' mode, please specify a weekday and hour.")
	elif args.mode == 'insert':
		if args.filename:
			rtext = add_datafile(args.filename)
			print rtext
		else:
			sys.exit("Error: for 'insert' mode, please specify a filename.")
	else:
		sys.exit("Error: please specify either 'insert' or 'predict' (or use -h for usage instructions).")


if __name__ == '__main__':

	# parse the terminal input:
	desc = "A helper script for using the demand predictor API."
	parser = argparse.ArgumentParser(description=desc, formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument('-mode', help="Whether you want to 'insert' data from a JSON file or 'predict' the demand given some specifed weekday and hour.", choices=['insert','predict'])
	parser.add_argument('-weekday', help='The first 3 letters, all lowercase, of a weekday.', choices=['sun','mon','tue','wed','thu','fri','sat'])
	parser.add_argument('-hour', help='An hour of the day, specified from 0 to 23.', choices=[str(n) for n in range(24)])
	parser.add_argument('-filename', help='The name of a file containing a JSON array of timestamp data.')
	args = parser.parse_args()

	main(args)