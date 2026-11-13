import os
os.environ["AUTHLIB_INSECURE_TRANSPORT"] = "1"
import time
import base64
import secrets
from io import BytesIO
from flask import Flask, request, jsonify, render_template
from authlib.integrations.flask_oauth2 import AuthorizationServer
from authlib.oauth2.rfc6749 import grants
from authlib.oauth2.rfc7636 import CodeChallenge
from authlib.jose import jwt
from passlib.context import CryptContext
import pyotp
import qrcode

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

app.config["OAUTH2_JWT_KEY"] = secrets.token_hex(32)
app.config["OAUTH2_JWT_ALG"] = "HS256"
app.config["OAUTH2_ACCESS_TOKEN_EXPIRES_IN"] = 3600

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

USERS = {
    "rocio": {
        "id": "1",
        "username": "rocio",
        "password_hash": pwd_context.hash("SuperSegura2026!"),
        "totp_secret": pyotp.random_base32(),
        "allowed_scopes": ["paciente:leer"]
    },
    "dr_gasca": {
        "id": "2",
        "username": "dr_gasca",
        "password_hash": pwd_context.hash("MedicoSegura2026!"),
        "totp_secret": pyotp.random_base32(),
        "allowed_scopes": ["paciente:leer", "medico:escribir"]
    }
}

CLIENTS = {
    "hospital-web": {
        "client_id": "hospital-web",
        "redirect_uris": [
            "http://localhost:8001/callback",
            "http://127.0.0.1:8001/callback"
        ],
        "grant_types": ["authorization_code", "refresh_token"],
        "response_types": ["code"],
        "scope": "paciente:leer medico:escribir",
        "token_endpoint_auth_method": "none"
    }
}

AUTH_CODES = {}
TOKENS = {}

class ClientObj:
    def __init__(self, data): self.__dict__.update(data)
    def get_client_id(self): return self.client_id
    def get_default_redirect_uri(self): return self.redirect_uris[0] if self.redirect_uris else None
    def check_redirect_uri(self, uri): return uri in self.redirect_uris
    def check_grant_type(self, gt): return gt in self.grant_types
    def check_response_type(self, rt): return rt in self.response_types
    def check_endpoint_auth_method(self, method, endpoint): return method == self.token_endpoint_auth_method
    def get_allowed_scope(self, scope):
        if not scope:
            return ""
        client_scopes = set(self.scope.split())
        requested_scopes = scope.split()
        return " ".join([s for s in requested_scopes if s in client_scopes])

class AuthCodeObj:
    def __init__(self, **kwargs): self.__dict__.update(kwargs)
    def is_expired(self): return time.time() > self.expires_at
    def get_redirect_uri(self): return self.redirect_uri
    def get_scope(self): return self.scope

class TokenObj:
    def __init__(self, **kwargs): self.__dict__.update(kwargs)
    def get_scope(self): return self.scope

class AuthorizationCodeGrant(grants.AuthorizationCodeGrant):
    TOKEN_ENDPOINT_AUTH_METHODS = ["none"]

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
            expires_at=time.time() + 300
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
    INCLUDE_NEW_REFRESH_TOKEN = False

    def authenticate_refresh_token(self, refresh_token):
        return TOKENS.get(refresh_token)

    def authenticate_user(self, credential):
        return next((u for u in USERS.values() if u["id"] == credential.user_id), None)

    def revoke_old_credential(self, credential):
        pass

def generate_jwt_access_token(client, grant_type, user, scope):
    now = int(time.time())
    header = {"alg": app.config["OAUTH2_JWT_ALG"]}
    payload = {
        "iss": "http://localhost:8000",
        "sub": user["username"],
        "aud": client.client_id,
        "scope": scope,
        "iat": now,
        "exp": now + app.config["OAUTH2_ACCESS_TOKEN_EXPIRES_IN"]
    }
    return jwt.encode(header, payload, app.config["OAUTH2_JWT_KEY"]).decode()

def save_token(token_data, request):
    if "refresh_token" in token_data:
        TOKENS[token_data["refresh_token"]] = TokenObj(
            user_id=request.user["id"],
            client_id=request.client.client_id,
            scope=token_data.get("scope", "")
        )

app.config["OAUTH2_ACCESS_TOKEN_GENERATOR"] = generate_jwt_access_token
server = AuthorizationServer(
    app,
    query_client=lambda cid: ClientObj(CLIENTS[cid]) if cid in CLIENTS else None,
    save_token=save_token
)
server.register_grant(AuthorizationCodeGrant, [CodeChallenge(required=False)])
server.register_grant(RefreshTokenGrant)

@app.route("/setup-mfa")
def setup_mfa():
    username = request.args.get("user", "rocio")
    user = USERS.get(username, USERS["rocio"])
    uri = pyotp.TOTP(user["totp_secret"]).provisioning_uri(
        f"{user['username']}@hospital.es", issuer_name="Insegus"
    )
    img = qrcode.make(uri)
    buf = BytesIO()
    img.save(buf, format="PNG")
    qr_b64 = base64.b64encode(buf.getvalue()).decode()
    return render_template("setup_mfa.html", qr_b64=qr_b64, db_seed=user["totp_secret"], username=user["username"])

@app.route("/oauth/authorize", methods=["GET", "POST"])
def authorize():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username", "")
    password = request.form.get("password", "")
    totp_code = request.form.get("totp", "")
    user = USERS.get(username)

    if not user:
        return render_template("login.html", error="El usuario especificado no existe en la base de datos"), 401

    if not pwd_context.verify(password, user["password_hash"]):
        return render_template("login.html", error="Contraseña incorrecta para este usuario"), 401

    totp = pyotp.TOTP(user["totp_secret"])
    if not totp.verify(totp_code, valid_window=1):
        return render_template("login.html", error="Código FreeOTP inválido"), 401

    return server.create_authorization_response(grant_user=user)

@app.route("/oauth/token", methods=["POST"])
def issue_token():
    return server.create_token_response()

@app.route("/.well-known/jwt-key")
def jwt_key():
    return jsonify({"key": app.config["OAUTH2_JWT_KEY"], "alg": app.config["OAUTH2_JWT_ALG"]})

if __name__ == "__main__":
    app.run(port=8000, debug=True)
