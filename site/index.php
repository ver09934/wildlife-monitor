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
      
      <table>
        <tr>
          <th>Time</th>
          <th>Video</th> 
          <th>Temperature</th>
        </tr>
        <tr>
          <td>content1</td>
          <td>content2</td> 
          <td>content3</td>
        </tr>
        <tr>
          <td>content4</td>
          <td>content5</td> 
          <td>content6</td>
        </tr>
      </table>
      
      <h2>Debug</h2>
      <p>This is placeholder text.</p>
      
      <?php
      
        $path = '/home/pi/wildlife-files/';
        
        $files = array_diff(scandir($path), array('.', '..'));
        
        foreach($files as $item) {
          // echo $item['filename'];
          // echo $item['filepath'];
          echo '<pre><a href="' . $path . $item . '">' . $path . $item . '</a></pre>' . "\n";
          //echo '<pre>'; var_dump($item);
        }
        
      ?>

    </div>
  </body>
</html>
