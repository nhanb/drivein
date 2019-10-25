import json
import subprocess
import os
import signal
from google import CLIENT_ID, CLIENT_SECRET

REMOTE_NAME = "drivethru"


def produce_config(refresh_token):
    token = json.dumps(
        {
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            # letting rclone fetch new access token for now
            "access_token": "sum_ting_wong",
            "expiry": "2000-01-01T00:00:00+00:00",
        }
    )

    return f"""\
[{REMOTE_NAME}]
type = drive
client_id = {CLIENT_ID}
client_secret = {CLIENT_SECRET}
scope = drive
token = {token}
"""


def write_config(refresh_token, filename="rclone.conf"):
    content = produce_config(refresh_token)
    with open(filename, "w") as f:
        f.write(content)


def mount(drive_letter="G") -> subprocess.Popen:
    """
    Spawn a parallel subprocess that mounts the Google Drive remote
    """
    return subprocess.Popen(
        f".\\rclone.exe mount {REMOTE_NAME}:/ {drive_letter}: --vfs-cache-mode writes --vfs-read-chunk-size 32M",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        # shell=True so I can send Ctrl+C event:
        # https://stackoverflow.com/a/26579101
        shell=True,
    )


def kill(subpr: subprocess.Popen):
    os.kill(subpr.pid, signal.CTRL_C_EVENT)
