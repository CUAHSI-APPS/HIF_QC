FRConst = {
  NEXT: 'next',
  PREVIOUS: 'previous'
}


//uncertian if we should only show tested cols or not
function getNextCol(currentCol){
  testedCols = JSON.parse(sessionStorage.getItem('testedCols'))
  if(currentCol === (testedCols.length - 1)){
    return currentCol;
  }

  return ++currentCol;

}

function getPrevCol(currentCol){
  testedCols = JSON.parse(sessionStorage.getItem('testedCols'))
  if(currentCol === 0){
    return currentCol;
  }

  return --currentCol;
}


function manageViewCol(signal, currentCol){
  switch(signal){
    case FRConst.NEXT:
      return getNextCol(currentCol);
      break;
    case FRConst.PREVIOUS:
      return getPrevCol(currentCol);
      break;
  }
}

//bind new subpage query
$('#right').on('click', function(){
    col = manageViewCol(FRConst.NEXT, parseInt(sessionStorage.getItem('currentCol')));

    console.log(col)

    let endpoint = `/view/flagReview/${sessionStorage.sessionId}?colName=${JSON.parse(sessionStorage.dataCols)[col]}`
    $('#StepPlaceholder').load(endpoint);
})


//bind new subpage query
$('#left').on('click', function(){
    col = manageViewCol(FRConst.PREVIOUS, parseInt(sessionStorage.getItem('currentCol')));

    console.log(col)

    let endpoint = `/view/flagReview/${sessionStorage.sessionId}?colName=${JSON.parse(sessionStorage.dataCols)[col]}`
    $('#StepPlaceholder').load(endpoint);
})
