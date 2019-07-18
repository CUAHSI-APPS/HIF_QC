import ConfigColumnList from './ConfigColumnList.jsx';
import ConfigMetadataView from './ConfigMetadataView.jsx';
import ConfigTestViews from './ConfigTestViews.jsx';
import AddTestModal from './AddTestModal.jsx'


'use strict';



class ConfigParentView extends React.Component {
  constructor(props) {
    super(props);

    //Variable initializations
    this.clicks = 0;
    this.dataCallJSON = {
      "dataColList": [],
      "indexCol": '',
      "timeStep": 10,
      "rateOfDownsample": 3
    }
    this.dataSourceEndpoint = "http://localhost:8082/data/vis/downsampled/"
    this.state = {selectedColumn: '', dataLoaded:false};
    this.colNames = JSON.parse(sessionStorage.getItem('dataCols'));
    this.metaData = {};
    this.testTypes = [];
    this.allTests = {};

    //bindings
    this.fetchMetadata = this.fetchMetadata.bind(this);
    this.updateSelectedColumn = this.updateSelectedColumn.bind(this);
    this.updateDownloadedMetadata = this.updateDownloadedMetadata.bind(this);
    this.clearData = this.clearData.bind(this);
    this.getData = this.getData.bind(this);
    this.addData = this.addData.bind(this);
    this.updateSelectedTests = this.updateSelectedTests.bind(this);
    this.addTest = this.addTest.bind(this);
    this.deleteTest = this.deleteTest.bind(this);

    //function calls on construct
    this.fetchTestTypes();

  }

  fetchTestTypes(){
    //replace with a call to server here
    //tests should be a list I suppose, of objects

    this.testTypes = [
      {'Type':'Basic Outlier Test',
        'Parameters':[
          {'Name':'Max', 'Data Type':'Float', 'Default Value': 10},
          {'Name':'Min', 'Data Type':'Float'}
        ],
        'Validation Reqs': ['"Max" > "Min"'],
        'Output': 'null'},
      {'Type':'Repeat Value Test', 'Parameters':[
        {'Name': 'Repeating Threshold', 'Data Type': 'Integer'}
      ]},
      {'Type':'Spatial Inconsistency', 'Parameters':[
        {'Name':'Comparision Data', 'Data Type': 'TimeSeries'}, //column name from the same file
        {'Name':'Difference Threshold (%)', 'Data Type': 'Integer'}  //user will be able to select a different column
                                                          //from thier dataset
      ] },
      {'Type': 'Machine Learning', 'Parameters':[
        {'Name': 'Training Set', 'Data Type': 'TimeSeries'}, //column name
        {'Name': 'Percentage Training Data', 'Data Type' : 'Integer'},
        {'Name': 'Percentage Test Data', 'Data Type' : 'Integer'}
      ]}
    ];
  }


  fetchMetadata(colName){

    if(typeof this.metaData[colName] === 'undefined'){
      var sampleMetadata = {
        'Mean': 25,
        'Standard Deviation': 9.3,
        'Greatest Value': 112,
        'Lowest Value': -83,
        'Units': '',
        'Data Type': '',
        'General Category': '',
        'Time Interval': ''
      }

      this.clicks += 1;
      sampleMetadata['Mean'] += this.clicks;
      this.setState({metaData: sampleMetadata});
      this.metaData[colName] = sampleMetadata;
    } else {
      this.setState({metaData: this.metaData[colName]});
    }

    console.log(this.metaData);
  }

  //enables propogation of selection back to this scope from
  // child scope
  //callback function
  updateSelectedColumn(selected){
    //set new selected column
    this.setState({selectedColumn: selected});

    //reset for new download of data
    this.setState({dataLoaded: false});
    this.setState({selectedColUpdated:true});
    this.fetchMetadata(selected);
    this.getData(selected);
    this.updateSelectedTests(selected);
  }

  updateDownloadedMetadata(selected, modifiedMetaData){
    this.metaData[selected] = modifiedMetaData;
  }




   getData(selectedDataStream){

     this.dataCallJSON['indexCol'] = sessionStorage.getItem('indexCol');
     this.dataCallJSON['dataColList'] = [selectedDataStream];
     let endpoint = this.dataSourceEndpoint + sessionStorage.getItem('sessionId');


     //makeAsyncCall
     fetch(endpoint, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(this.dataCallJSON)
      }).then( (response) => {
            return response.json();
        }
      ).then((json) => {
          var data = json[selectedDataStream].map((x) => {
            if( x['y'] === 'null'){
              x['y'] = null;
            }
            x['x'] = new Date(Date.parse(x['x']))
            return x;
          })

          this.setState({retrievedData: [data]});
          this.setState({dataLoaded: true});
        }
      );

   }

   //new datastreams is an array of datastreams by default
   addData(newDataStreams){
     this.dataCallJSON['indexCol'] = sessionStorage.getItem('indexCol');
     this.dataCallJSON['dataColList'] = newDataStreams;
     let endpoint = this.dataSourceEndpoint + sessionStorage.getItem('sessionId');

     //makeAsyncCall
     fetch(endpoint, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(this.dataCallJSON)
      }).then( (response) => {
            return response.json();
        }
      ).then((json) => {

        let newData = this.state.retrievedData;

        for(let stream in newDataStreams){
          var data = json[newDataStreams[stream]].map((x) => {
            if( x['y'] === 'null'){
              x['y'] = null;
            }
            x['x'] = new Date(Date.parse(x['x']))
            return x;
          })

          newData.push(data);

          this.setState({retrievedData:newData});

        }

      }
      );
   }

   clearData(){
      if(this.state.retrievedData.length > 1)
        this.getData(this.state.selectedColumn);
   }

   //test management functions

   //Updates the current class of selected test wehn the selected column changes
   updateSelectedTests(selectedCol){
     if(!isDefined(this.allTests[selectedCol])){
       this.allTests[selectedCol] = [];
     }

     this.setState({activeTests: this.allTests[selectedCol]});
   }

   //callback function to be called from a deeper scope when a test is added
   addTest(newTest){
     this.allTests[this.state.selectedColumn].push(JSON.parse(JSON.stringify(newTest)));
     this.setState({activeTests: this.allTests[this.state.selectedColumn]});

      // not the greatest I know...
      if (Object.keys(this.allTests).length > 0) {
        var nextStepButton = document.getElementById('nextTaskStep3');
        nextStepButton.removeAttribute('disabled');
      }

   }

   //callback function to be called from a deeper scope when a function is deleted
   deleteTest(delTestID){
     for (var test in this.allTests[this.state.selectedColumn]){
       if(this.allTests[this.state.selectedColumn][test]['ID'] === delTestID){
         this.allTests[this.state.selectedColumn].splice(test,1);
       }
     }
     this.setState({activeTests: this.allTests[this.state.selectedColumn]});
   }

  render() {

    return (
      <div className="card">
        <div className="row">
            <div className="col-sm-3">
              <ConfigColumnList dataColumns={this.colNames} updateSelCol={this.updateSelectedColumn}/>
              <div>Current Selection: {this.state['selectedColumn']}</div>
            </div>
            <div className="col-sm-3">
              <ConfigMetadataView
                selectedCol={this.state['selectedColumn']}
                metaData={this.state.metaData}
                updateDownloadedMetadata={this.updateDownloadedMetadata}/>
            </div>
            <div className="col-sm-6">
              <ConfigTestViews
              selectedCol={this.state['selectedColumn']}
              metaData={this.state.metaData}
              testTypes={this.testTypes}
              retrievedData={this.state.retrievedData}
              clearData={this.clearData}
              addData={this.addData}
              dataLoaded={this.state.dataLoaded}
              activeTests={this.state.activeTests}
              addTest={this.addTest}
              deleteTest={this.deleteTest}/>
            </div>
        </div>
    </div>
    );
  }
}


window.loadReactApp = function(){
  let domContainer = document.querySelector('#config-parent-view');
  ReactDOM.render(<ConfigParentView />, domContainer);
};


export default ConfigParentView;
