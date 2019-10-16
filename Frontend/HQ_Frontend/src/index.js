import ConfigParentView from "./ConfigParentView.jsx";
import MetadataReview from "./MetadataReview.jsx";


window.loadTestConfigComponents = function(){
  let domContainer = document.querySelector('#config-parent-view');
  ReactDOM.render(<ConfigParentView />, domContainer);
};

window.loadMetadataReviewPage = function(){
  let domContainer = document.querySelector('#metadata-review');
  ReactDOM.render(<MetadataReview/>, domContainer);
}

//define some global unility functions
window.isDefined = function(obj){
  if(typeof obj === 'undefined'){
    return false;
  }
  return true;
}

window.uuidv4 = function() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}
