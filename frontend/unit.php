<!DOCTYPE html>
<html>
  <head>
    <title>Test Unit</title>
    <link rel="stylesheet" type="text/css" href="main.css">
    <script type="text/javascript">
    <?php
      $datadir = 'data/';
      $unit = $_GET["pidata"] . '/';
      $videosubdir = 'videos/';
      $logsubdir = 'datalogs/';

      $videopath = $datadir . $unit . $videosubdir;
      $logpath = $datadir . $unit . $logsubdir;
      
      $logfiles = scandir($logpath);
      $logfiles = array_diff($logfiles, array('.', '..'));
      $logfiles = array_values($logfiles); // rescale indices

      // print_r($logfiles);

      $currentlogpath = $logfiles[count($logfiles) - 1];

      echo 'var currentlogpath = "' . $datadir . $unit . $logsubdir . $currentlogpath . '";';
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
      
      <h1>Test Unit Page</h1>
      
      <h2>Data Graphs</h2>
      
      <h3>Temperature/Barometric Pressure</h3>
      
      <div id="temp_chart" style="width: 650px; height: 450px" class="datagraph"></div>
      <div id="pres_chart" style="width: 650px; height: 450px" class="datagraph"></div>
      
      <h2>Livestream</h2>
      
      <?php
        $infoFile = 'info.xml';
        $idstr = 'channelid';
        $infoPath = $datadir . $unit . $infoFile;

        $infoxml = simplexml_load_file($infoPath);
        $channelID = $infoxml->$idstr;

        echo '<iframe width="560" height="315" src="https://www.youtube.com/embed/live_stream?channel=' . $channelID . '" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>';
      ?>
      
      <h2>Recorded Videos</h2>
      
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
                 
          $files = scandir($videopath);
          $files = array_diff($files, array('.', '..'));
          $files = array_values($files); // rescale indices to 0
          
          $mp4files = array();
          $xmlfiles = array();
          
          foreach($files as $item) {
            
            $ext = pathinfo($item, PATHINFO_EXTENSION);
            
            if ($ext == "mp4") {
              array_push($mp4files, $item);
            } elseif ($ext == "xml") {
              array_push($xmlfiles, $item);
            }
                      
          }

          $vidNotFound = "Video unavailable";
          $dataNotFound = "Data unavailable";
          
          if (count($xmlfiles) > count($mp4files)) {
                      
            $diff = count($xmlfiles) - count($mp4files);
            
            for ($x = 0; $x < $diff; $x++) {
                array_push($mp4files, $vidNotFound);
            }
            
          }
          else if (count($mp4files) > count($xmlfiles)) {

            $diff = count($mp4files) - count($xmlfiles);
            
            for ($x = 0; $x < $diff; $x++) {
                array_push($xmlfiles, $dataNotFound);
            }

          }
          
          // $mp4files and $xmlfiles are now of equal length

          $mp4files = array_reverse($mp4files);
          $xmlfiles = array_reverse($xmlfiles);
                    
          for ($i = 0; $i < count($xmlfiles); $i++) {
            echo '<tr>';
            
            echo '<td>' . strval(count($xmlfiles) - $i) . '</td>';
            
            if ($mp4files[$i] != $vidNotFound) {
              echo '<td>' . '<pre>' . '<a href="' . $videopath . $mp4files[$i] . '">' . $mp4files[$i] . '</a>' . '</pre>' . '</td>';
            }
            else {
              echo '<td>' . '<pre>' . $vidNotFound . '</pre>' . '</td>';
            }
            
            // if (file_exists($videopath . $xmlfiles[$x])) {

            if ($xmlfiles[$i] != $dataNotFound) {

                $xml = simplexml_load_file($videopath . $xmlfiles[$i]);

                $fields = array('time', 'temperature', 'pressure', 'length');
                $units = array('', ' &deg;C', ' Pa', '');

                for ($j = 0; $j < 4; $j++) {

                  $field = $fields[$j];
                  $unit = $units[$j];
                  
                  if ($xml->row[0]->$field != "") {
                    echo '<td>' . '<pre>' . $xml->row[0]->$field . $unit . '</pre>' . '</td>';
                  }
                  else {
                    echo '<td>' . '<pre>' . $dataNotFound . '</pre>' . '</td>';
                  }
                  
                }

            }
            else {
              for ($k = 0; $k < 4; $k++) {
                echo '<td>' . '<pre>' . $dataNotFound . '</pre>' . '</td>';
              } 
            }
                               
            // echo '<td>' . '<pre>' . '<a href="' . $videopath . $xmlfiles[$x] . '">' . $xmlfiles[$x] . '</a>' . '</pre>' . '</td>';
            
            echo '</tr>';
          }
          
        ?>
      
      </table>

    </div>
  </body>
</html>
