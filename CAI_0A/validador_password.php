<?php
/**
 * Anexo I: Validación e Inserción de Usuarios según la Política de Seguridad.
 */

/**
 * Valida si la contraseña cumple con las directivas de la organización:
 * 1. Mínimo 8 caracteres.
 * 2. Al menos una mayúscula y una minúscula.
 * 3. Al menos un dígito numérico (0-9).
 * 4. Al menos un símbolo: ! @ # $ % & * ^ ( ) - = { } [ ] \ : ; < > ? , . /
 *
 * @param string $password
 * @return bool True si cumple todos los requisitos, False en caso contrario.
 */
function validatePasswordPolicy($password) {
    // Regla 1: Longitud mínima de 8 caracteres
    if (strlen($password) < 8) {
        return false;
    }

    // Regla 2a: Al menos una letra mayúscula y al menos una minúscula
    if (!preg_match('/[A-Z]/', $password) || !preg_match('/[a-z]/', $password)) {
        return false;
    }

    // Regla 2b: Al menos un número (0-9)
    if (!preg_match('/[0-9]/', $password)) {
        return false;
    }

    // Regla 2c: Al menos un símbolo del listado permitido
    if (!preg_match('/[!@#\$%&\*\^\(\)\-=\{\}\[\]\\\:;<>\?,\.\/]/', $password)) {
        return false;
    }

    return true;
}

/**
 * Registra un nuevo usuario en la base de datos tras verificar la política de seguridad.
 *
 * @param string $username
 * @param string $password
 * @return int 0 si se inserta con éxito, 1 si no cumple la política, 2 si falla la BD.
 */
function addNewUser($username, $password) {
    global $connection;

    // Control previo: Validación técnica de la política antes de procesar
    if (!validatePasswordPolicy($password)) {
        return 1; // Error: La contraseña no cumple los requisitos de seguridad
    }

    // Saneamiento básico para evitar inyección SQL (siguiendo el criterio de clase)
    $username = str_replace("'", "''", $username);

    // Generación del hash (en este caso sha1 para coincidir con la práctica)
    $password = sha1($password);

    $q = "INSERT INTO " . TBL_USERS . " VALUES ('$username', '$password')";
    $result = mysql_query($q, $connection);

    if ($result) {
        return 0; // Registro completado con éxito
    } else {
        return 2; // Error de inserción en base de datos
    }
}
?>