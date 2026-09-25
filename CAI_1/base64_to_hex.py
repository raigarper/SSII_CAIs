import base64
import binascii
import json

# Datos de los 4 empleados extraídos de la tabla de la consultoría CAI 1
usuarios_cai1 = [
    {
        "nombre": "Luis Toreman Gerto",
        "hash_b64": "IVPqzJN3ToJlBFL+iscUnX+5TfeofzgYEyCb7p7c4dQ=",
        "salt": "40",
        "pista": "Palabra rara de la lengua inglesa"
    },
    {
        "nombre": "Ana Pearse Sanz",
        "hash_b64": "uk8KEM/134Q0XbxL9t5M7F8fj98LkmVoDIt1nqEQadU=",
        "salt": "51",
        "pista": "Contraseña común seguida de punto y dos números"
    },
    {
        "nombre": "Pedro Marteis Poncio",
        "hash_b64": "FPwPhQd5fiUveplyGXjfA1kNTAJOl+zWwNeXtTJ/c74=",
        "salt": "18",
        "pista": "Fecha de nacimiento de uno de sus hijos"
    },
    {
        "nombre": "Arturo Ruiz Gasca",
        "hash_b64": "S69Ye4GXUpcwsApivn+RJ43h+PUvrKQ8LWuqShtwt/U=",
        "salt": "31",
        "pista": "Combinación de nombre y apellidos con símbolo *"
    }
]

def b64_to_hex(b64_str: str) -> str:
    """Decodifica un string Base64 a su representación hexadecimal en minúsculas."""
    raw_bytes = base64.b64decode(b64_str.strip())
    return binascii.hexlify(raw_bytes).decode("utf-8").lower()

def main():
    print("=" * 80)
    print(" DECODIFICACIÓN BASE64 -> HEXADECIMAL (SHA-256 / 256 BITS)")
    print("=" * 80)

    datos_procesados = []
    lineas_hashcat_sufijo = []   # Formato hash:salt (sha256($pass.$salt), modo -m 1410)
    lineas_hashcat_prefijo = []  # Formato hash:salt (sha256($salt.$pass), modo -m 1420)
    lineas_hashes_puros = []

    for i, u in enumerate(usuarios_cai1, start=1):
        hex_digest = b64_to_hex(u["hash_b64"])
        num_bytes = len(bytes.fromhex(hex_digest))
        num_bits = num_bytes * 8

        registro = {
            "id": i,
            "nombre": u["nombre"],
            "hash_b64": u["hash_b64"],
            "hash_hex": hex_digest,
            "longitud_bytes": num_bytes,
            "longitud_bits": num_bits,
            "algoritmo_deducido": f"SHA-{num_bits}",
            "salt": u["salt"],
            "formato_hashcat": f"{hex_digest}:{u['salt']}",
            "pista": u["pista"]
        }
        datos_procesados.append(registro)

        # Preparar líneas para archivos de Hashcat
        lineas_hashcat_sufijo.append(f"{hex_digest}:{u['salt']}")
        lineas_hashes_puros.append(hex_digest)

        print(f"[{i}] {u['nombre']}")
        print(f"    - Base64 : {u['hash_b64']}")
        print(f"    - Hex    : {hex_digest} ({num_bits} bits -> SHA-256)")
        print(f"    - Salt   : {u['salt']}")
        print(f"    - Hashcat: {hex_digest}:{u['salt']}\n")

    # 1. Guardar resultados estructurados en JSON
    json_path = "hashes_cai1.json"
    with open(json_path, "w", encoding="utf-8") as f_json:
        json.dump(datos_procesados, f_json, indent=4, ensure_ascii=False)
    print(f"[+] Archivo JSON guardado con éxito: {json_path}")

    # 2. Guardar archivo TXT formateado para Hashcat (hash:salt)
    txt_hashcat_path = "hashes_hashcat.txt"
    with open(txt_hashcat_path, "w", encoding="utf-8") as f_txt:
        f_txt.write("\n".join(lineas_hashcat_sufijo) + "\n")
    print(f"[+] Archivo TXT para Hashcat guardado: {txt_hashcat_path}")

    # 3. Guardar archivo TXT individual por cada usuario para ataques dirigidos
    for reg in datos_procesados:
        filename = f"hash_user{reg['id']}.txt"
        with open(filename, "w", encoding="utf-8") as f_user:
            f_user.write(f"{reg['hash_hex']}:{reg['salt']}\n")
    print("[+] Archivos individuales generados: hash_user1.txt a hash_user4.txt\n")

if __name__ == "__main__":
    main()
