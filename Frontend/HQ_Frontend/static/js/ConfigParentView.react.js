import ConfigColumnList from './ConfigColumnList.react.js';

'use strict';

class ConfigParentView extends React.Component {
    constructor(props) {
        super(props);
        this.state = {};
        this.colNames = JSON.parse(sessionStorage.getItem('dataCols'));

        this.handleSelection = this.handleSelection.bind(this);
    }

    emptyFun() {}

    handleSelection(event) {}

    render() {

        return React.createElement(
            'div',
            { className: 'card' },
            React.createElement(
                'div',
                { className: 'row' },
                React.createElement(
                    'div',
                    { className: 'col-sm-3' },
                    React.createElement(ConfigColumnList, { dataColumns: this.colNames })
                ),
                React.createElement(
                    'div',
                    { className: 'col-sm-3' },
                    React.createElement(
                        'div',
                        { className: 'card-body' },
                        React.createElement(
                            'h6',
                            null,
                            'Data Field Metadata'
                        ),
                        React.createElement('textarea', { type: 'text', rows: '6', id: 'tbMeta', className: 'form-control selectBox' }),
                        React.createElement(
                            'div',
                            { className: 'text-center pt-3' },
                            React.createElement(
                                'button',
                                { disabled: true, id: 'btnMeta', onClick: this.emptyFun, className: 'btn btn-secondary' },
                                'Modify Metadata'
                            )
                        )
                    )
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
}

// <button disabled id="btnMeta" onClick="$('#modalMeta').modal('show');" className="btn btn-secondary">Modify Metadata</button>

// <button disabled id="btnAddTest" className="btn btn-secondary" onClick="$('#modalTest').modal('show');">Add Test</button>
// <button disabled id="btnModTest" className="btn btn-secondary" onClick="$('#modalTest').modal('show');">Modify Test</button>
// <button disabled id="btnRmvTest" className="btn btn-secondary" onClick="RemoveTest();">Remove Test</button>

let domContainer = document.querySelector('#config-parent-view');
ReactDOM.render(React.createElement(ConfigParentView, null), domContainer);
