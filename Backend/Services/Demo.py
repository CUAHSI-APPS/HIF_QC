import sys
sys.path.append("../classes")
from Configuration import SourceConfiguration, TestConfiguration
from DataSource import DataBaseSource
from DataContainers import Measurement, DataStream, DataBundle
from Testing import Tester
from flask import Flask, jsonify, json, request
from flask_cors import cross_origin,CORS
from collections import Counter
from sqlalchemy.sql import text
import pyodbc
import time


app = Flask(__name__)
app.url_map.strict_slashes = False
cors = CORS(app, resources={r"/Demo/*": {"origins": "*"}})

#variables
Final = {}


# Service Functionality
@app.route('/Demo/Config')
@cross_origin()
def Get():

    # Try
    try:
        # Variable
        Num = 0
        global Final
        Final = {}
        DataStreamQuerySource = "SQLQueries/DetailedDataStreamQuery.sql"
        MeasurementQuerySource= "SQLQueries/measurementQuery.sql"
        TesterGroup = []

        # Connection Section
        config = SourceConfiguration("config/datasource.config")
        Final["Source Config XML"] = config.XMLString

        print(config.XMLString)

        DataSource = DataBaseSource(config)
        DataSource.TDSconfigure()

        DataStreams = DataSource.fetchDataStreams(DataStreamQuerySource)

        Final["Data Streams"] = []
        for Stream in DataStreams:
             Final["Data Streams"].append(Stream.MetaData);

             print(Stream.MetaData)

        DataStreams = DataSource.fetchMeasurements(DataStreams, MeasurementQuerySource)

        Final["Measurements"] = {}
        for Stream in DataStreams:
            Final["Measurements"][Stream.StreamID] = len(Stream.Measurements)

            print( "Number of Measurements from DataStream ", Stream.StreamID, " :", len(Stream.Measurements) )

        TestConfig = TestConfiguration("config/tests.config")

        Final["Test Configuration"] = TestConfig.XMLString

        for Stream in DataStreams:
            TesterGroup.append( Tester( TestConfig.TestParameters[str(Stream.StreamID)] , Stream ) )

        begin = time.time()	


        for TesterObj in TesterGroup:
            TesterObj.RunTests()

        end = time.time()

        Final["Testing Time"] = (end - begin)

        for TesterObj in TesterGroup:
            Num +=1
            Final[str(Num)] = DataSource.writeFlagsToDataStream(TesterObj.DataStream.StreamID, TesterObj.DataStream.Measurements)


        #Serialize
        return jsonify({"Status":"Complete"})

    # Except
    except Exception as e:
        print(str(e))
        line = 'Error on line {}'.format(sys.exc_info()[-1].tb_lineno)
        print(line)
        return False, str(e), line

# Service Functionality
@app.route('/Demo/Run')
@cross_origin()
def Run():

    # Try
    try:

        #Serialize
        return jsonify(Final)

    # Except
    except Exception as e:
        print(str(e))
        line = 'Error on line {}'.format(sys.exc_info()[-1].tb_lineno)
        print(line)
        return False, str(e), line

# Run Main
if __name__ == '__main__':
	# Set to False when deploying
	app.debug = False
	app.run(host='127.0.0.1', port=8069)
