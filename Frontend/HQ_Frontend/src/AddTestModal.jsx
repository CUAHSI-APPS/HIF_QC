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

    this.state = {retrievedData:[]}

    this.handleSave = this.handleSave.bind(this);
    this.populateTestList = this.populateTestList.bind(this);
    this.getData = this.getData.bind(this);
  }

    //in case we need to remove data from state
   cleanupData(){

   }

   handleSave(){
     this.props.handleModalClose();
   }

   getData(selectedDataStream){
     //makeAsyncCall
     console.log(selectedDataStream);
   }

   populateTestList(){

   }

  render(){
    let testOptions;
    testOptions = this.props.testInfo.map((test) => (
       <option>{test['Type']}</option>
     ))

     this.getData(this.props.selectedDS);


    return(
      <Modal dialogClassName="wide-modal" show={this.props.active} onHide={this.props.handleModalClose}>
          <Modal.Header closeButton>
            <Modal.Title>Add a Test</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <div className="row">
              <div className="test col-sm-10">
                <ReusableChart data={this.state.retrievedData}
                               metaData={this.props.dataSetMetaData}
                               />
              </div>
              <div className="col-sm-2">
              <select>
                {testOptions}
               </select>
               </div>
             </div>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={this.props.handleModalClose}>
              Close Without Saving
            </Button>
            <Button variant="primary" onClick={this.handleSave}>
              Save Changes
            </Button>
          </Modal.Footer>
      </Modal>
    );
  }
}


export default AddTestModal;
