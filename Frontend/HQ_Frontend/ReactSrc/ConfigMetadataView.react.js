'use strict';

//import '../css/ConfigMetadataView.react.css'

class ConfigMetadataView extends React.Component {
  static defaultProps = {
        metaData: {
            'key': []
        }
    };

  constructor(props) {
    super(props);
    this.state = {};
  }

  render() {

    return (
      <div className="card-body">
          <h6>Data Field Metadata</h6>
          <div className="md-display">
          <ul>
            <li>Name: <span>{this.props.selectedCol}</span></li>
            {Object.keys(this.props.metaData).map( (key, index) => (
              <li>{key} : <span> {this.props.metaData[key]} </span> </li>
            ))}
          </ul>
          </div>
          <div className="text-center pt-3">
              <button disabled id="btnMeta" onClick={this.emptyFun} className="btn btn-secondary">Modify Metadata</button>
          </div>
      </div>
    );
  }
}

export default ConfigMetadataView;
//
// let domContainer = document.querySelector('#config-column-list');
// ReactDOM.render(<ConfigColumnList />, domContainer);
