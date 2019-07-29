'use strict';

import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';

import ReusableChart from './ReusableChart.jsx';

import './AddTestModal.css';

class AddTestModal extends React.Component {

  constructor(props) {
    super(props);

    this.state = {subModalView:false,
                  visualizedDataStreams:[],
                  currentTest: this.props.getFirstDefaultTest()['Type']}

    //get columns from session storage
    this.colNames = JSON.parse(sessionStorage.getItem('dataCols'))

    this.handleSave = this.handleSave.bind(this);
    this.handleAddData = this.handleAddData.bind(this);
    this.openSubMenu = this.openSubMenu.bind(this);
    this.closeSubmenu = this.closeSubmenu.bind(this);
    this.handleClose = this.handleClose.bind(this);
    this.handleSelections = this.handleSelections.bind(this);
    this.handleTestSelection = this.handleTestSelection.bind(this);
    this.handleRenderDifferentParamInputs = this.handleRenderDifferentParamInputs.bind(this);
    this.handleValueInput = this.handleValueInput.bind(this);
  }

  handleAddData(){
    //add all selected data stream except the current data stream (slice(1))
    let newDS = this.state.visualizedDataStreams.slice(1);
    this.props.addData(newDS);
    this.closeSubmenu();
  }

  handleClose(){
    this.state.visualizedDataStreams = [this.props.selectedDS];

    let defaultTest = this.props.getFirstDefaultTest();
    this.setState({currentTest: defaultTest['Type']});

    this.props.handleModalClose();
  }

  handleSave(){
    let possibleTests = [];
    let defaultTest = {};

    //generate id for deletion
    //modify with more complex id in the future
    this.props.testJSON['ID'] = this.props.testJSON['Type'];

    // run validation for spatial inconsistency
    //or something :/

    this.props.addTest(this.props.testJSON);
    possibleTests = this.props.setPossibleNewTests();

    if(possibleTests.length != 0){
      this.setState({currentTest: possibleTests[0]['Type']});
      this.props.handleModalClose(true);
    } else {
      this.props.handleModalClose(false);
    }

  }



  //submodal Functionality
  openSubMenu(){
   this.setState({subModalView:true});
  }

  closeSubmenu(){
   this.setState({subModalView:false});
  }

  handleSelections(e){
   let options = e.target.options;
   let defaultStream = this.props.selectedDS;

   //reset array and set default data stream as our current
   this.state.visualizedDataStreams = [];
   this.state.visualizedDataStreams.push(defaultStream);

   let selected = this.state.visualizedDataStreams;

   for(let option in options){
     if(options[option].selected){
       selected.push(options[option].value);
     }
   }


  }

  handleTestSelection(e){
    let testInfo;

    this.setState({currentTest:e.target.value});

    for(let test in this.props.testInfo){
       if(this.props.testInfo[test]['Type'] === e.target.value){
         testInfo = this.props.testInfo[test];
       }
    }

    //rebuild json
    this.props.rebuildJSON(testInfo);
  }

  handleValueInput(e){
    let parameterName = e.target.getAttribute('parameter-name');
    for(let parameter in this.props.testJSON['Parameters']){
      if(this.props.testJSON['Parameters'][parameter]['Name'] === parameterName){
        this.props.testJSON['Parameters'][parameter]['Value'] = e.target.value;
      }
    }
  }

  /* Function that manages the output of the correct tags for the data type
  of a particular parameter. Ultimiately will include error checking.
  */
  handleRenderDifferentParamInputs(parameter){
   let otherColumns;

   switch(parameter['Data Type']){
      case 'TimeSeries':
        let first = true;
        //get other columns as options
        otherColumns = this.colNames.map((dataStream) => {
          if(dataStream !== this.props.selectedDS){
               if(first){
                 return <option key={uuidv4()}>{dataStream}</option>
                 first = false;
               } else{
                 return <option key={uuidv4()}>{dataStream}</option>
               }
           }
        });

        return(<select key={uuidv4()} className="form-control" parameter-name={parameter['Name']} onChange={this.handleValueInput}>{otherColumns}</select>)
        break;

      default:
        return(<input key={uuidv4()} className="form-control" parameter-name={parameter['Name']} placeholder="0" onChange={this.handleValueInput}/>)
        break;
   }

  }

  render(){
    let testOptions, testConfigurations;
    let dataStreamOptions;
    let inputTagGroup;

    //pass test info down as subset of possible testTypes
    testOptions = this.props.testInfo.map((test) => {
      return(<option key={uuidv4()}>{test['Type']}</option>);
    });

     dataStreamOptions = this.colNames.map((dataStream) => {
       if(dataStream !== this.props.selectedDS){
            return <option key={uuidv4()}>{dataStream}</option>
        }
     });

     //Loading Test Configurations
     // Need to push this into a function
     testConfigurations = this.props.testInfo.map((test) => {
          if(!isDefined(this.state.currentTest)){
            return(null);
          }
          else if(this.state.currentTest === test['Type']){
            return(
              test['Parameters'].map((parameter) => {
                  inputTagGroup = this.handleRenderDifferentParamInputs(parameter);
                  return(
                  <>
                    <label key={uuidv4()}>{parameter['Name']}:</label>
                    {inputTagGroup}
                  </>
                  )
              })
            )
          }
          else {
            return(null);
          }
      });





    return(
      <>
        <Modal dialogClassName="wide-modal" show={this.props.active} onHide={this.props.handleModalClose}>
            <Modal.Header closeButton>
              <Modal.Title>Add a Test</Modal.Title>
            </Modal.Header>
            <Modal.Body>
              <div className="row">
                <div className="test col-sm-8">
                  <ReusableChart data={this.props.data}
                                 metaData={this.props.dataSetMetaData}
                                 />
                </div>
                <div className="col-sm-4">
                  <form>
                    <div className="form-group">
                       <select className="form-control" style={{minWidth :'100%'}} value={this.state['currentTest']} onChange={this.handleTestSelection}>
                        {testOptions}
                       </select>
                     </div>
                     <div className="form-group">
                      {testConfigurations}
                     </div>
                  </form>
               </div>
              </div>
            </Modal.Body>
            <Modal.Footer>
              <Button variant="secondary" onClick={this.openSubMenu}>
                Add Data
              </Button>
              <Button variant="secondary" onClick={this.props.handleModalClose}>
                Close Without Saving
              </Button>
              <Button variant="primary" onClick={this.handleSave}>
                Save Changes
              </Button>
            </Modal.Footer>
        </Modal>

        <Modal show={this.state.subModalView} onHide={this.closeSubmenu}>
            <Modal.Header closeButton>
              <Modal.Title>Add a Data Stream to the Visualization</Modal.Title>
            </Modal.Header>
            <Modal.Body>
              <select multiple={true} onChange={this.handleSelections}>
                {dataStreamOptions}
              </select>
            </Modal.Body>
            <Modal.Footer>
              <Button variant="secondary" onClick={this.handleAddData}>
                Add Selected Data
              </Button>
            </Modal.Footer>
        </Modal>
      </>
    );
  }
}


export default AddTestModal;
