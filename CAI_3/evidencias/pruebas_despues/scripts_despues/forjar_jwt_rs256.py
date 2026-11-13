"""
RT-01 (verificacion POST-fix): intenta forjar un JWT RS256 con una clave
privada PROPIA del atacante (nunca con la del servidor, que ya no se
publica). Si el servidor corregido esta bien hecho, el token debe ser
rechazado, porque el cliente verifica contra la clave PUBLICA real del
servidor (obtenida de /.well-known/jwks.json), no contra cualquier clave.
"""
import time
from authlib.jose import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

atacante_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
atacante_priv_pem = atacante_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
)

now = int(time.time())
header = {"alg": "RS256", "kid": "hospital-identity-2026"}
payload = {
    "iss": "http://localhost:8000",
    "sub": "dr_gasca",
    "aud": "hospital-web",
    "scope": "paciente:leer medico:escribir",
    "iat": now,
    "exp": now + 3600,
    "jti": "forjado-123",
}
token = jwt.encode(header, payload, atacante_priv_pem).decode()
print(token)
