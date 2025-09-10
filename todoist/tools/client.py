import httpx
from typing import Any, Dict, List, Optional, Union, cast

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