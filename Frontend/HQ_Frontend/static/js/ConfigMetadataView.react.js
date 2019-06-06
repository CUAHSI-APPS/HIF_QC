'use strict';

//import '../css/ConfigMetadataView.react.css'

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var ConfigMetadataView = function (_React$Component) {
  _inherits(ConfigMetadataView, _React$Component);

  function ConfigMetadataView(props) {
    _classCallCheck(this, ConfigMetadataView);

    var _this = _possibleConstructorReturn(this, (ConfigMetadataView.__proto__ || Object.getPrototypeOf(ConfigMetadataView)).call(this, props));

    _this.state = {};
    return _this;
  }

  _createClass(ConfigMetadataView, [{
    key: 'render',
    value: function render() {
      var _this2 = this;

      return React.createElement(
        'div',
        { className: 'card-body' },
        React.createElement(
          'h6',
          null,
          'Data Field Metadata'
        ),
        React.createElement(
          'div',
          { className: 'md-display' },
          React.createElement(
            'ul',
            null,
            React.createElement(
              'li',
              null,
              'Name: ',
              React.createElement(
                'span',
                null,
                this.props.selectedCol
              )
            ),
            Object.keys(this.props.metaData).map(function (key, index) {
              return React.createElement(
                'li',
                null,
                key,
                ' : ',
                React.createElement(
                  'span',
                  null,
                  ' ',
                  _this2.props.metaData[key],
                  ' '
                ),
                ' '
              );
            })
          )
        ),
        React.createElement(
          'div',
          { className: 'text-center pt-3' },
          React.createElement(
            'button',
            { disabled: true, id: 'btnMeta', onClick: this.emptyFun, className: 'btn btn-secondary' },
            'Modify Metadata'
          )
        )
      );
    }
  }]);

  return ConfigMetadataView;
}(React.Component);

ConfigMetadataView.defaultProps = {
  metaData: {
    'key': []
  }
};


export default ConfigMetadataView;
//
// let domContainer = document.querySelector('#config-column-list');
// ReactDOM.render(<ConfigColumnList />, domContainer);