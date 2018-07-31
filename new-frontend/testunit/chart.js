var xhttp = new XMLHttpRequest();
xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
        readData(xhttp);
    }
};
xhttp.open("GET","data/datalogs/current_log-2018-07-31.xml", true);
xhttp.send();

function readData(xml) {
    var xmlDoc = xml.responseXML;
    google.charts.load('current', {packages: ['corechart', 'line']});
    google.charts.setOnLoadCallback(function() {drawLineColors(xml);});
}

function drawLineColors(xml) {
    
    var tempData = new google.visualization.DataTable();
    var presData = new google.visualization.DataTable();
    tempData.addColumn('number','x');
    tempData.addColumn('number','Temperature');
    presData.addColumn('number','x');
    presData.addColumn('number','Pressure');

    var xmlDoc = xml.responseXML;
    var rows = xmlDoc.getElementsByTagName("row");

    for(let i = 0; i < rows.length; i++) {
        tempData.addRow([i, Number(rows[i].getElementsByTagName("temperature")[0].childNodes[0].nodeValue)]);
        presData.addRow([i, Number(rows[i].getElementsByTagName("pressure")[0].childNodes[0].nodeValue)]);
    }

    var tempOptions = {
        'title':'Temperature over Time',
        legend: 'none',
        hAxis: {
            title: 'Time'
        },
        vAxis: {
            title: 'Temperature (\xB0C)'
        },
        colors: ['#a52714']
    };
    
    var presOptions = {
        'title':'Pressure over Time',
        legend: 'none',
        hAxis: {
            title: 'Time'
        },
        vAxis: {
            title: 'Pressure (Pa)'
        },
        colors: ['#097138']
    };

    var tempChart = new google.visualization.LineChart(document.getElementById('temp_chart'));
    var presChart = new google.visualization.LineChart(document.getElementById('pres_chart'));
    
    tempChart.draw(tempData, tempOptions);
    presChart.draw(presData, presOptions);
}


