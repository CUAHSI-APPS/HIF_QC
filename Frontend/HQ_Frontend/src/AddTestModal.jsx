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
                  invalidInput:true}

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
    this.getInstructions = this.getInstructions.bind(this);
    // this.validateInput = this.validateInput.bind(this);
  }

  validateInput(parameter){
      let localState = false;
      for(let parameter in this.props.testJSON['Parameters']){
        if(this.props.testJSON['Parameters'][parameter]['Required'] && (this.props.testJSON['Parameters'][parameter]['Value'] === '' || !isDefined(this.props.testJSON['Parameters'][parameter]['Value'])) ){
          localState = true;
        }
      }
      this.setState({invalidInput: localState});
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
    this.props.setFirstDefaultTest(defaultTest['Type']);

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
      this.props.setFirstDefaultTest(possibleTests[0]['Type']);
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

    this.props.setFirstDefaultTest(e.target.value);

    for(let test in this.props.testInfo){
       if(this.props.testInfo[test]['Type'] === e.target.value){
         testInfo = this.props.testInfo[test];
       }
    }

    //reset validity
    this.setState({invalidInput:true});

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


    this.validateInput();


  }

  getInstructions(){

    var test = this.props.testInfo.find(test => {
        if(!isDefined(this.props.currentTest)){
          return(null);
        }
        return test['Type'] == this.props.currentTest;
    });

    if (test !== null && isDefined(test)){
      return <p>{test['Instructions']}</p>
    }
  };

  /* Function that manages the output of the correct tags for the data type
  of a particular parameter. Ultimiately will include error checking.
  */
  handleRenderDifferentParamInputs(parameter){
   let otherColumns, options;

   switch(parameter['Data Type']){
      case 'TimeSeries':
        let first = true

        //get other columns as options
        otherColumns = this.colNames.map((dataStream) => {
          if(dataStream !== this.props.selectedDS){
               if(first){
                 first = false;
                 for(let p in this.props.testJSON['Parameters']){
                   if(this.props.testJSON['Parameters'][p]['Name'] === parameter['Name']){
                     this.props.testJSON['Parameters'][p]['Value'] = dataStream;
                   }
                 }
                 return <option key={uuidv4()} select="selected">{dataStream}</option>
               } else{
                 return <option key={uuidv4()}>{dataStream}</option>
               }
           }
        });

        return(<select key={uuidv4()} className="form-control" parameter-name={parameter['Name']} onChange={this.handleValueInput}>{otherColumns}</select>)
        break;

      case 'Time Resolution':
        first = true;
        options = parameter['Options'].map( (option) => {

          if(first){
            first = false;
            for(let p in this.props.testJSON['Parameters']){
              if(this.props.testJSON['Parameters'][p]['Name'] === parameter['Name']){
                this.props.testJSON['Parameters'][p]['Value'] = option;
              }
            }
            return <option key={uuidv4()} select="selected">{option}</option>
          } else{
            return <option key={uuidv4()}>{option}</option>
          }

        })

        return(<select key={uuidv4()} className="form-control" parameter-name={parameter['Name']} onChange={this.handleValueInput}>{options}</select>)
        break;

      default:
        return(<input key={`${parameter['Name']}_key`} className="form-control" parameter-name={parameter['Name']} placeholder="-" onChange={this.handleValueInput}/>)
        break;
   }


  }

  render(){
    let testOptions, testConfigurations, getInstructions;
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
          if(!isDefined(this.props.currentTest)){
            return(null);
          }
          else if(this.props.currentTest === test['Type']){
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
                       {this.getInstructions()}
                       <select className="form-control" style={{minWidth :'100%'}} value={this.props['currentTest']} onChange={this.handleTestSelection}>
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
              <Button variant="primary" onClick={this.handleSave} disabled={this.state.invalidInput}>
                Save Changes
              </Button>
            </Modal.Footer>
        </Modal>

        <Modal show={this.state.subModalView} onHide={this.closeSubmenu}>
            <Modal.Header closeButton>
              <Modal.Title>
                Add a Data Stream to the Visualization
              </Modal.Title>
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
