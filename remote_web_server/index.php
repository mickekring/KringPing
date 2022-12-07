<!doctype html>
<html lang="en">
  <head>
     <meta charset="utf-8">
     <meta name="viewport" content="width=device-width, initial-scale=1">
     <title>KringPing - Site Checker</title>
     <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.0/jquery.min.js"></script>
     <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-rbsA2VBKQhggwzxH7pPCaAqO46MgnOM80zW1RWuH61DGLwZJEdK2Kadq2F9CUG65" crossorigin="anonymous">
     <link rel="stylesheet" type="text/css" href="style.css">
     <link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;500;600;700&family=Poppins:wght@300;400;700;800&display=swap" rel="stylesheet">
     <script src="https://kit.fontawesome.com/9b703bf6e7.js" crossorigin="anonymous"></script>

     <script>
  $(document).ready(function() {
      $(".status").load("status.php");
      var refreshId = setInterval(function() {
          $(".status").load("status.php");
      }, 5000);
  });
  </script>

  </head>
  <body>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-kenU1KFdBIe4zVF0s0G1M5b4hcpxyD9F7jL+jjXkk+Q2h455rYXK/7HAuoJl+0I4" crossorigin="anonymous"></script>
   
    <div class="container-sm">
      <div class="row">
        <div class="col titlediv">
        <h1><i class="fa-solid fa-server"></i> .KringPing</h1>
        </div>
      </div>
        
        <div class="status"></div>
       
    </div>
  </body>
</html>