import socketserver
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse


def wait_for_authorization_code():
    """
    Returns a generator that yields twice:
        - first, the sucessfully bound port - use this to construct `redirect_uri`
        - second, the actual authorization code

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
        print("serving at port", port)
        server.handle_request()
        yield port
        google_auth_response = server.google_auth_response

    # auth response is in the form of GET params, so let's parse them:
    params = parse_qs(urlparse(google_auth_response).query)
    if "code" in params:
        yield params["code"][0]
    else:
        raise Exception(f"Failed to get authorization code: {params['error']}")
