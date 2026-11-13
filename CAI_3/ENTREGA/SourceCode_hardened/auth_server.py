"""
Servidor de Identidad (Authorization Server) - VERSION CORREGIDA (Blue Team)
CAI 3 - Parte 1 - Security Team 2 (ST-2)

Cada bloque de codigo incluye un comentario "FIX RT-xx / CODE-xx" que indica
que vulnerabilidad de evidencias/auditoria_codigo/hallazgos.md corrige.

Nota de alcance (ver enunciado): no se usan bases de datos reales ni
contenedores, ni gestores de secretos externos (Vault/KMS). Las claves y
secretos se leen de variables de entorno con un valor de desarrollo por
defecto, que debe sustituirse por un valor real en un despliegue serio.
"""
import os
import time
import base64
import secrets
import hmac
from io import BytesIO
from flask import Flask, request, jsonify, render_template, abort

# FIX CODE-02: AUTHLIB_INSECURE_TRANSPORT solo es aceptable porque todo el
# laboratorio corre en HTTP sobre localhost (sin TLS, fuera del alcance del
# CAI). En un despliegue real este servidor debe ir detras de HTTPS y esta
# linea debe eliminarse.
os.environ["AUTHLIB_INSECURE_TRANSPORT"] = "1"

from authlib.integrations.flask_oauth2 import AuthorizationServer
from authlib.oauth2.rfc6749 import grants
from authlib.oauth2.rfc7636 import CodeChallenge
from authlib.jose import jwt, jwk
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from passlib.context import CryptContext
import pyotp
import qrcode

app = Flask(__name__)

# FIX CODE-? (buena practica general): secretos leidos de entorno, con un
# valor de desarrollo solo para que el laboratorio funcione sin configurar
# nada. En produccion estas variables deben definirse fuera del codigo.
app.secret_key = os.environ.get("FLASK_SECRET_KEY", secrets.token_hex(32))
CLIENT_SECRET = os.environ.get("HOSPITAL_CLIENT_SECRET", "dev-secret-cambiar-en-produccion")
INTERNAL_API_KEY = os.environ.get("INTERNAL_API_KEY", "dev-internal-key-cambiar-en-produccion")

# --- FIX RT-01: firma asimetrica (RS256) en vez de clave simetrica publica ---
# Antes: una unica clave HS256 compartida, publicada sin autenticacion en
# /.well-known/jwt-key. Cualquiera podia leerla y FIRMAR tokens falsos.
# Ahora: el servidor genera un par de claves RSA. Firma con la clave PRIVADA
# (que nunca sale del servidor) y publica solo la clave PUBLICA en formato
# JWKS. Con la clave publica se puede VERIFICAR un token, pero no FORJARLO.
_rsa_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
PRIVATE_KEY_PEM = _rsa_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
)
PUBLIC_KEY_PEM = _rsa_key.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
)
JWK_KID = "hospital-identity-2026"
PUBLIC_JWK = jwk.dumps(PUBLIC_KEY_PEM, kty="RSA")
PUBLIC_JWK["kid"] = JWK_KID
PUBLIC_JWK["use"] = "sig"
PUBLIC_JWK["alg"] = "RS256"

app.config["OAUTH2_JWT_ALG"] = "RS256"
app.config["OAUTH2_ACCESS_TOKEN_EXPIRES_IN"] = 900  # 15 min (antes 1h)

# FIX CODE-05: el expires_in que se devuelve en /oauth/token debe coincidir
# con la caducidad real (exp) del JWT emitido. Antes se usaba el valor por
# defecto de Authlib (864000 s) mientras el JWT real caducaba en 3600 s.
app.config["OAUTH2_TOKEN_EXPIRES_IN"] = {
    "authorization_code": app.config["OAUTH2_ACCESS_TOKEN_EXPIRES_IN"],
    "refresh_token": app.config["OAUTH2_ACCESS_TOKEN_EXPIRES_IN"],
}

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

USERS = {
    "rocio": {
        "id": "1",
        "username": "rocio",
        "password_hash": pwd_context.hash("SuperSegura2026!"),
        "totp_secret": pyotp.random_base32(),
        "allowed_scopes": ["paciente:leer"],
    },
    "dr_gasca": {
        "id": "2",
        "username": "dr_gasca",
        "password_hash": pwd_context.hash("MedicoSegura2026!"),
        "totp_secret": pyotp.random_base32(),
        "allowed_scopes": ["paciente:leer", "medico:escribir"],
    },
}

# FIX RT-03: cliente CONFIDENCIAL (tiene client_secret) y obligado a usar
# PKCE. Antes era un cliente "none" (publico) sin PKCE.
CLIENTS = {
    "hospital-web": {
        "client_id": "hospital-web",
        "client_secret": CLIENT_SECRET,
        "redirect_uris": [
            "http://localhost:8001/callback",
            "http://127.0.0.1:8001/callback",
        ],
        "grant_types": ["authorization_code", "refresh_token"],
        "response_types": ["code"],
        "scope": "paciente:leer medico:escribir",
        "token_endpoint_auth_method": "client_secret_basic",
    }
}

AUTH_CODES = {}
TOKENS = {}
REVOKED_JTIS = set()  # FIX RT-08: lista de revocacion de tokens (en memoria)

# FIX RT-06 / RT-07: control de intentos fallidos y de codigos TOTP ya usados
LOGIN_ATTEMPTS = {}       # username -> [timestamps de fallos recientes]
MAX_ATTEMPTS = 5
LOCKOUT_SECONDS = 60
USED_TOTP_CODES = {}      # username -> set of (time_step, code) ya consumidos

MSG_LOGIN_INVALIDO = "Usuario, contraseña o código FreeOTP incorrectos."
MSG_CUENTA_BLOQUEADA = "Cuenta bloqueada temporalmente por demasiados intentos fallidos. Inténtalo de nuevo en un minuto."


class ClientObj:
    def __init__(self, data):
        self.__dict__.update(data)

    def get_client_id(self):
        return self.client_id

    def get_default_redirect_uri(self):
        return self.redirect_uris[0] if self.redirect_uris else None

    def check_redirect_uri(self, uri):
        return uri in self.redirect_uris

    def check_grant_type(self, gt):
        return gt in self.grant_types

    def check_response_type(self, rt):
        return rt in self.response_types

    def check_endpoint_auth_method(self, method, endpoint):
        return method == self.token_endpoint_auth_method

    def check_client_secret(self, client_secret):
        # FIX RT-03: comparacion en tiempo constante del client_secret.
        return hmac.compare_digest(client_secret or "", self.client_secret)

    def get_allowed_scope(self, scope):
        if not scope:
            return ""
        client_scopes = set(self.scope.split())
        requested_scopes = scope.split()
        return " ".join([s for s in requested_scopes if s in client_scopes])


class AuthCodeObj:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def is_expired(self):
        return time.time() > self.expires_at

    def get_redirect_uri(self):
        return self.redirect_uri

    def get_scope(self):
        return self.scope


class TokenObj:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def get_scope(self):
        return self.scope


class AuthorizationCodeGrant(grants.AuthorizationCodeGrant):
    # FIX RT-03: ya no se acepta "none"; el cliente debe autenticarse.
    TOKEN_ENDPOINT_AUTH_METHODS = ["client_secret_basic"]

    def save_authorization_code(self, code, request):
        requested = (request.scope or "").split()
        user_allowed = set(request.user.get("allowed_scopes", []))
        final_scope = " ".join([s for s in requested if s in user_allowed])

        AUTH_CODES[code] = AuthCodeObj(
            code=code,
            client_id=request.client.client_id,
            redirect_uri=request.redirect_uri,
            scope=final_scope,
            user_id=request.user["id"],
            code_challenge=request.data.get("code_challenge"),
            code_challenge_method=request.data.get("code_challenge_method"),
            expires_at=time.time() + 300,
        )

    def query_authorization_code(self, code, client):
        item = AUTH_CODES.get(code)
        if item and item.client_id == client.client_id and not item.is_expired():
            return item

    def delete_authorization_code(self, authorization_code):
        AUTH_CODES.pop(authorization_code.code, None)

    def authenticate_user(self, authorization_code):
        return next((u for u in USERS.values() if u["id"] == authorization_code.user_id), None)


class RefreshTokenGrant(grants.RefreshTokenGrant):
    TOKEN_ENDPOINT_AUTH_METHODS = ["client_secret_basic"]
    INCLUDE_NEW_REFRESH_TOKEN = True  # FIX CODE-04: rotar el refresh token

    def authenticate_refresh_token(self, refresh_token):
        return TOKENS.get(refresh_token)

    def authenticate_user(self, credential):
        return next((u for u in USERS.values() if u["id"] == credential.user_id), None)

    def revoke_old_credential(self, credential):
        # FIX CODE-04: al rotar, el refresh token anterior deja de servir.
        for rt, obj in list(TOKENS.items()):
            if obj is credential:
                TOKENS.pop(rt, None)


def generate_jwt_access_token(client, grant_type, user, scope):
    now = int(time.time())
    header = {"alg": app.config["OAUTH2_JWT_ALG"], "kid": JWK_KID}
    payload = {
        "iss": "http://localhost:8000",
        "sub": user["username"],
        "aud": client.client_id,
        "scope": scope,
        "iat": now,
        "exp": now + app.config["OAUTH2_ACCESS_TOKEN_EXPIRES_IN"],
        "jti": secrets.token_hex(16),  # FIX RT-08: identificador unico revocable
    }
    return jwt.encode(header, payload, PRIVATE_KEY_PEM).decode()


def save_token(token_data, request):
    if "refresh_token" in token_data:
        TOKENS[token_data["refresh_token"]] = TokenObj(
            user_id=request.user["id"],
            client_id=request.client.client_id,
            scope=token_data.get("scope", ""),
        )


app.config["OAUTH2_ACCESS_TOKEN_GENERATOR"] = generate_jwt_access_token
server = AuthorizationServer(
    app,
    query_client=lambda cid: ClientObj(CLIENTS[cid]) if cid in CLIENTS else None,
    save_token=save_token,
)
# FIX RT-03: PKCE obligatorio (required=True) con S256.
server.register_grant(AuthorizationCodeGrant, [CodeChallenge(required=True)])
server.register_grant(RefreshTokenGrant)


def _is_locked_out(username):
    attempts = [t for t in LOGIN_ATTEMPTS.get(username, []) if time.time() - t < LOCKOUT_SECONDS]
    LOGIN_ATTEMPTS[username] = attempts
    return len(attempts) >= MAX_ATTEMPTS


def _register_failed_attempt(username):
    LOGIN_ATTEMPTS.setdefault(username, []).append(time.time())


def _totp_already_used(username, totp_obj, code):
    step = int(time.time() // totp_obj.interval)
    used = USED_TOTP_CODES.setdefault(username, set())
    # FIX RT-07: se comprueba el paso actual y el anterior/siguiente (por el
    # valid_window=1 que seguimos aceptando para tolerar el desfase de reloj).
    for s in (step - 1, step, step + 1):
        if (s, code) in used:
            return True
    return False


def _mark_totp_used(username, totp_obj, code):
    step = int(time.time() // totp_obj.interval)
    used = USED_TOTP_CODES.setdefault(username, set())
    used.add((step, code))
    # limpieza simple para no crecer indefinidamente
    if len(used) > 50:
        USED_TOTP_CODES[username] = {u for u in used if u[0] >= step - 2}


@app.route("/setup-mfa", methods=["GET", "POST"])
def setup_mfa():
    """
    FIX RT-02: antes este endpoint no pedia ninguna credencial y devolvia el
    secreto TOTP de cualquier usuario solo con ?user=<nombre>. Ahora exige
    la contraseña del usuario (formulario POST) antes de mostrar el QR, y ya
    no se muestra el secreto en texto plano en la pagina.
    """
    username = request.values.get("user", "rocio")
    user = USERS.get(username, USERS["rocio"])

    if request.method == "GET":
        return render_template("setup_mfa.html", username=user["username"], pedir_password=True)

    password = request.form.get("password", "")
    if not pwd_context.verify(password, user["password_hash"]):
        return render_template(
            "setup_mfa.html", username=user["username"], pedir_password=True,
            error="Contraseña incorrecta. No se puede mostrar el código QR.",
        ), 401

    uri = pyotp.TOTP(user["totp_secret"]).provisioning_uri(
        f"{user['username']}@hospital.es", issuer_name="Hospital-Seguro"
    )
    img = qrcode.make(uri)
    buf = BytesIO()
    img.save(buf, format="PNG")
    qr_b64 = base64.b64encode(buf.getvalue()).decode()
    return render_template("setup_mfa.html", qr_b64=qr_b64, username=user["username"], pedir_password=False)


@app.route("/oauth/authorize", methods=["GET", "POST"])
def authorize():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username", "")
    password = request.form.get("password", "")
    totp_code = request.form.get("totp", "")

    # FIX RT-06: un unico mensaje de error generico para no permitir
    # distinguir "usuario no existe" de "contraseña incorrecta".
    if _is_locked_out(username):
        return render_template("login.html", error=MSG_CUENTA_BLOQUEADA), 429

    user = USERS.get(username)
    if not user:
        _register_failed_attempt(username)
        return render_template("login.html", error=MSG_LOGIN_INVALIDO), 401

    if not pwd_context.verify(password, user["password_hash"]):
        _register_failed_attempt(username)
        return render_template("login.html", error=MSG_LOGIN_INVALIDO), 401

    totp_obj = pyotp.TOTP(user["totp_secret"])
    if not totp_obj.verify(totp_code, valid_window=1):
        _register_failed_attempt(username)
        return render_template("login.html", error=MSG_LOGIN_INVALIDO), 401

    # FIX RT-07: el codigo TOTP solo puede usarse una vez.
    if _totp_already_used(username, totp_obj, totp_code):
        _register_failed_attempt(username)
        return render_template("login.html", error=MSG_LOGIN_INVALIDO), 401
    _mark_totp_used(username, totp_obj, totp_code)

    LOGIN_ATTEMPTS.pop(username, None)  # login correcto: reiniciar contador
    return server.create_authorization_response(grant_user=user)


@app.route("/oauth/token", methods=["POST"])
def issue_token():
    return server.create_token_response()


@app.route("/oauth/revoke", methods=["POST"])
def revoke_token():
    """
    FIX RT-08: revocacion real. El cliente llama aqui en /logout con el
    access_token y sus credenciales; el jti queda marcado como revocado.
    """
    client_id = request.form.get("client_id", "")
    client_secret = request.form.get("client_secret", "")
    client = CLIENTS.get(client_id)
    if not client or not hmac.compare_digest(client_secret, client["client_secret"]):
        abort(401)

    token = request.form.get("token", "")
    try:
        # No exigimos que siga vigente: queremos poder revocar incluso si
        # esta a punto de caducar. Verificamos solo la firma.
        claims = jwt.decode(token, PUBLIC_KEY_PEM)
        jti = claims.get("jti")
        if jti:
            REVOKED_JTIS.add(jti)
    except Exception:
        pass
    return jsonify({"status": "ok"})


@app.route("/internal/jti-status")
def jti_status():
    """
    FIX RT-08: endpoint interno (servidor-a-servidor) para que el Portal
    Medico compruebe si un token ha sido revocado. Protegido con una clave
    compartida distinta del client_secret OAuth2 (uso exclusivamente
    interno, no es parte del flujo OAuth2 estandar).
    """
    if not hmac.compare_digest(request.headers.get("X-Internal-Key", ""), INTERNAL_API_KEY):
        abort(401)
    jti = request.args.get("jti", "")
    return jsonify({"revoked": jti in REVOKED_JTIS})


@app.route("/.well-known/jwks.json")
def jwks():
    # FIX RT-01: solo se publica la clave PUBLICA. No permite firmar nada.
    return jsonify({"keys": [PUBLIC_JWK]})


if __name__ == "__main__":
    # FIX CODE-01: debug=False. El depurador interactivo de Werkzeug queda
    # desactivado (evita una posible ejecucion remota de codigo).
    app.run(port=8000, debug=False)
