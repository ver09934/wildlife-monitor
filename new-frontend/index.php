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
        </tr>
        
        <?php
          $dirs = glob($somePath . 'data/*' , GLOB_ONLYDIR);
          
          foreach ($dirs as $dir) {
              $dirname = basename($dir);
              echo '<tr>';
              echo '<td>' . $dirname . '</td>';
              echo '<td>' . '<a href="unit.php?pidata=' . $dirname . '">unit.php?pidata=' . $dirname . '</a>' . '</td>';
              echo '</tr>';
          }
          /*
          for ($x = 0; $x < count($dirs); $x++) {
              echo "The number is: $x <br>";
          }
          */
        ?>
      
      </table>

    </div>
  </body>
</html>
