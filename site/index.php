<!DOCTYPE html>
<html>
  <head>
    <title>Wildlife Monitor</title>
    <link rel="stylesheet" type="text/css" href="main.css">
  </head>
  <body>
    <?php
      include 'menu.php';
    ?>
    <div id="main">
      
      <h1>Wildlife Monitor Homepage</h1>
      <h2>Recent Activity</h2>
      
      <p>The entries at the top are the most recent. To see the time a video was recorded, see the metadata file.</p>
      
      <table>
        <tr>
          <th>Number</th>
          <th>Video</th> 
          <th>Metadata</th>
        </tr>
      
        <?php
        
          // echo '<pre><a href="' . $path . $item . '">' . $item . '</a></pre>' . "\n";
          // echo pathinfo($item, PATHINFO_EXTENSION);

          $path = 'data/';
          $files = scandir($path);
          $files = array_diff($files, array('.', '..'));
          
          $mp4files = array();
          $jsonfiles = array();
          
          foreach($files as $item) {
            
            $ext = pathinfo($item, PATHINFO_EXTENSION);
            
            if ($ext == "mp4") {
              array_push($mp4files, $item);
            } else {
              array_push($jsonfiles, $item);
            }
                      
          }
          
          if (count($jsonfiles) > count($mp4files)) {
                      
            $diff = count($jsonfiles) - count($mp4files);
            
            for ($x = 0; $x < $diff; $x++) {
                array_push($mp4files, "File currently unavailable");
            }
            
          }
          
          $mp4files = array_reverse($mp4files);
          $jsonfiles = array_reverse($jsonfiles);
                    
          for ($x = 0; $x < count($jsonfiles); $x++) {
            echo '<tr>';
            
            echo '<td>' . strval($x + 1) . '</td>';
            
            if ($mp4files[$x] == "File currently unavailable") {
              echo '<td>' . '<pre>' . $mp4files[$x] . '</pre>' . '</td>';
            } else {
              echo '<td>' . '<pre>' . '<a href="' . $path . $mp4files[$x] . '">' . $mp4files[$x] . '</a>' . '</pre>' . '</td>';
            }
            
            echo '<td>' . '<pre>' . '<a href="' . $path . $jsonfiles[$x] . '">' . $jsonfiles[$x] . '</a>' . '</pre>' . '</td>';
                      
            echo '</tr>';
          }
          
        ?>
      
      </table>

    </div>
  </body>
</html>
