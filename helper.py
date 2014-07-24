#!/user/bin/env python

import argparse
import requests


def predictor(weekday, hour):
	"""
	Uses the hourly-demand API to return a predicted usage at some 
	weekday and hour. Weekdays should be specified by a 3 letter 
	string, and hours should be specified as an int between 0 an 23.
	Assumes that the API is running on http://localhost:5000.
	[doctest]
	"""
	daylist = ['sun','mon','tue','wed','thu','fri','sat']

	if weekday.lower() not in daylist:
		return 'Error: please choose a weekday by specifying the first 3 letters of one.'

	if hour <= 0 or hour >= 23:
		return 'Error: please specify an hour between 0 and 23.' 

	day_idx = {d:idx for idx,d in enumerate(daylist)}
	d = str(day_idx[weekday.lower()]) + ',' +str(hour)
	r = requests.get('http://localhost:5000/api/predict', data=d)

	return r.json()


if __name__ == '__main__':

	# parse the terminal input:
	desc = "A helper script for using the demand predictor API."
	parser = argparse.ArgumentParser(description=desc, formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument('weekday', help='The first 3 letters, all lowercase, of a weekday.', choices=['sun','mon','tue','wed','thu','fri','sat'])
	parser.add_argument('hour', help='An hour of the day, specified from 0 to 23.', choices=[str(n) for n in range(24)])
	args = parser.parse_args()

	stats = predictor(args.weekday, args.hour)
	
	for k,v in stats.iteritems():
		print '%-25s %f' % (k,v)