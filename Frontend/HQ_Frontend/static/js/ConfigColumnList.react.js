'use strict';

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var ConfigColumnList = function (_React$Component) {
  _inherits(ConfigColumnList, _React$Component);

  function ConfigColumnList(props) {
    _classCallCheck(this, ConfigColumnList);

    var _this = _possibleConstructorReturn(this, (ConfigColumnList.__proto__ || Object.getPrototypeOf(ConfigColumnList)).call(this, props));

    _this.state = {};
    _this.colNames = props.dataColumns;

    _this.handleSelection = _this.handleSelection.bind(_this);
    return _this;
  }

  //propogates selection back to parent scope


  _createClass(ConfigColumnList, [{
    key: "handleSelection",
    value: function handleSelection(event) {
      this.props.updateSelCol(event.target.value);
    }
  }, {
    key: "render",
    value: function render() {

      var dataColsList = this.colNames.map(function (col, i) {
        return React.createElement(
          "option",
          { key: i },
          col
        );
      });

      return React.createElement(
        "div",
        { className: "card-body" },
        React.createElement(
          "h6",
          null,
          "Data Fields"
        ),
        React.createElement(
          "select",
          { multiple: true, className: "form-control selectBox", onChange: this.handleSelection },
          dataColsList
        )
      );
    }
  }]);

  return ConfigColumnList;
}(React.Component);

export default ConfigColumnList;
//
// let domContainer = document.querySelector('#config-column-list');
// ReactDOM.render(<ConfigColumnList />, domContainer);