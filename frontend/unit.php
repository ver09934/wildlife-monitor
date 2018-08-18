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

  // Video / Video Metadata filename info
  $typeAndDateSeparator = '_';
  $extSeparator = '.';
  $vidName = 'video';
  $dataName = 'data';
  $vidExtension = 'mp4';
  $dataExtension = 'xml';

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
    <link rel="icon" href="/favicon.png">
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
        echo '<h1 class="title">' . $prettyName . '</h1>';
      ?>

      <div id="unit-page">

        <h2 class="subtitle">Minutely Image</h2>

        <?php
          echo '<img src="' . $currentImagePath . '" alt="' . $currentImageAlt . '">';
        ?>
        
        <h2 class="subtitle">Sensor Data</h2>
              
        <div id="temp-chart" class="data-graph"></div>
        <div id="pres-chart" class="data-graph"></div>

        <h2 class="subtitle">Captured Videos</h2>
        
        <table id="data-table">
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
            
            $union = array();
            
            foreach($files as $file) {
              
              $ext = pathinfo($file, PATHINFO_EXTENSION);
              $name = pathinfo($file, PATHINFO_FILENAME);

              if ($ext == $vidExtension || $ext == $dataExtension) {
                $date = substr($name, strpos($name, $typeAndDateSeparator) + 1);
                if (!in_array($date, $union)) {
                  array_push($union, $date);
                }
              }           
            }

            // Newest at top
            $union = array_reverse($union);

            // iterate over all files - create 1 table row per loop
            for ($i = 0; $i < count($union); $i++) {

              $videoFile = $vidName . $typeAndDateSeparator . $union[$i] . $extSeparator . $vidExtension;
              $dataFile = $dataName . $typeAndDateSeparator . $union[$i] . $extSeparator . $dataExtension;

              echo '<tr>';
              
              // --- Column 1 - Number ---
              echo '<td>' . strval(count($union) - $i) . '</td>';
              
              // --- Column 2 - Video ---
              if (file_exists($videoDirPath . $videoFile)) {
                echo '<td><pre><a href="' . $videoDirPath . $videoFile . '">' . $videoFile . '</a></pre></td>'; // link to video
                // echo '<td><video width="320" height="240" controls><source src="' . $videoDirPath . $mp4Files[$i] . '" type="video/mp4"></video></td>'; // embed video 
              }
              else {
                echo '<td><pre>' . $vidNotFound . '</pre></td>';
              }
              
              // --- Rest of Columns - XML data ---
              if (file_exists($videoDirPath . $dataFile)) {

                  $dataXml = simplexml_load_file($videoDirPath . $dataFile);

                  for ($j = 0; $j < count($dataFields); $j++) {

                    $dataField = $dataFields[$j];
                    $dataUnit = $dataUnits[$j];
                    
                    if ($dataXml->row[0]->$dataField != "") {
                      echo '<td><pre>' . $dataXml->row[0]->$dataField . $dataUnit . '</pre></td>';
                    }
                    else {
                      echo '<td><pre>' . $dataNotFound . '</pre></td>';
                    }
                    
                  }

              }
              else {
                for ($k = 0; $k < count($dataFields); $k++) {
                  echo '<td><pre>' . $dataNotFound . '</pre></td>';
                }
              }
              
              echo '</tr>';
            }
            
          ?>
        
        </table>

      </div>
    </div>
  </body>
</html>
