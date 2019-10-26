import socketserver
import uuid
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlencode, urlparse

import requests

CLIENT_ID = "164693485770-h07il8ktpsolga43oivh7hhg8hbgmais.apps.googleusercontent.com"
CLIENT_SECRET = "MhTtR6tzECYOi7DOGpNPlv2c"


def wait_for_authorization_code():
    """
    Returns a generator that yields twice:
        - first, the sucessfully bound port - use this to construct `redirect_uri`
        - second, the actual authorization code

    Example:
        handler = wait_for_authorization_code()
        port = next(handler)
        <give user oauth url>
        authorization_code = next(handler)  # will block here until user consents

    https://developers.google.com/identity/protocols/OAuth2InstalledApp#step-2:-send-a-request-to-googles-oauth-2.0-server
    """

    # Prepare a quick http server that serves one GET request
    class OneTimeHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(
                b"Sucesssfully authorized. You can close this browser tab now."
            )
            self.server.google_auth_response = self.path

    with socketserver.TCPServer(("", 0), OneTimeHandler) as server:
        port = server.socket.getsockname()[1]
        yield port
        print("serving at port", port)
        server.handle_request()
        google_auth_response = server.google_auth_response

    yield _get_code_from_response(google_auth_response)


def _get_code_from_response(google_auth_response):
    # auth response is in the form of GET params, so let's parse them:
    params = parse_qs(urlparse(google_auth_response).query)
    if "code" in params:
        return params["code"][0]
    else:
        raise Exception(f"Failed to get authorization code: {params['error']}")


def build_oauth_url(redirect_port):
    base_url = "https://accounts.google.com/o/oauth2/auth"
    params = {
        "access_type": "offline",
        "client_id": CLIENT_ID,
        "redirect_uri": f"http://127.0.0.1:{redirect_port}",
        "response_type": "code",
        "scope": "https://www.googleapis.com/auth/drive",
        "state": str(uuid.uuid4()),  # we probably don't need to use this?
    }
    return f"{base_url}?{urlencode(params)}"


def get_initial_tokens(authorization_code, redirect_port):
    endpoint = "https://www.googleapis.com/oauth2/v4/token"
    params = {
        "code": authorization_code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "redirect_uri": f"http://127.0.0.1:{redirect_port}",
    }
    resp = requests.post(endpoint, data=params)
    assert resp.status_code == 200, f"Failed to get initial tokens: {resp.text}"

    resp_json = resp.json()
    return {
        "refresh_token": resp_json["refresh_token"],
        "access_token": resp_json["access_token"],
        "expires_in": resp_json["expires_in"],
    }


def get_access_token(refresh_token):
    endpoint = "https://oauth2.googleapis.com/token"
    params = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }
    resp = requests.post(endpoint, data=params)
    assert resp.status_code == 200, "Failed to get access token"

    resp_json = resp.json()
    return {
        "access_token": resp_json["access_token"],
        "expires_in": resp_json["expires_in"],
    }
