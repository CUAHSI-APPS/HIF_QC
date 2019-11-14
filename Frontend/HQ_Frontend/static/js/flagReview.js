FRConst = {
  NEXT: 'next',
  PREVIOUS: 'previous'
}

//uncertian if we should only show tested cols or not
//fetch next column in a safe way
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

//organizational function
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


// View manipulation ------------------------------------------

//bind new subpage query go to next
$('#right').on('click', function(){
    //get index of next column to show in safe way
    col = manageViewCol(FRConst.NEXT, parseInt(sessionStorage.getItem('currentCol')));

    //construct the endpoint of our next column
    //and reload page
    let endpoint = `/view/flagReview/${sessionStorage.sessionId}?colName=${encodeURIComponent(JSON.parse(sessionStorage.dataCols)[col])}&indexCol=${encodeURIComponent(sessionStorage.indexCol)}`
    $('#StepPlaceholder').load(endpoint);

    //update our current column in persistent memory
    sessionStorage.setItem('currentCol', col);
})


//bind new subpage to go back to previous
$('#left').on('click', function(){
    col = manageViewCol(FRConst.PREVIOUS, parseInt(sessionStorage.getItem('currentCol')));
    let endpoint = `/view/flagReview/${sessionStorage.sessionId}?colName=${encodeURIComponent(JSON.parse(sessionStorage.dataCols)[col])}&indexCol=${encodeURIComponent(sessionStorage.indexCol)}`
    $('#StepPlaceholder').load(endpoint);

    sessionStorage.setItem('currentCol', col);
})
