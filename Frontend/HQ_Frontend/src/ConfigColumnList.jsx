'use strict';

class ConfigColumnList extends React.Component {
  constructor(props) {
    super(props);
    this.state = {};
    this.colNames = props.dataColumns;

    this.handleSelection = this.handleSelection.bind(this);
  }

  //propogates selection back to parent scope
  handleSelection(event){
      this.props.updateSelCol(event.target.value);
  }

  render() {

    var dataColsList = this.colNames.map(
      function(col, i){
        return <option key={i}>{col}</option>
    })

    return (
      <div className="card-body">
          <h6>Data Fields</h6>
          <select multiple className="form-control selectBox" onChange={this.handleSelection}>
            {dataColsList}
          </select>
      </div>
    );
  }
}

export default ConfigColumnList;
//
// let domContainer = document.querySelector('#config-column-list');
// ReactDOM.render(<ConfigColumnList />, domContainer);
