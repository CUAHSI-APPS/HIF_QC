import AddTestModal from './AddTestModal.jsx';



'use strict';

class ConfigTestViews extends React.Component {
  constructor(props) {
    super(props);

    this.state = {addTestModal: false,
                  modTestModal: false};

    this.emptyFun = this.emptyFun.bind(this);
    this.handleAddTest = this.handleAddTest.bind(this);
    this.handleModTest = this.handleModTest.bind(this);
    this.handleModalClose = this.handleModalClose.bind(this);
  }

  handleAddTest(){
    this.setState({addTestModal:true});
    this.setState({modTestModal: false});
  }

  handleModTest(){
    this.setState({addTestModal:false});
    this.setState({modTestModal:true});
  }

  handleModalClose(){
    this.setState({addTestModal:false});
    this.setState({modTestModal:false});
  }

  emptyFun(){}

  render(){
    return(
      <>
        <div className="card-body">
            <h6>QC Test</h6>
            <select id="selectTest" multiple className="form-control selectBox">
            </select>
            <div className="button-group text-center pt-3">
                <button  id="btnAddTest" className="btn btn-secondary" onClick={this.handleAddTest}>Add Test</button>
                <button disabled id="btnModTest" className="btn btn-secondary" onClick={this.handleModTest}>Modify Test</button>
                <button disabled id="btnRmvTest" className="btn btn-secondary" onClick={this.emptyFun}>Remove Test</button>
            </div>
        </div>
        <AddTestModal
        active={this.state.addTestModal}
        testInfo={this.props.testTypes}
        handleModalClose={this.handleModalClose}
        selectedDS={this.props.selectedCol}
        dataSetMetaData={this.props.metaData}/>
      </>
    );
  }
}


export default ConfigTestViews;
