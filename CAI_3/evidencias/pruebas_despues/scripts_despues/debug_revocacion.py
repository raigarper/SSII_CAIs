import sys
import requests
from authlib.jose import jwt

token = open(sys.argv[1]).read().strip()
jwks = requests.get("http://localhost:8000/.well-known/jwks.json").json()["keys"][0]
claims = jwt.decode(token, jwks)
jti = claims.get("jti")
print("jti:", jti)

resp = requests.get(
    "http://localhost:8000/internal/jti-status",
    params={"jti": jti},
    headers={"X-Internal-Key": "dev-internal-key-cambiar-en-produccion"},
)
print("jti-status:", resp.status_code, resp.text)

api_resp = requests.get(
    "http://localhost:8001/api/historial",
    headers={"Authorization": f"Bearer {token}"},
)
print("API directa:", api_resp.status_code, api_resp.text)
