import json
import subprocess
import os
import signal
from google import CLIENT_ID, CLIENT_SECRET

# FIXME: mount() and kill() are grossly Windows-specific

REMOTE_NAME = "DriveIn"


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


def mount(drive_letter="G", shell=False) -> subprocess.Popen:
    """
    Spawn a parallel subprocess that mounts the Google Drive remote
    """
    if shell:
        sub = subprocess.Popen(
            f".\\rclone.exe mount {REMOTE_NAME}:/ {drive_letter}: --vfs-cache-mode writes --vfs-read-chunk-size 32M",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            # shell=True so I can send Ctrl+C event:
            # https://stackoverflow.com/a/26579101
            shell=True,
        )
    else:
        sub = subprocess.Popen(
            [
                ".\\rclone.exe",
                "mount",
                f"{REMOTE_NAME}:/",
                f"{drive_letter}:",
                "--vfs-cache-mode",
                "writes",
                "--vfs-read-chunk-size",
                "32M",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    print(f"Spawned subprocess pid = {sub.pid}")


def kill():
    # yeeeesh
    os.system(f"taskkill /im rclone.exe /f")


def rclone_is_running():
    tasklist_result = subprocess.check_output(
        'tasklist /nh /fi "IMAGENAME eq rclone.exe"'
    ).decode()
    return "rclone.exe" in tasklist_result
