import ConfigColumnList from './ConfigColumnList.jsx';
import ConfigMetadataView from './ConfigMetadataView.jsx';
import ConfigTestViews from './ConfigTestViews.jsx';
import AddTestModal from './AddTestModal.jsx'


'use strict';



class ConfigParentView extends React.Component {
  constructor(props) {
    super(props);

    this.clicks = 0;

    this.state = {selectedColumn: ''};
    this.colNames = JSON.parse(sessionStorage.getItem('dataCols'));
    this.metaData = {};
    this.testTypes = [];

    this.fetchTestTypes();

    this.fetchMetadata = this.fetchMetadata.bind(this);
    this.updateSelectedColumn = this.updateSelectedColumn.bind(this);
    this.updateDownloadedMetadata = this.updateDownloadedMetadata.bind(this);


    this.getData = this.getData.bind(this);
    this.dataCallJSON = {
      "dataColList": [],
      "indexCol": '',
      "timeStep": 10,
      "rateOfDownsample": 3
    }
    this.dataSourceEndpoint = "http://localhost:8082/data/vis/downsampled/"

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
        {'Name':'Comparision Data', 'Data Type': 'Vector'}, //column name from the same file
        {'Name':'Difference Threshold (%)', 'Data Type': 'Integer'}  //user will be able to select a different column
                                                          //from thier dataset
      ] },
      {'Type': 'Machine Learning', 'Parameters':[
        {'Name': 'Training Set', 'Data Type': 'Vector'}, //column name
        {'Name': 'Percentage Training Data', 'Data Type' : 'Integer'},
        {'Name': 'Percentage Test Data', 'Data Type' : 'Integer'}
      ]}
    ];
  }

  affixTestToCol(colName){

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
    this.setState({selectedColumn: selected});
    this.fetchMetadata(selected);
    this.getData(selected);
  }

  updateDownloadedMetadata(selected, modifiedMetaData){
    this.metaData[selected] = modifiedMetaData;
  }


   getData(selectedDataStream){

     this.dataCallJSON['indexCol'] = sessionStorage.getItem('indexCol');
     this.dataCallJSON['dataColList'] = [selectedDataStream];
     let endpoint = this.dataSourceEndpoint + sessionStorage.getItem('sessionId');

     console.log(endpoint, this.dataCallJSON);

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
          console.log(data);
          this.setState({retrievedData: data})
        }
      );

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
              retrievedData={this.state.retrievedData}/>
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
