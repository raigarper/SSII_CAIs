"""
RT-08 (verificacion post-fix): ciclo completo.
1. Login legitimo -> access_token.
2. Se usa el token contra la API (debe funcionar).
3. Se llama a /oauth/revoke (lo que hace el boton "Cerrar sesion").
4. Se reutiliza el MISMO token (debe ser rechazado).
"""
import sys
sys.path.insert(0, "evidencias/pruebas_despues/scripts_despues")
from flujo_pkce_completo import login_y_obtener_token
import requests

AUTH = "http://localhost:8000"
API = "http://localhost:8001/api/historial"
CLIENT_ID = "hospital-web"
CLIENT_SECRET = "dev-secret-cambiar-en-produccion"

data = login_y_obtener_token("dr_gasca", "MedicoSegura2026!")
token = data["access_token"]
print("1) Login OK, token obtenido.")

r1 = requests.get(API, headers={"Authorization": f"Bearer {token}"})
print(f"2) Uso ANTES de logout -> HTTP {r1.status_code}")

r2 = requests.post(f"{AUTH}/oauth/revoke", data={
    "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "token": token,
})
print(f"3) /oauth/revoke -> HTTP {r2.status_code} {r2.text}")

r3 = requests.get(API, headers={"Authorization": f"Bearer {token}"})
print(f"4) Uso DESPUES de logout (mismo token) -> HTTP {r3.status_code} {r3.text}")
