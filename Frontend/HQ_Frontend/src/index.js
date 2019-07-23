//define some global unility functions
window.isDefined = function(obj){
  if(typeof obj === 'undefined'){
    return false;
  }
  return true;
}

import ConfigParentView from "./ConfigParentView.jsx";



window.loadTestConfigComponents = function(){
  let domContainer = document.querySelector('#config-parent-view');
  ReactDOM.render(<ConfigParentView />, domContainer);
};
