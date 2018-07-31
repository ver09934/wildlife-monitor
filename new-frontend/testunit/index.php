<!DOCTYPE html>
<html>
  <head>
    <title>Test Unit</title>
    <link rel="stylesheet" type="text/css" href="../main.css">
    <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
    <script type="text/javascript" src="chart.js"></script>
  </head>
  <body>
    <?php
      include '../menu.php';
    ?>
    <div id="main">
      
      <h1>Test Unit Page</h1>
      
      <h2>Data Graphs</h2>
      
      <h3>Temperature/Barometric Pressure</h3>
      
      <div id="temp_chart" style="width: 600px; height: 400px" class="datagraph"></div>
      <div id="pres_chart" style="width: 500px; height: 400px" class="datagraph"></div>
      
      <h2>Livestream</h2>
      
      <iframe width="560" height="315" src="https://www.youtube.com/embed/NpEaa2P7qZI" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>
      
      <h2>Recorded Videos</h2>
      
      <table>
        <tr>
          <th>Number</th>
          <th>Video</th> 
          <th>Time</th>
          <th>Temperature</th>
          <th>Pressure</th>
          <th>Metadata File</th>
        </tr>
      
        <?php

          $path = 'data/videos/';
          $files = scandir($path);
          $files = array_diff($files, array('.', '..'));
          
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
          
          if (count($xmlfiles) > count($mp4files)) {
                      
            $diff = count($xmlfiles) - count($mp4files);
            
            for ($x = 0; $x < $diff; $x++) {
                array_push($mp4files, "File currently unavailable");
            }
            
          }
          
          $mp4files = array_reverse($mp4files);
          $xmlfiles = array_reverse($xmlfiles);
                    
          for ($x = 0; $x < count($xmlfiles); $x++) {
            echo '<tr>';
            
            echo '<td>' . strval(count($xmlfiles) - $x) . '</td>';
            
            if ($mp4files[$x] == "File currently unavailable") {
              echo '<td>' . '<pre>' . $mp4files[$x] . '</pre>' . '</td>';
            }
            else {
              echo '<td>' . '<pre>' . '<a href="' . $path . $mp4files[$x] . '">' . $mp4files[$x] . '</a>' . '</pre>' . '</td>';
            }
            
            // Server needs php-xml to be installed
            if (file_exists($path . $xmlfiles[$x])) {
                $xml = simplexml_load_file($path . $xmlfiles[$x]);
                echo '<td>' . '<pre>' . $xml->row[0]->time . '</pre>' . '</td>';
                echo '<td>' . '<pre>' . $xml->row[0]->temperature . ' &deg;C' . '</pre>' . '</td>';
                echo '<td>' . '<pre>' . $xml->row[0]->pressure . ' Pa' . '</pre>' . '</td>';
                
            } else {
                echo '<td>' . '<pre>' . 'File not available' . '</pre>' . '</td>';
                echo '<td>' . '<pre>' . 'File not available' . '</pre>' . '</td>';
                echo '<td>' . '<pre>' . 'File not available' . '</pre>' . '</td>';
            }
                               
            echo '<td>' . '<pre>' . '<a href="' . $path . $xmlfiles[$x] . '">' . $xmlfiles[$x] . '</a>' . '</pre>' . '</td>';
            
            echo '</tr>';
          }
          
        ?>
      
      </table>

    </div>
  </body>
</html>
