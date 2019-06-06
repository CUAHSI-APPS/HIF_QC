import ConfigColumnList from './ConfigColumnList.react.js';
import ConfigMetadataView from './ConfigMetadataView.react.js';

'use strict';

class ConfigParentView extends React.Component {
  constructor(props) {
    super(props);

    this.state = {selectedColumn: ''};
    this.colNames = JSON.parse(sessionStorage.getItem('dataCols'));

    this.fetchMetadata = this.fetchMetadata.bind(this);
  }

  emptyFun(){}


  fetchMetadata(colName){
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
    this.setState({metaData: sampleMetadata});
  }

  //enables propogation of selection back to this scope from
  // child scope
  //callback function
  updateSelectedColumn = (selected) => {
    this.setState({selectedColumn: selected});
    this.fetchMetadata(selected);
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
              <ConfigMetadataView selectedCol={this.state['selectedColumn']} metaData={this.state['Metadata']}/>
            </div>
            <div className="col-sm-6">
                <div className="card-body">
                    <h6>QC Test</h6>
                    <select id="selectTest" multiple className="form-control selectBox">
                    </select>
                    <div className="button-group text-center pt-3">
                        <button disabled id="btnAddTest" className="btn btn-secondary" onClick={this.emptyFun}>Add Test</button>
                        <button disabled id="btnModTest" className="btn btn-secondary" onClick={this.emptyFun}>Modify Test</button>
                        <button disabled id="btnRmvTest" className="btn btn-secondary" onClick={this.emptyFun}>Remove Test</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    );
  }
}

// <button disabled id="btnMeta" onClick="$('#modalMeta').modal('show');" className="btn btn-secondary">Modify Metadata</button>

// <button disabled id="btnAddTest" className="btn btn-secondary" onClick="$('#modalTest').modal('show');">Add Test</button>
// <button disabled id="btnModTest" className="btn btn-secondary" onClick="$('#modalTest').modal('show');">Modify Test</button>
// <button disabled id="btnRmvTest" className="btn btn-secondary" onClick="RemoveTest();">Remove Test</button>

let domContainer = document.querySelector('#config-parent-view');
ReactDOM.render(<ConfigParentView />, domContainer);
