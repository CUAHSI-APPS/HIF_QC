var lower = 0;
var upper = 0;

function dropPreview() {
    $("#UploadFileTable").removeAttr("hidden");
    $("#nextTaskStep1").prop("disabled", false);
    $("#UploadFileTable").load('/api/dropPreview/2');
    $("#loadingModal").modal("hide");
}

function setStep2() {
    $("#tablePlaceholder").load('/api/dropPreview/100');
    $("#SelectPlaceholder").load('/api/dropPreviewColumnNames');
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

function Step3() {
    $('#nextTaskStep2').prop('disabled', false);
}

function SetMeta(name, item1, item2) {
    $('#btnMeta').prop('disabled', false);
    $('#btnAddTest').prop('disabled', false);
    $('#metaTitle').text(name);
    lower = item1;
    upper = item2;
    $('#tbMeta1').val(item1);
    $('#tbMeta2').val(item2);
    var item = "Name : " + name + "\nTempLower : " + item1 + "\nTempUpper : " + item2;
    var $meta = $("#tbMeta");
    $meta.val(item);
    setTest();
    $.get('/api/save/' + lower + '/' + upper);
    $('#modalMeta').modal('hide');
}

function AddTest() {
    var $test = $('#selectTest');
    var num = $test.children().length;
    num++;
    var item = "<option value=\"Test_" + num + "\">Test_" + num + "</option>";
    $test.append(item);
    setValues();
    $('#modalTest').modal('hide');
    $('#btnModTest').prop('disabled', false);
    $('#btnRmvTest').prop('disabled', false);
    $('#nextTaskStep3').prop('disabled', false);
}

function RemoveTest() {
    var $test = $('#selectTest');
    var selectedItems = $test.val() || [];

    for (var i = 0; i < selectedItems.length; i++) {
        $test.find('[value="' + selectedItems[i] + '"]').remove();
    }

    if ($test.children().length === 0) {
        $('#btnModTest').prop('disabled', true);
        $('#btnRmvTest').prop('disabled', true);
        $('#nextTaskStep3').prop('disabled', true);
    }
}

function RunTest() {
    $('#headerTest').text("Test Running...");
    var $progress = $("#progressTest");
    setTimeout(function () {
        $progress.addClass("w-25");
        $progress.attr("aria-valuenow", "25");
        setTimeout(function () {
            $progress.addClass("w-50");
            $progress.attr("aria-valuenow", "50");
            setTimeout(function () {
                $progress.addClass("w-75");
                $progress.attr("aria-valuenow", "75");
                setTimeout(function () {
                    NextProgressBar(5);
                }, 1000);
            }, 1000);
        }, 1000);
    }, 1000);
}

function SetReviewMeta() {
    var item = "TempLower : " + lower + "\nTempUpper : " + upper;
    var $meta = $("#taMetaReview");
    $meta.val(item);
}

function getLower() {
    return lower;
}

function getUpper() {
    return upper;
}

function setTest() {
    $('#lowerTB').val(getLower());
    $('#upperTB').val(getUpper());
}

function setValues() {
    lower = $('#lowerTB').val();
    upper = $('#upperTB').val();
}

function SetGraph() {
    var request = new XMLHttpRequest();
    var URL = "/api/process_csv/" + getLower() + "/" + getUpper();
    request.open("GET", URL);
    request.responseType = "json";
    request.send();
    request.onload = function () {
        var dataPoints = request.response;
        var labelArray = dataPoints["Time Stamp ((UTC-08:00) Pacific Time (US & Canada))"];
        var tempArray = dataPoints["Temperature"];
        var humArray = dataPoints["Humidity"];
        var length = 0;
        for (x in labelArray) {
            length++;
        }
        var labels = new Array(length);
        var temp = new Array(length);
        var hum = new Array(length);
        var i = 0;
        for (x in labelArray) {
            labels[i] = labelArray[x];
            i++;
        }
        i = 0;
        for (x in tempArray) {
            temp[i] = tempArray[x];
            i++;
        }
        i = 0;
        for (x in humArray) {
            hum[i] = humArray[x];
            i++;
        }
        var ctx = document.getElementById("testGraph").getContext('2d');
        var myChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: "Humidity",
                    data: hum,
                    fill: true,
                    borderColor: 'rgba(0,255,0,.5)',
                    backgroundColor: 'rgba(0,255,0,.5)',
                    lineTension: 0.1
                },
                {
                    label: "Temperature",
                    data: temp,
                    fill: true,
                    borderColor: 'rgba(255,0,0,.5)',
                    backgroundColor: 'rgba(255,0,0,.5)',
                    lineTension: 0.1
                }
                ]
            },
            options: {
                responsive: true,
                scales:
                {
                    yAxes: [{
                        ticks: {
                            beginAtZero: true
                        }
                    }]
                }
            }
        });
    }
}

function SetTestGraph() {
    var request = new XMLHttpRequest();
    var URL = "/api/process_csv/0/100";
    request.open("GET", URL);
    request.responseType = "json";
    request.send();
    request.onload = function () {
        var dataPoints = request.response;
        var labelArray = dataPoints["Time Stamp ((UTC-08:00) Pacific Time (US & Canada))"];
        var tempArray = dataPoints["Temperature"];
        var humArray = dataPoints["Humidity"];
        var length = 0;
        for (x in labelArray) {
            length++;
        }
        var labels = new Array(length);
        var temp = new Array(length);
        var hum = new Array(length);
        var i = 0;
        for (x in labelArray) {
            labels[i] = labelArray[x];
            i++;
        }
        i = 0;
        for (x in tempArray) {
            temp[i] = tempArray[x];
            i++;
        }
        i = 0;
        for (x in humArray) {
            hum[i] = humArray[x];
            i++;
        }
        var ctx = document.getElementById("testGraph").getContext('2d');
        var myChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: "Humidity",
                    data: hum,
                    fill: true,
                    borderColor: 'rgba(0,255,0,.5)',
                    backgroundColor: 'rgba(0,255,0,.5)',
                    lineTension: 0.1
                },
                {
                    label: "Temperature",
                    data: temp,
                    fill: true,
                    borderColor: 'rgba(255,0,0,.5)',
                    backgroundColor: 'rgba(255,0,0,.5)',
                    lineTension: 0.1
                }
                ]
            },
            options: {
                responsive: true,
                scales:
                {
                    yAxes: [{
                        ticks: {
                            beginAtZero: true
                        }
                    }]
                }
            }
        });
    }
}