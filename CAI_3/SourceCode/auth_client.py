import os
os.environ["AUTHLIB_INSECURE_TRANSPORT"] = "1"

import time
import secrets
import requests
from flask import Flask, redirect, url_for, request, jsonify, make_response, render_template
from authlib.integrations.flask_client import OAuth
from authlib.oauth2.rfc6750 import BearerTokenValidator
from authlib.oauth2.rfc6749.util import scope_to_list
from authlib.integrations.flask_oauth2 import ResourceProtector
from authlib.jose import jwt, JoseError

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

oauth = OAuth(app)
oauth.register(
    name="hospital_insegus",
    client_id="hospital-web",
    authorize_url="http://localhost:8000/oauth/authorize",
    access_token_url="http://localhost:8000/oauth/token",
    client_kwargs={
        "scope": "paciente:leer medico:escribir",
        "token_endpoint_auth_method": "none"
    }
)

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
        cfg = requests.get("http://localhost:8000/.well-known/jwt-key").json()
        try:
            claims = jwt.decode(token_string, cfg["key"])
            claims.validate()
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

@app.route("/")
def index():
    return render_template("portal.html")

@app.route("/login")
def login():
    redirect_uri = url_for("callback", _external=True)
    return oauth.hospital_insegus.authorize_redirect(redirect_uri)

@app.route("/callback")
def callback():
    token = oauth.hospital_insegus.authorize_access_token()
    resp = make_response(redirect("/"))
    resp.set_cookie(
        "access_token",
        token["access_token"],
        httponly=False,
        samesite="Lax"
    )
    return resp

@app.route("/logout")
def logout():
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
        "datos": "Historial clínico confidencial (Grupo O+)"
    })

@app.route("/api/historial", methods=["POST"])
@require_oauth()
def post_historial():
    datos = request.get_json(silent=True) or {}
    diagnostico = datos.get("diagnostico", "")
    return jsonify({
        "status": "ok",
        "mensaje": f"Historial médico actualizado con: {diagnostico}",
    })

if __name__ == "__main__":
    app.run(port=8001, debug=True)
