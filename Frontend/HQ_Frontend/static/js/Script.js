var lower = 0;
var upper = 0;



function manageSuccessfulUpload(file, response){
  sessionStorage.setItem('sessionId', response['token']);
  dropPreview();
}

function getPreviewDataUrl(numRows){
    var dropPreviewBaseUrl = '/api/dropPreview/'
    // Format url for retrieval of information
    var rows = numRows.toString();

    var url = dropPreviewBaseUrl+rows+'?';
    url += 'sessionId=' + sessionStorage.getItem('sessionId');

    return url
}

function dropPreview() {
    var url = ''
  // Unhide table
  //  $("#UploadFileTable").removeAttr("hidden");
    $("#nextTaskStep1").prop("disabled", false);

    // Format url for retrieval of information
    url = getPreviewDataUrl(2);

    //$("#UploadFileTable").load(url);
    $("#loadingModal").modal("hide");
}

function setStep2() {
    console.log("Check for proper persistence:", sessionStorage.getItem('sessionId'))
    url = getPreviewDataUrl(100);

    $("#tablePlaceholder").load(url);
    $("#SelectPlaceholder").load('/api/dropPreviewColumnNames?sessionId='+sessionStorage.getItem('sessionId'));
}

function setDateTimeBox() {
    var $dateTimeBox = $('#dateTimeBox1');
    var $dataBox = $('#dataBox1');

    $dateTimeBox.empty();
    $dateTimeBox.append($dataBox.children().clone());
    $('#nextTaskStep2').prop('disabled', true);
}

function setDataBox2() {
    var $dataBox2 = $('#dataBox2');
    var $dataBox1 = $('#dataBox1');
    var selectedItems = $dataBox1.val() || [];

    for (var i = 0; i < selectedItems.length; i++) {
        var item = "<option value=\"" + selectedItems[i] + "\">" + selectedItems[i] + "</option>";
        $dataBox2.append(item);
        $dataBox1.find('[value="' + selectedItems[i] + '"]').remove();
    }
    setDateTimeBox();
}

function setDataBox1() {
    var $dataBox2 = $('#dataBox2');
    var $dataBox1 = $('#dataBox1');
    var selectedItems = $dataBox2.val() || [];

    for (var i = 0; i < selectedItems.length; i++) {
        var item = "<option value=\"" + selectedItems[i] + "\">" + selectedItems[i] + "</option>";
        $dataBox1.append(item);
        $dataBox2.find('[value="' + selectedItems[i] + '"]').remove();
    }
    setDateTimeBox();
}

// enables us to go on to step 3
function Step3() {
    $('#nextTaskStep2').prop('disabled', false);
}

function manageDataForStep(step){
  switch(step){
    case 3:
      stepThreeCleanup();
      break;
  }
}

function stepThreeCleanup(){
    var dataColumns = [];

    $('#dataBox2').find('option').each(function(i){
      dataColumns.push($(this).attr('value'));
    })

    var dateTimeCol = $('#dateTimeBox1').children("option:selected").val();

    sessionStorage.setItem('indexCol', dateTimeCol);
    sessionStorage.setItem('dataCols', JSON.stringify(dataColumns));

    //upload selected data cols for stats analysis
}


function queryStatus() {
    let endpoint = "http://localhost:8085/test/result/"
    endpoint = endpoint + sessionStorage.getItem("sessionId");

    setTimeout(function () {
      fetch(endpoint)
      .then((response) => response.json())
      .then(function(data){
        if(data == 'None'){
          queryStatus();
        }
        else{
          window.csv = data['csv'];
          $('#headerTest').text("Test Complete!");
          $('#nextTask').prop('disabled', false);

        }
      })
    }, 1000);

}

function downloadCSV(){
  let endpoint = "http://localhost:8085/test/result/"
  endpoint = endpoint + sessionStorage.getItem("sessionId");

  fetch(endpoint)
  .then((response) => response.json())
  .then( (d) => {
      var encodedUri = 'data:text/csv;charset=utf-8,' + encodeURI(d['csv']);
      var link = document.createElement("a");
        link.target = '_blank';
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", "flags.csv");
        document.body.appendChild(link); // Required for FF

      link.click();
  });
}

function RunTest() {
    let endpoint = "http://localhost:8085/test/run/"
    endpoint = endpoint + sessionStorage.getItem("sessionId");

    fetch(endpoint)
    .then((response) => {
        $('#headerTest').text("Test Running...");
        queryStatus();
      })
    .catch((error)=>{
      console.log(error)
    })
}
