import socketserver
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse


def wait_for_authorization_code(port=8000):
    google_auth_response = None

    # Prepare a quick http server that serves one GET request
    class OneTimeHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(
                b"Sucesssfully authorized. You can close this browser tab now."
            )
            self.server.google_auth_response = self.path

    with socketserver.TCPServer(("", port), OneTimeHandler) as server:
        print("serving at port", port)
        server.handle_request()
        google_auth_response = server.google_auth_response

    params = parse_qs(urlparse(google_auth_response).query)
    if "code" in params:
        return params["code"][0]
    else:
        raise Exception(f"Failed to get authorization code: {params['error']}")


print(f"got code {wait_for_authorization_code()}")
