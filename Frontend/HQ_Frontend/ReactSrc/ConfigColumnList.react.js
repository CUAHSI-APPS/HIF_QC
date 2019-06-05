'use strict';

class ConfigColumnList extends React.Component {
  constructor(props) {
    super(props);
    this.state = {};
    this.colNames = props.dataColumns;
    console.log(props.dataColumns);

    this.handleSelection = this.handleSelection.bind(this);
  }

  handleSelection(event){
      console.log(event);
      SetMeta("this", '0', '0');
  }

  render() {

    return (
      <div className="card-body">
          <h6>Data Fields</h6>
          <select multiple className="form-control selectBox" onChange={this.handleSelection}>
              <option>TempValue</option>
          </select>
      </div>
    );
  }
}

export default ConfigColumnList;
//
// let domContainer = document.querySelector('#config-column-list');
// ReactDOM.render(<ConfigColumnList />, domContainer);
