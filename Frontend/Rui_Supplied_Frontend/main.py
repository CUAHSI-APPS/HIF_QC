import os
from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import json
import util

# get current app directory
dir_path = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = dir_path + '/data/'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['COL_NAME'] = 'Temperature'
app.config['META_FILE'] = UPLOAD_FOLDER + 'meta_data.txt'

@app.route('/api/post_csv', methods=['POST'])
def post_csv():
    # request.file <class 'werkzeug.datastructures.FileStorage'>
    # request.url is http://127.0.0.1:5000/api/post_csv
    # check if the post request has the file part
    if 'file' not in request.files:
        log = 'no file field in request.'
        return render_template('fail.html', log = log)
    # print(request.files['file'])
    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        log = 'Empty filename.'
        return render_template('fail.html', log = log)
        
    if file and util.allowed_file(file.filename):
        # get filename in a safe way
        filename = secure_filename(file.filename)
    # check if the data folder exists, if not create one
    if os.path.exists(app.config['UPLOAD_FOLDER']) == False:
        os.makedirs(app.config['UPLOAD_FOLDER'])

    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return render_template('Step_1.html',filename=filename)

@app.route('/api/dropPreview/<int:rows>')
def drop_Preview(rows):
    column_names, data_part = util.preview_csv(app.config['UPLOAD_FOLDER']+'NRDC_data.csv', rows)
    return render_template('dropPreview.html',column_names=column_names, data_part=data_part)

@app.route('/api/dropPreviewColumnNames')
def dropPreviewColumnNames():
    column_names, data_part = util.preview_csv(app.config['UPLOAD_FOLDER']+'NRDC_data.csv', 2)
    return render_template('UploadColumns.html',column_names=column_names)

@app.route('/api/process_csv/<lower_threshold>/<upper_threshold>')
def process_csv(lower_threshold='', upper_threshold=''):
    qualified, outlier = util.threshold_process_method(app.config['UPLOAD_FOLDER']+'NRDC_data.csv', app.config['COL_NAME'], float(lower_threshold), float(upper_threshold))
    return qualified

@app.route('/api/save/<lower>/<upper>', methods=['POST','GET'])
def save_csv(lower, upper):
    result_str = "Name : TempValue \nTempLower : " + lower + " \nTempUpper : " + upper
    text_file = open(app.config['META_FILE'], "w")
    text_file.write(result_str)
    text_file.close()

@app.route('/')
def index():
    # this is your index page
    return render_template('Step_1.html')

@app.route('/view/SetStep/<page>',methods= ['POST', 'GET'])
def SetStep(page):
    # this is the returned page
    return render_template(page + '.html')

if __name__ == '__main__':
    app.debug = True
    ip = '127.0.0.1'
    portNum = 7999
    app.run(host=ip, port=portNum)
