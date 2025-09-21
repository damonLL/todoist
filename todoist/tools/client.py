import httpx
from typing import Any, Dict, List, Optional, Union, cast
import os
from arcade_tdk import ToolContext
from arcade_tdk.errors import ToolExecutionError

BASE = "https://api.todoist.com/rest/v2"

class TodoistClient:
    def __init__(self, token: str) -> None:
        self.headers = {"Authorization": f"Bearer {token}"}

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        with httpx.Client(timeout=15) as c:
            r = c.get(f"{BASE}{path}", headers=self.headers, params=params or {})
            r.raise_for_status()
            return cast(Union[List[Dict[str, Any]], Dict[str, Any]], r.json())

    def post(self, path: str, json: Optional[Dict[str, Any]] = None) -> Union[bool, Dict[str, Any]]:
        with httpx.Client(timeout=15) as c:
            r = c.post(f"{BASE}{path}", headers=self.headers, json=json)
            if r.status_code == 204:
                return True
            r.raise_for_status()
            # Some POSTs (like create task) return JSON
            return cast(Dict[str, Any], r.json())


def resolve_todoist_token(ctx: ToolContext) -> str:
    """Return OAuth token if available, else fall back to TODOIST_API_TOKEN.

    Raises ToolExecutionError if neither is available.
    """
    oauth_token = ctx.get_auth_token_or_empty() if ctx else ""
    env_token = os.getenv("TODOIST_API_TOKEN", "")
    token = oauth_token or env_token
    if not token:
        raise ToolExecutionError(
            message="Todoist token missing",
            developer_message=(
                "No Todoist token available. Locally, export TODOIST_API_TOKEN. "
                "In Arcade, authorize via OAuth for this tool."
            ),
        )
    return token

