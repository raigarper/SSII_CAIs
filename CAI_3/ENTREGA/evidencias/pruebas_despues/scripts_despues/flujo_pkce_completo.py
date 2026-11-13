"""
Simula el flujo OAuth2 + PKCE completo como lo haria el Portal Medico,
para poder obtener un access_token real y probar RT-08 (revocacion en
logout) de principio a fin desde un script.
"""
import sys
import base64
import hashlib
import secrets
import requests

sys.path.insert(0, "evidencias/pruebas_despues/scripts_despues")
from totp_codes_hardened import get_code

AUTH = "http://localhost:8000"
CLIENT_ID = "hospital-web"
CLIENT_SECRET = "dev-secret-cambiar-en-produccion"
REDIRECT_URI = "http://localhost:8001/callback"


def login_y_obtener_token(username, password):
    code_verifier = secrets.token_urlsafe(48)
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).rstrip(b"=").decode()

    authorize_url = (
        f"{AUTH}/oauth/authorize?response_type=code&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}&scope=paciente:leer+medico:escribir"
        f"&state=script&code_challenge={code_challenge}&code_challenge_method=S256"
    )

    totp = get_code(username)
    passwords = {"rocio": password, "dr_gasca": password}
    resp = requests.post(
        authorize_url,
        data={"username": username, "password": password, "totp": totp},
        allow_redirects=False,
    )
    if resp.status_code != 302:
        raise RuntimeError(f"Login fallido: {resp.status_code} {resp.text[:200]}")

    location = resp.headers["Location"]
    code = location.split("code=")[1].split("&")[0]

    token_resp = requests.post(
        f"{AUTH}/oauth/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "code_verifier": code_verifier,
        },
        auth=(CLIENT_ID, CLIENT_SECRET),  # client_secret_basic
    )
    token_resp.raise_for_status()
    return token_resp.json()


if __name__ == "__main__":
    user = sys.argv[1] if len(sys.argv) > 1 else "dr_gasca"
    pwd = sys.argv[2] if len(sys.argv) > 2 else "MedicoSegura2026!"
    data = login_y_obtener_token(user, pwd)
    print(data["access_token"])
