<?php
/*require '../class-php/offEnd.php';
$exe=new offEnd('windows','../inicia.py');
echo $exe->start();

*/
$command = "..\\inicia.pyw";
// Use shell_exec ou exec, dependendo da sua necessidade de retorno/status
//echo shell_exec($command);
// ou
exec($command);


 ?>
