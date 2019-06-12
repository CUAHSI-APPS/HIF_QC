'use strict';

import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';

class AddTestModal extends React.Component {
  static defaultProps = {
        testInfo: [],
    };

  constructor(props) {
    super(props);

    this.handleSave = this.handleSave.bind(this);
    this.populateTestList = this.populateTestList.bind(this);
  }

   handleSave(){
     this.props.handleModalClose();
   }

   populateTestList(){



   }

  render(){
    return(
      <Modal show={this.props.active} onHide={this.props.handleModalClose}>
          <Modal.Header closeButton>
            <Modal.Title>Add a Test</Modal.Title>
          </Modal.Header>
          <Modal.Body>
              {this.props.testInfo.map((test) => (
                   <div>{test['Type']}</div>
                 ))
               }
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
