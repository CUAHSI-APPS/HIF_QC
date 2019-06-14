'use strict';

import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';

import ReusableChart from './ReusableChart.jsx';

import './AddTestModal.css';

class AddTestModal extends React.Component {
  // static defaultProps = {
  //       testInfo: [],
  //   };

  constructor(props) {
    super(props);

    this.state = {subModalView:false,
                  visualizedDataStreams:[],
                  currentTest: this.props.testInfo[0]['Type']}

    //get columns from session storage
    this.colNames = JSON.parse(sessionStorage.getItem('dataCols'))

    this.handleSave = this.handleSave.bind(this);
    this.populateTestList = this.populateTestList.bind(this);
    this.handleAddData = this.handleAddData.bind(this);
    this.openSubMenu = this.openSubMenu.bind(this);
    this.closeSubmenu = this.closeSubmenu.bind(this);
    this.handleClose = this.handleClose.bind(this);
    this.handleSelections = this.handleSelections.bind(this);
    this.handleTestSelection = this.handleTestSelection.bind(this);

  }

  handleAddData(){
    let newDS = this.state.visualizedDataStreams.slice(1);
    this.props.addData(newDS);
    this.closeSubmenu();
  }

  handleClose(){
    this.state.visualizedDataStreams = [this.props.selectedDS];
    this.props.handleModalClose();
  }

   handleSave(){
     this.props.handleModalClose();
   }

   populateTestList(){

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

     console.log(this.state.visualizedDataStreams);

   }

   handleTestSelection(e){
     this.setState({currentTest:e.target.value});
   }

  render(){
    let testOptions, testConfigurations;
    let dataStreamOptions;

    testOptions = this.props.testInfo.map((test) => (
       <option>{test['Type']}</option>
     ));

     dataStreamOptions = this.colNames.map((dataStream) => {
       if(dataStream !== this.props.selectedDS){
            return <option>{dataStream}</option>
        }
     });

     testConfigurations = this.props.testInfo.map((test) => {
          if(!isDefined(this.state.currentTest)){
            return(null);
          }
          else if(this.state.currentTest === test['Type']){
            return(
              test['Parameters'].map((parameter) => (
                  <li><div className="row">
                    <div className="col-sm-5">{parameter['Name']}:</div>
                    <div className="col-sm-7"> <input/> </div>
                  </div></li>
              ))
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
                  <select style={{minWidth :'100%'}} onChange={this.handleTestSelection}>
                    {testOptions}
                   </select>
                   <div>
                     <ul>
                      {testConfigurations}
                     </ul>
                   </div>
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
