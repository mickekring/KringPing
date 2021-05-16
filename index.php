<!DOCTYPE html>
<html lang="sv">
<head>
  <title>Web Status</title>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.0/jquery.min.js"></script>
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
  <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
  <link rel="stylesheet" type="text/css" href="style.css">
  <link href="https://fonts.googleapis.com/css?family=Poppins:300,400,700,900&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.3.1/css/all.css" integrity="sha384-mzrmE5qonljUremFsqc01SB46JvROS7bZs3IO2EmfFsd15uHvIt+Y8vEf7N7fWAU" crossorigin="anonymous">
  
  <script>
  $(document).ready(function() {
      $(".divtime").load("time.php");
      var refreshId = setInterval(function() {
          $(".divtime").load("time.php");
      }, 5000);
      $(".divstatus").load("status.php");
      var refreshId3 = setInterval(function() {
          $(".divstatus").load("status.php");
      }, 5000);
      $(".downnow").load("downnow.php");
      var refreshId3 = setInterval(function() {
          $(".downnow").load("downnow.php");
      }, 5000);
      $(".lastdown").load("lastdown.php");
      var refreshId3 = setInterval(function() {
          $(".lastdown").load("lastdown.php");
      }, 5000);
  });
  </script>

</head>

<body>

<div class="container-fluid">
  
  <div class="mainrow">
    
    <div class="col-md-5 divtall">
      <div class="div1-half-top">
        <h2 class="calheading">KRING|PING - SITE CHECK</h2>
        <div class="divtime"></div>
      </div>
      <div class="div1-half-bottom">
        <video id="videoBG" autoplay muted loop>
        <source src="beach.mp4" type="video/mp4">
        </video>
        <div class="divtemp"></div>
        <div class="boxleft">
          <h2 class="calheadingbox"><i class="fas fa-exclamation-circle" aria-hidden="true"></i> SITES DOWN</h2>
          <div class="downnow"></div>
          
      </div>
      <div class="boxleft2">
          <h2 class="calheadingbox"><i class="fas fa-clock" aria-hidden="true"></i> LATEST ERROR</h2>
          <div class="lastdown"></div>
        </div>
      </div>
    </div>

    
    <div class="col-md-7 divtall">
      <div class="div2">
        <h2 class="calheading"><i class="fas fa-power-off" aria-hidden="true"></i> WEB SITE STATUS</h2>
        <div class="divstatus"></div>
    </div>
  
  </div>

</div>

</body>
</html>