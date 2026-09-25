#!/bin/bash
# run_attack.sh - Script de automatización de fuerza bruta para HMAC 32-bit

if [ ! -f "hashes_hmac.txt" ]; then
    echo "[-] Falta el archivo hashes_hmac.txt con las entradas hash:mensaje"
    exit 1
fi

echo "[*] Selecciona el modo de Hashcat:"
echo "    50   -> HMAC-MD5 (128 bits)"
echo "    150  -> HMAC-SHA1 (160 bits)"
echo "    1450 -> HMAC-SHA256 (256 bits)"
read -p "Introduce el modo (-m): " MODO

echo "[*] Lanzando benchmark de velocidad..."
hashcat -m $MODO -b -D 1 -O | grep -E "Speed.#1|Speed.#"

echo "[*] Ejecutando ataque de fuerza bruta sobre claves de 4 bytes (2^32 combinaciones)..."
# Clave de 32 bits = 4 bytes crudos, no necesariamente ASCII imprimible.
# ?b cubre el rango completo 0x00-0xff, por lo que ?b?b?b?b agota el espacio 2^32.
hashcat -m $MODO -a 3 -D 1 -O hashes_hmac.txt ?b?b?b?b --outfile soluciones_hmac.txt

echo "[+] Ataque finalizado. Resultados:"
cat soluciones_hmac.txt