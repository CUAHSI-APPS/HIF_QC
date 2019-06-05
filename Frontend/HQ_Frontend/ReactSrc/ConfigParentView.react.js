import ConfigColumnList from './ConfigColumnList.react.js';

'use strict';

class ConfigParentView extends React.Component {
  constructor(props) {
    super(props);
    this.state = {};
    this.colNames = sessionStorage.getItem('dataCols');

    this.handleSelection = this.handleSelection.bind(this);
  }

  emptyFun(){}

  handleSelection(event){

  }

  render() {

    return (
      <div className="card">
        <div className="row">
            <div className="col-sm-3">
              <ConfigColumnList dataColumns={this.colNames}/>
            </div>
            <div className="col-sm-3">
                <div className="card-body">
                    <h6>Data Field Metadata</h6>
                    <textarea type="text" rows="6" id="tbMeta" className="form-control selectBox" />
                    <div className="text-center pt-3">
                        <button disabled id="btnMeta" onClick={this.emptyFun} className="btn btn-secondary">Modify Metadata</button>
                    </div>
                </div>
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
