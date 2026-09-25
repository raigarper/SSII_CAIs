import base64
import binascii
import json

# Mensajes y HMAC (Base64) recibidos de la entidad financiera (CAI 1 Parte 2, enunciado B)
# Formato del mensaje: cuenta_origen cuenta_destino cantidad
mensajes_cai1b = [
    {"mensaje": "34567893 987344 120", "hmac_b64": "CLxpGZUJ6GkQzdNHOZsVJC1PVlUWDSg6e6oIu2Yv5Zk="},
    {"mensaje": "34567894 986454 10", "hmac_b64": "we7bS6LiKkOdZ408IXyReGUSexNm0F7kJXOeQGeCfyI="},
    {"mensaje": "34537895 957769 110", "hmac_b64": "bT42fKu1YvprxMGun/SUIarQC/Ie/emtRXQYxIrRg3I="},
]


def b64_to_hex(b64_str: str) -> str:
    """Decodifica un HMAC en Base64 a su representación hexadecimal en minúsculas."""
    raw_bytes = base64.b64decode(b64_str.strip())
    return binascii.hexlify(raw_bytes).decode("utf-8").lower()


def main():
    print("=" * 80)
    print(" NORMALIZACIÓN DE HMAC BASE64 -> HEXADECIMAL (FORMATO HASHCAT -m 1450)")
    print("=" * 80)

    registros = []
    lineas_hashcat = []

    for i, m in enumerate(mensajes_cai1b, start=1):
        hex_digest = b64_to_hex(m["hmac_b64"])
        num_bytes = len(bytes.fromhex(hex_digest))
        num_bits = num_bytes * 8

        registro = {
            "id": i,
            "mensaje": m["mensaje"],
            "hmac_b64": m["hmac_b64"],
            "hmac_hex": hex_digest,
            "longitud_bytes": num_bytes,
            "longitud_bits": num_bits,
            "algoritmo_deducido": f"HMAC-SHA-{num_bits}",
            "formato_hashcat_m1450": f"{hex_digest}:{m['mensaje']}",
        }
        registros.append(registro)
        lineas_hashcat.append(f"{hex_digest}:{m['mensaje']}")

        print(f"[{i}] Mensaje : {m['mensaje']}")
        print(f"    Base64  : {m['hmac_b64']}")
        print(f"    Hex     : {hex_digest} ({num_bits} bits -> HMAC-SHA-256)")
        print(f"    Hashcat : {hex_digest}:{m['mensaje']}\n")

    # 1. JSON estructurado con todos los datos
    with open("hashes_cai1b.json", "w", encoding="utf-8") as f_json:
        json.dump(registros, f_json, indent=4, ensure_ascii=False)
    print("[+] Archivo JSON guardado: hashes_cai1b.json")

    # 2. Fichero de entrada para Hashcat (modo 1450: hash:mensaje)
    with open("hashes_hmac.txt", "w", encoding="utf-8") as f_txt:
        f_txt.write("\n".join(lineas_hashcat) + "\n")
    print("[+] Archivo para Hashcat guardado: hashes_hmac.txt")


if __name__ == "__main__":
    main()
