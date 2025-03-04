<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="2"> <!-- Actualiza la página cada 2 segundos -->
    <title>Control de Ventanas</title>
</head>
<body>

    <h1>Estado del Comando</h1>

    <?php
    // **CONFIGURACIÓN DEL BOT TELEGRAM**
    $botToken = "BotToken";  
    $chatId = "ID";    
    $telegramUrl = "https://api.telegram.org/bot$botToken/getUpdates";
    $archivo = "comando.txt";

    // **FUNCIÓN PARA LEER EL ÚLTIMO MENSAJE NUEVO DESDE TELEGRAM**
    function obtenerUltimoMensaje() {
        global $telegramUrl, $botToken;

        // Obtener los datos desde Telegram
        $response = @file_get_contents($telegramUrl);
        if ($response === FALSE) {
            return null; // Evita errores si la API no responde
        }

        $data = json_decode($response, true);
        if (!isset($data["result"]) || empty($data["result"])) {
            return null; // No hay mensajes nuevos
        }

        $mensajes = $data["result"];
        $ultimoMensaje = end($mensajes);

        // Marcar el mensaje como leído usando `offset`
        if (isset($ultimoMensaje["update_id"])) {
            $ultimoUpdateID = $ultimoMensaje["update_id"] + 1; // Para evitar leerlo de nuevo
            file_get_contents("https://api.telegram.org/bot$botToken/getUpdates?offset=$ultimoUpdateID");
        }

        // Extraer y devolver el mensaje en minúsculas y sin espacios extra
        if (isset($ultimoMensaje["message"]["text"])) {
            return strtolower(trim($ultimoMensaje["message"]["text"]));
        }

        return null;
    }

    // **GUARDAR COMANDO EN `comando.txt`**
    $comando = obtenerUltimoMensaje();
    if ($comando) {
        $comandos_permitidos = ["abrir", "cerrar", "reset"]; // Agregamos "reset"

        if (in_array($comando, $comandos_permitidos)) {
            file_put_contents($archivo, $comando);
            echo "<p style='color:green;'> Comando desde Telegram guardado: <strong>$comando</strong></p>";
        } else {
            echo "<p style='color:red;'> Comando no válido desde Telegram.</p>";
        }
    } else {
        echo "<p style='color:red;'> No se recibió ningún mensaje desde Telegram.</p>";
    }

    // **MOSTRAR EL ÚLTIMO COMANDO GUARDADO**
    if (file_exists($archivo)) {
        $ultimo_comando = file_get_contents($archivo);
        echo "<h2>Último comando recibido: <strong>$ultimo_comando</strong></h2>";
    } else {
        echo "<h2>No se ha recibido ningún comando aún.</h2>";
    }

    // **ENVÍO DE MENSAJES A TELEGRAM**
    if (isset($_GET['mensaje'])) {
        $mensaje = trim($_GET['mensaje']);
        $mensaje = urlencode($mensaje); // Convertir a formato URL seguro

        // Construir la URL de la API de Telegram
        $url = "https://api.telegram.org/bot$botToken/sendMessage?chat_id=$chatId&text=$mensaje";

        // Intentar enviar el mensaje
        $response = file_get_contents($url);
        if ($response !== false) {
            echo "<p style='color:green;'> Mensaje enviado a Telegram.</p>";
        } else {
            echo "<p style='color:red;'> Error al enviar mensaje a Telegram.</p>";
        }
    }
    ?>

</body>
</html>
