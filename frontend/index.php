<?php

  // File paths and names
  $dataDir = 'data/';
  
  $logDir = 'datalogs/';
  $infoFileName = 'info.xml';

  // Info XML fields
  $prettyNameField = 'prettyname';

  // Datalog XML fields
  $timeField = 'time';

?>
<!DOCTYPE html>
<html>
  <head>
    <title>Wildlife Monitor</title>
    <link rel="stylesheet" type="text/css" href="main.css">
    <link rel="icon" href="/favicon.png">
  </head>
  <body>
    <?php
      include 'menu.php';
    ?>
    <div id="main">
      
      <h1 class="title">Wildlife Monitor Homepage</h1>

      <div id="homepage">
      
        <table id="unit-table">
          <tr>
            <th>Page</th>
            <th>Last Reported</th>
          </tr>
          
          <?php
            
            $unitDirPaths = glob($dataDir . '*' , GLOB_ONLYDIR);
            
            foreach ($unitDirPaths as $unitDirPath) {
                
                // NOTE: $unitDirPath does not have a '/' at the end...

                $unitDirName = basename($unitDirPath);

                echo '<tr>';

                if (file_exists($unitDirPath . '/' . $infoFileName)) {
                  $xml = simplexml_load_file($unitDirPath . '/' . $infoFileName);
                  $prettyName = $xml->$prettyNameField;
                  echo '<td><a href="unit.php?pidata=' . $unitDirName . '">' . $prettyName . '</a></td>';
                }
                else {
                  echo '<td><a href="unit.php?pidata=' . $unitDirName . '">' . $unitDirName . '</a></td>';
                }

                // echo '<td><a href="unit.php?pidata=' . $unitDirName . '">unit.php?pidata=' . $unitDirName . '</a></td>';

                $logDirpath = $unitDirPath . '/' . $logDir;

                $logFiles = scandir($logDirpath);
                $logFiles = array_diff($logFiles, array('.', '..'));
                $logFiles = array_values($logFiles); // rescale indices to 0

                if (count($logFiles) != 0) {

                  $currentLog = $logFiles[count($logFiles) - 1];
                  $xml = simplexml_load_file($logDirpath . $currentLog);

                  $elemCount = $xml->count();
                  echo '<td>' . $xml->row[$elemCount - 1]->$timeField . '</td>';

                }

                echo '</tr>';
            }
          ?>
        
        </table>

      </div>
    </div>
  </body>
</html>
