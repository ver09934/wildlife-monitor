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
      <h2>Unit List</h2>
      
      <p>List of currently active units:</p>
      
      <table>
        <tr>
          <th>Name</th>
          <th>Page Link</th>
          <!-- --> <th>Last Reported</th> <!-- -->
        </tr>
        
        <?php
          $dirs = glob('data/*' , GLOB_ONLYDIR);
          
          foreach ($dirs as $dir) {
              $dirname = basename($dir);
              echo '<tr>';
              
              echo '<td>' . $dirname . '</td>';
              echo '<td>' . '<a href="unit.php?pidata=' . $dirname . '">unit.php?pidata=' . $dirname . '</a>' . '</td>';

              // echo '<td>' . '<a href="unit.php?pidata=' . $dirname . '">' . $dirname . '</a></td>';

              $logsubdir = $dir . '/datalogs/';
              $logfiles = scandir($logsubdir);
              $logfiles = array_diff($logfiles, array('.', '..'));
              $logfiles = array_values($logfiles); // rescale indices to 0

              if (count($logfiles) != 0) {
                $currentlog = $logfiles[count($logfiles) - 1];
                $xml = simplexml_load_file($logsubdir . $currentlog);

                $elemCount = $xml->count();
                echo '<td>' . $xml->row[$elemCount - 1]->time . '</td>';
                // echo '<td>' . $xml->count() . '</td>';
              }

              echo '</tr>';
          }
        ?>
      
      </table>

    </div>
  </body>
</html>
