"""
Genera codigos TOTP de 6 digitos para los usuarios de prueba.

Los secretos se obtuvieron SIN AUTENTICACION desde el endpoint
/setup-mfa del Servidor de Identidad (puerto 8000), lo cual ya es
en si mismo la Vulnerabilidad RT-02 (ver hallazgos.md).

Uso:
    python totp_codes.py rocio
    python totp_codes.py dr_gasca
"""
import sys
import pyotp

SECRETS = {
    "rocio": "QXRSRXSHW4Z2ZPPTQCGFMSR5CIA5ETSS",
    "dr_gasca": "XGBFGLJM7X4FTJ6YQ7H4E772M6Q5ZMGE",
}

def get_code(user: str) -> str:
    if user not in SECRETS:
        raise ValueError(f"Usuario desconocido: {user}. Usa: {list(SECRETS)}")
    return pyotp.TOTP(SECRETS[user]).now()

if __name__ == "__main__":
    user = sys.argv[1] if len(sys.argv) > 1 else "rocio"
    print(get_code(user))
