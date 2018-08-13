<?php

  // File paths and names
  $unit = $_GET["pidata"] . '/';

  $dataDir = 'data/';

  $logDir = 'datalogs/';
  $videoDir = 'videos/';
  $infoFile = 'info.xml';
  $currentImage = 'preview-img.jpg';

  $logDirPath = $dataDir . $unit . $logDir;
  $videoDirPath = $dataDir . $unit . $videoDir;
  $infoFilePath = $dataDir . $unit . $infoFile;
  $currentImagePath = $dataDir . $unit . $currentImage;

  // Info XML fields
  $prettyNameField = 'prettyname';

  // Video data XML fields
  $dataFields = array('time', 'temperature', 'pressure', 'length');
  $dataUnits = array('', ' &deg;C', ' Pa', '');

  // Other displayed items
  $currentImageAlt = 'current-image';
  $vidNotFound = "Video unavailable";
  $dataNotFound = "Data unavailable";

?>
<!DOCTYPE html>
<html>
  <head>
    <title>Test Unit</title>
    <link rel="stylesheet" type="text/css" href="main.css">
    <script type="text/javascript">
    <?php

      $logFiles = scandir($logDirPath);
      $logFiles = array_diff($logFiles, array('.', '..'));
      $logFiles = array_values($logFiles); // rescale indices

      $currentLogPath = $logFiles[count($logFiles) - 1];

      echo 'var currentLogPath = "' . $logDirPath . $currentLogPath . '";';
    ?>
    </script>
    <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
    <script type="text/javascript" src="chart.js"></script>
  </head>
  <body>
    <?php
      include 'menu.php';
    ?>
    <div id="main">
      
      <?php
        $infoXml = simplexml_load_file($infoFilePath);
        $prettyName = $infoXml->$prettyNameField;
        echo '<h1>' . $prettyName . '</h1>';
      ?>

      <h2>Current Image</h2>

      <?php
        echo '<img src="' . $currentImagePath . '" alt="' . $currentImageAlt . '">';
      ?>
      
      <h2>Data Graphs</h2>
      
      <h3>Temperature/Barometric Pressure</h3>
      
      <div id="temp-chart" class="data-graph"></div>
      <div id="pres-chart" class="data-graph"></div>

      <h2>Captured Videos</h2>
      
      <table>
        <tr>
          <th>Number</th>
          <th>Video</th> 
          <th>Time</th>
          <th>Temperature</th>
          <th>Pressure</th>
          <th>Length</th>
          <!-- <th>Metadata File</th> -->
        </tr>
      
        <?php
                 
          $files = scandir($videoDirPath);
          $files = array_diff($files, array('.', '..'));
          $files = array_values($files); // rescale indices to 0
          
          $mp4Files = array();
          $xmlFiles = array();
          
          foreach($files as $file) {
            
            $ext = pathinfo($file, PATHINFO_EXTENSION);
            
            if ($ext == "mp4") {
              array_push($mp4Files, $file);
            }
            elseif ($ext == "xml") {
              array_push($xmlFiles, $file);
            }
                      
          }
          
          if (count($xmlFiles) > count($mp4Files)) {
                      
            $diff = count($xmlFiles) - count($mp4Files);
            
            for ($x = 0; $x < $diff; $x++) {
                array_push($mp4Files, $vidNotFound);
            }
            
          }
          else if (count($mp4Files) > count($xmlFiles)) {

            $diff = count($mp4Files) - count($xmlFiles);
            
            for ($x = 0; $x < $diff; $x++) {
                array_push($xmlFiles, $dataNotFound);
            }

          }
          
          // $mp4Files and $xmlFiles are now of equal length

          $mp4Files = array_reverse($mp4Files);
          $xmlFiles = array_reverse($xmlFiles);
          
          // iterate over all files (arbitrarily use count($xmlFiles) instead of count($mp4Files)) - create 1 table row
          for ($i = 0; $i < count($xmlFiles); $i++) {
            echo '<tr>';
            
            // --- Column 1 - Number ---
            echo '<td>' . strval(count($xmlFiles) - $i) . '</td>';
            
            // --- Column 2 - Video ---
            if ($mp4Files[$i] != $vidNotFound) {
              
              echo '<td>' . '<pre>' . '<a href="' . $videoDirPath . $mp4Files[$i] . '">' . $mp4Files[$i] . '</a>' . '</pre>' . '</td>'; // link to video
              // echo '<td>' . '<video width="320" height="240" controls>' . '<source src="' . $videoDirPath . $mp4Files[$i] . '" type="video/mp4">' . '</video>' . '</td>'; // embed video 
            }
            else {
              echo '<td>' . '<pre>' . $vidNotFound . '</pre>' . '</td>';
            }
            
            // --- Rest of Columns - XML data ---
            if ($xmlFiles[$i] != $dataNotFound) {

                $dataXml = simplexml_load_file($videoDirPath . $xmlFiles[$i]);

                for ($j = 0; $j < count($dataFields); $j++) {

                  $dataField = $dataFields[$j];
                  $dataUnit = $dataUnits[$j];
                  
                  if ($dataXml->row[0]->$dataField != "") {
                    echo '<td>' . '<pre>' . $dataXml->row[0]->$dataField . $dataUnit . '</pre>' . '</td>';
                  }
                  else {
                    echo '<td>' . '<pre>' . $dataNotFound . '</pre>' . '</td>';
                  }
                  
                }

            }
            else {
              for ($k = 0; $k < count($dataFields); $k++) {
                echo '<td>' . '<pre>' . $dataNotFound . '</pre>' . '</td>';
              }
            }
                                           
            echo '</tr>';
          }
          
        ?>
      
      </table>

    </div>
  </body>
</html>
