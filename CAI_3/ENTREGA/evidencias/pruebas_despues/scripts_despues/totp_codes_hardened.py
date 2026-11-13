"""
Codigos TOTP para las pruebas de verificacion (Fase 4) contra la version
corregida (SourceCode_hardened). A diferencia de la Fase 1, estos secretos
se obtuvieron de forma LEGITIMA: usando la contrasena real de cada usuario
en /setup-mfa (que ahora la exige, FIX RT-02) y decodificando el QR que el
propio usuario recibiria en su movil.
"""
import sys
import pyotp

SECRETS = {
    "rocio": "IVFTZYNSFFUUYR4FA3OUUZ6SJDTGT6TE",
    "dr_gasca": "MPOVVPZXEYIZUPKQ56WO2T2P7XFYNLDH",
}

def get_code(user: str) -> str:
    return pyotp.TOTP(SECRETS[user]).now()

if __name__ == "__main__":
    user = sys.argv[1] if len(sys.argv) > 1 else "rocio"
    print(get_code(user))
