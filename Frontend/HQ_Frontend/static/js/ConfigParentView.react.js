var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

import ConfigColumnList from './ConfigColumnList.react.js';
import ConfigMetadataView from './ConfigMetadataView.react.js';

'use strict';

var ConfigParentView = function (_React$Component) {
  _inherits(ConfigParentView, _React$Component);

  function ConfigParentView(props) {
    _classCallCheck(this, ConfigParentView);

    var _this = _possibleConstructorReturn(this, (ConfigParentView.__proto__ || Object.getPrototypeOf(ConfigParentView)).call(this, props));

    _this.updateSelectedColumn = function (selected) {
      _this.setState({ selectedColumn: selected });
      _this.fetchMetadata(selected);
    };

    _this.clicks = 0;

    _this.state = { selectedColumn: '' };
    _this.colNames = JSON.parse(sessionStorage.getItem('dataCols'));
    _this.metaData = {};

    _this.fetchMetadata = _this.fetchMetadata.bind(_this);
    return _this;
  }

  _createClass(ConfigParentView, [{
    key: 'emptyFun',
    value: function emptyFun() {}
  }, {
    key: 'fetchMetadata',
    value: function fetchMetadata(colName) {

      if (typeof this.metaData[colName] === 'undefined') {
        var sampleMetadata = {
          'Mean': 25,
          'Standard Deviation': 9.3,
          'Greatest Value': 112,
          'Lowest Value': -83,
          'Units': '',
          'Data Type': '',
          'General Category': '',
          'Time Interval': ''
        };

        this.clicks += 1;
        sampleMetadata['Mean'] += this.clicks;
        this.setState({ metaData: sampleMetadata });
        this.metaData[colName] = sampleMetadata;
      } else {
        this.setState({ metaData: this.metaData[colName] });
      }

      console.log(this.metaData);
    }

    //enables propogation of selection back to this scope from
    // child scope
    //callback function

  }, {
    key: 'render',
    value: function render() {

      return React.createElement(
        'div',
        { className: 'card' },
        React.createElement(
          'div',
          { className: 'row' },
          React.createElement(
            'div',
            { className: 'col-sm-3' },
            React.createElement(ConfigColumnList, { dataColumns: this.colNames, updateSelCol: this.updateSelectedColumn }),
            React.createElement(
              'div',
              null,
              'Current Selection: ',
              this.state['selectedColumn']
            )
          ),
          React.createElement(
            'div',
            { className: 'col-sm-3' },
            React.createElement(ConfigMetadataView, {
              selectedCol: this.state['selectedColumn'],
              metaData: this.state.metaData,
              updateDownloadedMetadata: this.updateDownloadedMetadata })
          ),
          React.createElement(
            'div',
            { className: 'col-sm-6' },
            React.createElement(
              'div',
              { className: 'card-body' },
              React.createElement(
                'h6',
                null,
                'QC Test'
              ),
              React.createElement('select', { id: 'selectTest', multiple: true, className: 'form-control selectBox' }),
              React.createElement(
                'div',
                { className: 'button-group text-center pt-3' },
                React.createElement(
                  'button',
                  { disabled: true, id: 'btnAddTest', className: 'btn btn-secondary', onClick: this.emptyFun },
                  'Add Test'
                ),
                React.createElement(
                  'button',
                  { disabled: true, id: 'btnModTest', className: 'btn btn-secondary', onClick: this.emptyFun },
                  'Modify Test'
                ),
                React.createElement(
                  'button',
                  { disabled: true, id: 'btnRmvTest', className: 'btn btn-secondary', onClick: this.emptyFun },
                  'Remove Test'
                )
              )
            )
          )
        )
      );
    }
  }]);

  return ConfigParentView;
}(React.Component);

// <button disabled id="btnMeta" onClick="$('#modalMeta').modal('show');" className="btn btn-secondary">Modify Metadata</button>

// <button disabled id="btnAddTest" className="btn btn-secondary" onClick="$('#modalTest').modal('show');">Add Test</button>
// <button disabled id="btnModTest" className="btn btn-secondary" onClick="$('#modalTest').modal('show');">Modify Test</button>
// <button disabled id="btnRmvTest" className="btn btn-secondary" onClick="RemoveTest();">Remove Test</button>

var domContainer = document.querySelector('#config-parent-view');
ReactDOM.render(React.createElement(ConfigParentView, null), domContainer);