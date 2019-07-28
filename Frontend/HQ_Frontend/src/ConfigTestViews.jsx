import AddTestModal from './AddTestModal.jsx';
import './ConfigTestViews.css'


'use strict';

class ConfigTestViews extends React.Component {
  constructor(props) {
    super(props);

    this.state = {addTestModal: false,
                  modTestModal: false,
                  selectedTest: null,
                  possibleTests: this.props.testTypes};

    this.tempTestJSON = {};


    this.handleAddTest = this.handleAddTest.bind(this);
    this.handleModTest = this.handleModTest.bind(this);
    this.handleModalClose = this.handleModalClose.bind(this);
    this.rebuildTempTestJSON = this.rebuildTempTestJSON.bind(this);
    this.getFirstDefaultTest = this.getFirstDefaultTest.bind(this);
    this.showActiveTests = this.showActiveTests.bind(this);
    this.setPossibleNewTests = this.setPossibleNewTests.bind(this);
    this.testSelected = this.testSelected.bind(this);
    this.disableModRmv = this.disableModRmv.bind(this);
    this.handleRmvTest = this.handleRmvTest.bind(this);

  }

  getFirstDefaultTest(){
      return this.state.possibleTests[0];
  }

  //start here tomorrow
  setPossibleNewTests(){
    let possibleTests = [];
    let at = this.props.activeTests;

    //filter already configured tests
    possibleTests = this.props.testTypes.filter((testType) => {
        let valid = true;

        if(isDefined(at) &&
            at != 0){
          for(let test in at){
            if(at[test]['Type'] === testType['Type']){
              valid = false;
            }
          }
        }

        if(valid){
          return testType;
        }

    });

    this.setState({possibleTests:possibleTests});

    return possibleTests;
  }

  handleAddTest(){
    let possibleTests;

    this.setState({addTestModal:true});
    this.setState({modTestModal:false});

    //set temp test json clear
    //pending development of first default test
    possibleTests = this.setPossibleNewTests();

    let defaultTest = possibleTests[0];
    this.rebuildTempTestJSON(defaultTest);
  }

  handleModTest(){
    this.setState({addTestModal:false});
    this.setState({modTestModal:true});
  }

  handleRmvTest(){
    //fetch id using this.state.selectedTest and delete
    this.props.deleteTest(this.state.selectedTestId)
  }

  handleModalClose(isAddValid){
    this.props.clearData();

    this.setState({addTestModal:false});
    this.setState({modTestModal:false});
  }

  rebuildTempTestJSON(testInfo){
    this.tempTestJSON['Type'] = testInfo['Type'];
    this.tempTestJSON['Parameters'] = [];

    testInfo['Parameters'].map((val, ndx) => {
      this.tempTestJSON['Parameters'][ndx] = JSON.parse(JSON.stringify(val))
    })
  }

  testSelected(e){
    this.setState({selectedTest:e.target.value});
    this.setState({selectedTestId:e.target.getAttribute('test-id')})
  }

  disableModRmv(){

    if(!isDefined(this.props.activeTests)){
      return true;
    }
    else if(this.props.activeTests.length == 0) {
      return true;
    } else if(this.state.selectedTest === null){
      return true;
    } else {
      return false;
    }

  }

  showActiveTests(){
    if(isDefined(this.props.activeTests)){
      return( this.props.activeTests.map( (test) => {
        return(
          <option test-id={test['ID']} onClick={this.testSelected}>{test['Type']}</option>
        );
      }));
    } else {
      return(null);
    }
  }

// We need to disable the add test button until data is loaded!
  render(){
    let activeTests = this.showActiveTests();
    return(
      <>
        <div className="card-body">
            <h6>QC Test</h6>
            <select id="selectTest" multiple className="form-control selectBox test-list">
              {activeTests}
            </select>
            <div className="button-group text-center pt-3">
                <button disabled={!this.props.dataLoaded} id="btnAddTest" className="btn btn-secondary mx-1" onClick={this.handleAddTest}>Add Test</button>
                <button disabled={this.disableModRmv()} id="btnModTest" className="btn btn-secondary mx-1" onClick={this.handleModTest}>Modify Test</button>
                <button disabled={this.disableModRmv()} id="btnRmvTest" className="btn btn-secondary mx-1" onClick={this.handleRmvTest}>Remove Test</button>
            </div>
        </div>
        <AddTestModal
        active={this.state.addTestModal}
        testInfo={this.state.possibleTests}
        handleModalClose={this.handleModalClose}
        selectedDS={this.props.selectedCol}
        dataSetMetaData={this.props.metaData}
        data={this.props.retrievedData}
        addData={this.props.addData}
        testJSON={this.tempTestJSON}
        rebuildJSON={this.rebuildTempTestJSON}
        getFirstDefaultTest={this.getFirstDefaultTest}
        addTest={this.props.addTest}
        setPossibleNewTests={this.setPossibleNewTests}/>
      </>
    );
  }
}


export default ConfigTestViews;
