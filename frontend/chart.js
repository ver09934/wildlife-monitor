if (typeof currentLogPath === 'undefined') {
    console.log("chart.js didn't get a currentLogPath variable...");
    throw new Error();
}

var xhttp = new XMLHttpRequest();
xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {

        google.charts.load('current', {packages: ['corechart', 'line']});
        google.charts.setOnLoadCallback(
            function() {
                drawLineColors(xhttp);
            }
        );

    }
};
xhttp.open("GET", currentLogPath, true);
xhttp.send();

function drawLineColors(xml) {
    
    var tempData = new google.visualization.DataTable();
    var presData = new google.visualization.DataTable();
    
    tempData.addColumn('datetime','x');
    tempData.addColumn('number','Temperature');
    
    presData.addColumn('datetime','x');
    presData.addColumn('number','Pressure');

    var xmlDoc = xml.responseXML;
    var rows = xmlDoc.getElementsByTagName("row");

    for (let i = 0; i < rows.length; i++) {
        tempData.addRow([new Date(rows[i].getElementsByTagName("time")[0].childNodes[0].nodeValue), Number(rows[i].getElementsByTagName("temperature")[0].childNodes[0].nodeValue)]);
        presData.addRow([new Date(rows[i].getElementsByTagName("time")[0].childNodes[0].nodeValue), Number(rows[i].getElementsByTagName("pressure")[0].childNodes[0].nodeValue)]);
    }

    var tempOptions = {
        title: 'Temperature over Time',
        legend: 'none',
        hAxis: {
            // format: 'M/d/yy hh:mm:ss',
            title: 'Time'
        },
        vAxis: {
            title: 'Temperature (\xB0C)'
        },
        colors: ['#e52920']
    };
    
    var presOptions = {
        title: 'Pressure over Time',
        legend: 'none',
        hAxis: {
            // format: 'M/d/yy hh:mm:ss',
            title: 'Time'
        },
        vAxis: {
            title: 'Pressure (Pa)'
        },
        colors: ['#4286f4']
    };

    var tempChart = new google.visualization.LineChart(document.getElementById('temp-chart'));
    var presChart = new google.visualization.LineChart(document.getElementById('pres-chart'));
    
    tempChart.draw(tempData, tempOptions);
    presChart.draw(presData, presOptions);
}
