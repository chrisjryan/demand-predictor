#!/usr/bin/enc python

from flask import Flask, jsonify, request
import os

import dataprep

app = Flask(__name__)





@app.route('/api/alldata', methods = ['GET'])
def get_alldata():
    """
    Return all the timetamp data as a JSON file.
    """
    return jsonify( { 'logins': logindata } )


# @app.route('/api/predict', methods = [''])
# def predict_demand():



# let this be a single-datum post method. Include another that updates the logindata file as a batch and then computes statistics all at the end.
@app.route('/api/post', methods = ['POST'])
def post_data():


	# TODO: handle any cases where request.data is not a properly formatted string.
    # if not request.data or not 'title' in request.json:
    #     abort(400)
    logindata.append(request.data)

    # update any stats accordingly (or)

    # return info, like the new predictions?


if __name__ == '__main__':

	# load pre-existing data:
    # datafile = 'hourly_demand_prediction_challenge.json'
    datafile = ''
    if os.path.isfile(datafile):
	    logindata = dataprep.load_json(datafile)
    else:
        logindata = []

    # note: logindata will be a list of [unicode] strings

    # compute any statistics:
    # hours, usage = dataprep.prepare(datafile)

    # run the API:
    app.run(debug = True)



