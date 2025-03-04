<?php
$archivo = "comando.txt";
file_put_contents($archivo, " "); // Escribe un espacio en blanco para "borrar" el comando
echo "Comando borrado.";
?>
