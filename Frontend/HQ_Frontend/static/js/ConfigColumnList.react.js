'use strict';

class ConfigColumnList extends React.Component {
  constructor(props) {
    super(props);
    this.state = {};
    this.colNames = props.dataColumns;
    console.log(props.dataColumns);

    this.handleSelection = this.handleSelection.bind(this);
  }

  handleSelection(event) {
    console.log(event);
    SetMeta("this", '0', '0');
  }

  render() {

    return React.createElement(
      'div',
      { className: 'card-body' },
      React.createElement(
        'h6',
        null,
        'Data Fields'
      ),
      React.createElement(
        'select',
        { multiple: true, className: 'form-control selectBox', onChange: this.handleSelection },
        React.createElement(
          'option',
          null,
          'TempValue'
        )
      )
    );
  }
}

export default ConfigColumnList;
//
// let domContainer = document.querySelector('#config-column-list');
// ReactDOM.render(<ConfigColumnList />, domContainer);