#!/usr/bin/env python
import os
from flask import Flask, request, render_template, redirect, url_for
from redis import Redis
from werkzeug.utils import secure_filename
from Backend.Classes.Data import DataManager
from Backend.Classes.Vis import VisBuilder
import json
import util

# get current app directory
dir_path = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = dir_path + '/data/'

#data management
redis = Redis(host='redis', port=6379)
dataManager = DataManager(redis)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['COL_NAME'] = 'Temperature'
app.config['META_FILE'] = UPLOAD_FOLDER + 'meta_data.txt'


@app.route('/api/dropPreview/<int:rows>')
def drop_Preview(rows):
    filePath = dataManager.retrieveFileLoc(request.args.get('sessionId'))
    column_names = dataManager.getCols(filePath)
    data_part = dataManager.getData(filePath, rows)

    # column_names, data_part = util.preview_csv(app.config['UPLOAD_FOLDER']+'NRDC_data.csv', rows)
    return render_template('dropPreview.html',column_names=column_names, data_part=data_part)

@app.route('/api/dropPreviewColumnNames')
def dropPreviewColumnNames():
    #get column names
    filePath = dataManager.retrieveFileLoc(request.args.get('sessionId'))
    column_names = dataManager.getCols(filePath)

    return render_template('UploadColumns.html',column_names=column_names)


@app.route('/')
def index():
    # this is your index page
    return render_template('Step_1.html')

@app.route('/view/flagReview/<sessionId>')
def FetchFlagReview(sessionId):
    VB = VisBuilder();
    # get the name of our current time series column
    col = request.args.get('colName')
    # get flags
    fp = redis.get(sessionId+'outputcsv')
    flags = dataManager.getOutputAsDf(sessionId, fp)

    flags.to_csv('flags_debug.csv');

    indexCol = flags.index
    singleSeries = flags[col+"_flags"]

    flagobjs = []
    for i, flag in enumerate(singleSeries):
        obj = {}
        obj['code'] = flag
        obj['datetime'] = indexCol[i]
        flagobjs.append(obj)

    # build visualization
    fileName = dataManager.retrieveFileLoc(sessionId)
    dataCol = dataManager.retrieveOnlyDataCols(fileName, [col], None)[col]

    script, div = VB.BuildLineChart(indexCol, dataCol, singleSeries)


    return render_template('Step_5.html', colName=col, flags=flagobjs, okFlag="OK", chartScript=script, chartDiv=div)


@app.route('/view/SetStep/<page>',methods= ['POST', 'GET'])
def SetStep(page):


    # this is the returned page
    return render_template(page + '.html')

if __name__ == '__main__':
    app.debug = True
    ip = '0.0.0.0'
    portNum = 7999
    app.run(host=ip, port=portNum)
