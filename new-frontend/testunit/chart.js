var xhttp = new XMLHttpRequest();
xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
        readData(xhttp);
    }
};
xhttp.open("GET","data/current_log.xml", true);
xhttp.send();

function drawLineColors(xml) {
    
    var data = new google.visualization.DataTable();
    data.addColumn('number','x');
    data.addColumn('number','Temperature');
    data.addColumn('number','Pressure');

    var xmlDoc = xml.responseXML;
    var rows = xmlDoc.getElementsByTagName("row");

    for(let i = 0; i < rows.length; i++) {
        data.addRow([i,
            Number(rows[i].getElementsByTagName("temp")[0].childNodes[0].nodeValue),
            Number(rows[i].getElementsByTagName("pres")[0].childNodes[0].nodeValue)]);
    }

    //var line = file.readln().split(";");
    //data.addRow([count++,line[1],line[2]]);

    var option = {
        hAxis: {
            title: 'Time (Needs to show actual time...)'
        },
        vAxis: {
            title: 'Temperature / Pressure'
        },
        colors: ['#a52714', '#097138']
    };

    var chart = new google.visualization.LineChart(document.getElementById('baro_chart'));
    chart.draw(data,option);
}

function readData(xml) {
    var xmlDoc = xml.responseXML;
    google.charts.load('current', {packages: ['corechart', 'line']});
    google.charts.setOnLoadCallback(function() {drawLineColors(xml);});
}
