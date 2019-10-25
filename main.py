from google import wait_for_authorization_code, build_oauth_url, get_initial_tokens

handler = wait_for_authorization_code()
redirect_port = next(handler)
oauth_url = build_oauth_url(redirect_port)
print(oauth_url)
authorization_code = next(handler)
tokens = get_initial_tokens(authorization_code, redirect_port)
