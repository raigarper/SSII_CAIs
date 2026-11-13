"""
Portal Medico (Cliente OAuth2 + API) - VERSION CORREGIDA (Blue Team)
CAI 3 - Parte 1 - Security Team 2 (ST-2)

Cada bloque incluye un comentario "FIX RT-xx / CODE-xx" indicando la
vulnerabilidad de evidencias/auditoria_codigo/hallazgos.md que corrige.
"""
import os
import time
import secrets
import requests
from flask import Flask, redirect, url_for, request, jsonify, make_response, render_template

# FIX CODE-02: ver nota identica en auth_server.py (solo valido en este
# laboratorio HTTP/localhost; eliminar en un despliegue con TLS real).
os.environ["AUTHLIB_INSECURE_TRANSPORT"] = "1"

from authlib.integrations.flask_client import OAuth
from authlib.oauth2.rfc6750 import BearerTokenValidator
from authlib.oauth2.rfc6749.util import scope_to_list
from authlib.integrations.flask_oauth2 import ResourceProtector
from authlib.jose import jwt, JoseError

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", secrets.token_hex(32))

CLIENT_SECRET = os.environ.get("HOSPITAL_CLIENT_SECRET", "dev-secret-cambiar-en-produccion")
INTERNAL_API_KEY = os.environ.get("INTERNAL_API_KEY", "dev-internal-key-cambiar-en-produccion")
AUTH_SERVER = "http://localhost:8000"

oauth = OAuth(app)
oauth.register(
    name="hospital_insegus",
    client_id="hospital-web",
    client_secret=CLIENT_SECRET,  # FIX RT-03: cliente confidencial
    authorize_url=f"{AUTH_SERVER}/oauth/authorize",
    access_token_url=f"{AUTH_SERVER}/oauth/token",
    client_kwargs={
        "scope": "paciente:leer medico:escribir",
        "token_endpoint_auth_method": "client_secret_basic",
        "code_challenge_method": "S256",  # FIX RT-03: activa PKCE automaticamente
    },
)

EXPECTED_ISS = f"{AUTH_SERVER}"
EXPECTED_AUD = "hospital-web"

# FIX RT-01 (lado cliente): cache de la clave publica (JWKS) con una
# pequeña validez, en vez de pedirla a cada peticion. Ya no es una clave
# secreta que haya que proteger, pero cachearla evita una llamada de red
# extra por cada peticion a la API.
_jwks_cache = {"key": None, "fetched_at": 0}
JWKS_CACHE_TTL = 300  # 5 min


def _get_public_key():
    now = time.time()
    if _jwks_cache["key"] is None or now - _jwks_cache["fetched_at"] > JWKS_CACHE_TTL:
        data = requests.get(f"{AUTH_SERVER}/.well-known/jwks.json", timeout=5).json()
        _jwks_cache["key"] = data["keys"][0]
        _jwks_cache["fetched_at"] = now
    return _jwks_cache["key"]


def _is_revoked(jti):
    # FIX RT-08: comprobamos la revocacion contra el servidor en cada
    # peticion a la API (llamada interna autenticada con INTERNAL_API_KEY).
    if not jti:
        return False
    try:
        resp = requests.get(
            f"{AUTH_SERVER}/internal/jti-status",
            params={"jti": jti},
            headers={"X-Internal-Key": INTERNAL_API_KEY},
            timeout=5,
        )
        return bool(resp.json().get("revoked"))
    except requests.RequestException:
        # Si el servidor de identidad no responde, por seguridad se
        # rechaza el token en vez de aceptarlo a ciegas.
        return True


class JWTTokenObj:
    def __init__(self, claims):
        self.claims = claims
        self.scope = claims.get("scope", "")

    def is_expired(self):
        exp = self.claims.get("exp")
        return exp is not None and time.time() > exp

    def is_revoked(self):
        return False

    def get_scope(self):
        return self.scope


class JWTBearerValidator(BearerTokenValidator):
    def authenticate_token(self, token_string):
        try:
            public_jwk = _get_public_key()
            # FIX CODE-03: se restringe explicitamente el algoritmo
            # aceptado (RS256) para evitar confusion de algoritmo, y se
            # valida iss/aud contra los valores esperados de este portal.
            claims = jwt.decode(
                token_string,
                public_jwk,
                claims_options={
                    "iss": {"essential": True, "value": EXPECTED_ISS},
                    "aud": {"essential": True, "value": EXPECTED_AUD},
                    "exp": {"essential": True},
                },
            )
            claims.validate()

            if claims.header.get("alg") != "RS256":
                return None

            # FIX RT-08: rechazar tokens cuyo jti haya sido revocado
            # (por ejemplo, al hacer logout).
            if _is_revoked(claims.get("jti")):
                return None

            return JWTTokenObj(claims)
        except JoseError:
            return None

    def request_invalid(self, request):
        return False

    def token_revoked(self, token):
        return False

    def scope_insufficient(self, token_scopes, required_scopes):
        if not required_scopes:
            return False
        token_scope_set = set(scope_to_list(token_scopes))
        required_scope_set = set(scope_to_list(required_scopes))
        return not required_scope_set.issubset(token_scope_set)


require_oauth = ResourceProtector()
require_oauth.register_token_validator(JWTBearerValidator())


def _set_secure_cookie(resp, value):
    # FIX RT-05 / RT-08: cookie HttpOnly (no accesible desde JavaScript),
    # SameSite=Strict (mitiga CSRF) y vida corta alineada con el JWT.
    resp.set_cookie(
        "access_token",
        value,
        httponly=True,
        samesite="Strict",
        secure=request.is_secure,  # True automaticamente en HTTPS
        max_age=900,
    )
    return resp


@app.after_request
def set_security_headers(resp):
    # FIX CODE-07 (defensa en profundidad): cabeceras basicas de seguridad.
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "no-referrer"
    resp.headers["Content-Security-Policy"] = "default-src 'self'"
    resp.headers["Cache-Control"] = "no-store"
    return resp


@app.route("/")
def index():
    # FIX RT-05: ya no se lee el usuario desde el JWT en el navegador via
    # JavaScript. Si hay sesion, el propio servidor decodifica el JWT (que
    # ya no es accesible por JS) y pasa el nombre de usuario a la plantilla.
    username = None
    token = request.cookies.get("access_token")
    if token:
        validator = JWTBearerValidator()
        token_obj = validator.authenticate_token(token)
        if token_obj:
            username = token_obj.claims.get("sub")
    return render_template("portal.html", username=username)


@app.route("/login")
def login():
    redirect_uri = url_for("callback", _external=True)
    return oauth.hospital_insegus.authorize_redirect(redirect_uri)


@app.route("/callback")
def callback():
    token = oauth.hospital_insegus.authorize_access_token()
    resp = make_response(redirect("/"))
    return _set_secure_cookie(resp, token["access_token"])


@app.route("/logout", methods=["POST"])
def logout():
    # FIX RT-08: /logout ahora exige POST (evita que un simple enlace/imagen
    # cierre la sesion de otro usuario - CSRF trivial sobre GET) y revoca el
    # token en el servidor de identidad, no solo borra la cookie local.
    token = request.cookies.get("access_token")
    if token:
        try:
            requests.post(
                f"{AUTH_SERVER}/oauth/revoke",
                data={
                    "client_id": "hospital-web",
                    "client_secret": CLIENT_SECRET,
                    "token": token,
                },
                timeout=5,
            )
        except requests.RequestException:
            pass
    resp = make_response(redirect("/"))
    resp.delete_cookie("access_token")
    return resp


@app.before_request
def inject_bearer_from_cookie():
    if request.path.startswith("/api/") and "Authorization" not in request.headers:
        token = request.cookies.get("access_token")
        if token:
            request.environ["HTTP_AUTHORIZATION"] = f"Bearer {token}"


@app.route("/api/historial", methods=["GET"])
@require_oauth("paciente:leer")
def get_historial():
    return jsonify({
        "status": "ok",
        "datos": "Historial clínico confidencial (Grupo O+)",
    })


@app.route("/api/historial", methods=["POST"])
@require_oauth("medico:escribir")  # FIX RT-04: exige el scope correcto
def post_historial():
    datos = request.get_json(silent=True) or {}
    diagnostico = datos.get("diagnostico", "")
    return jsonify({
        "status": "ok",
        "mensaje": f"Historial médico actualizado con: {diagnostico}",
    })


if __name__ == "__main__":
    # FIX CODE-01: debug=False en produccion/pruebas de seguridad.
    app.run(port=8001, debug=False)
