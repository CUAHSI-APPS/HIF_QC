'use strict';

import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';


class ConfigMetadataView extends React.Component {


  constructor(props) {
    super(props);
    this.state = {
      show:false,
    };

    if(isDefined(this.props.metaData)){
      this.temp = JSON.parse(JSON.stringify(this.props.metaData));
    }

    this.handleClose = this.handleClose.bind(this);
    this.handleShow = this.handleShow.bind(this);
    this.manageInput = this.manageInput.bind(this);
    this.handleSave = this.handleSave.bind(this);
  }

  manageInput(e){
    var field = e.target.getAttribute("field");

    this.temp[field] = e.target.value;

  }

  handleClose() {
      this.temp = null;
      this.setState({ show: false });
   }

   handleSave(){
     for(var field in this.temp){
       this.props.metaData[field] = this.temp[field];
     }
     this.setState({ show: false });
   }

   handleShow() {
     //does a deep copy to ensure changes are not propogated back to our main state
     // if not explicitly saved
     if(isDefined(this.props.metaData)){
       this.temp = JSON.parse(JSON.stringify(this.props.metaData));
     }



     this.setState({ show: true });
   }

  render() {
    let md, mdedit;

    if( isDefined(this.props.metaData) ){
      md = Object.keys(this.props.metaData).map( (key, index) => (
        <li key={'li'+key}>{key} : <span key={key}> {this.props.metaData[key]} </span> </li>
      ))

      mdedit = Object.keys(this.props.metaData).map( (key, index) => (
        <li key={'mli'+key}>{key} : <input type='text' key={key} field={key} defaultValue={this.props.metaData[key]} onChange={this.manageInput} /> </li>
      ))
    }
    else{
      md = null;
      mdedit = null;
    }



    return (
      <>
        <div className="card-body">
            <h6>Data Field Metadata</h6>
            <div className="md-display">
            <ul>
              <li>Name: <span>{this.props.selectedCol}</span></li>
              {md}
            </ul>
            </div>
            <div className="text-center pt-3">
                <button id="btnMeta" onClick={this.handleShow} className="btn btn-secondary">Modify Metadata</button>
            </div>
        </div>

        <Modal show={this.state.show} onHide={this.handleClose}>
            <Modal.Header closeButton>
              <Modal.Title>Modify Metadata</Modal.Title>
            </Modal.Header>
            <Modal.Body>
            <ul>
              <li>Name: <span>{this.props.selectedCol}</span></li>
              {mdedit}
            </ul>
            </Modal.Body>
            <Modal.Footer>
              <Button variant="secondary" onClick={this.handleClose}>
                Close Without Saving
              </Button>
              <Button variant="primary" onClick={this.handleSave}>
                Save Changes
              </Button>
            </Modal.Footer>
        </Modal>
      </>
    );
  }
}

export default ConfigMetadataView;
//
// let domContainer = document.querySelector('#config-column-list');
// ReactDOM.render(<ConfigColumnList />, domContainer);
