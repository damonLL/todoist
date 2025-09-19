import os
import secrets
import urllib.parse
from typing import List, Tuple

TODOIST_AUTHORIZE_URL = "https://todoist.com/oauth/authorize"

def generate_state() -> str:
    return secrets.token_urlsafe(32)

def build_authorize_url(client_id: str, redirect_uri: str, scopes: List[str], state: str) -> str:
    params = {
        "client_id": client_id,
        "scope": " ".join(scopes),
        "state": state,
        "redirect_uri": redirect_uri,
    }
    return f"{TODOIST_AUTHORIZE_URL}?{urllib.parse.urlencode(params)}"

def get_authorize_url_from_env(default_scopes: List[str] | None = None) -> Tuple[str, str]:
    scopes = default_scopes or ["data:read_write"]
    client_id = os.environ["TODOIST_CLIENT_ID"]
    redirect_uri = os.environ.get(
        "TODOIST_REDIRECT_URI",
        "https://cloud.arcade.dev/api/v1/oauth/f4c6b_ap_6j1OmuOazcvL/callback",
    )
    state = generate_state()
    return build_authorize_url(client_id, redirect_uri, scopes, state), state

STATE_FILE = os.environ.get("TODOIST_OAUTH_STATE_PATH", ".todoist_oauth_state")

def persist_state(state: str) -> None:
    with open(STATE_FILE, "w") as f:
        f.write(state)

def read_state() -> str | None:
    try:
        with open(STATE_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None