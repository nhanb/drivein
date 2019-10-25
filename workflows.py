from google import wait_for_authorization_code, build_oauth_url, get_initial_tokens
from rclone import write_config, mount, kill


def google_auth():
    handler = wait_for_authorization_code()
    redirect_port = next(handler)
    oauth_url = build_oauth_url(redirect_port)
    print(oauth_url)
    authorization_code = next(handler)
    tokens = get_initial_tokens(authorization_code, redirect_port)
    return tokens


def launch_rclone(refresh_token):
    write_config(refresh_token)
    rclone_process = mount()
    return rclone_process
