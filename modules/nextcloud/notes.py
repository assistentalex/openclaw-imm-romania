"""Nextcloud Notes API client."""

import argparse
import json
import os
import sys
import urllib.parse
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import requests
    from requests.auth import HTTPBasicAuth
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    requests = None  # type: ignore
    HTTPBasicAuth = None  # type: ignore


class NotesClient:
    """Client for Nextcloud Notes API."""
    
    def __init__(self) -> None:
        self.url = os.environ.get("NEXTCLOUD_URL", "").rstrip("/")
        self.username = os.environ.get("NEXTCLOUD_USERNAME", "")
        self.app_password = os.environ.get("NEXTCLOUD_APP_PASSWORD", "")
        
        if not all([self.url, self.username, self.app_password]):
            raise EnvironmentError("Missing NEXTCLOUD_URL, NEXTCLOUD_USERNAME, or NEXTCLOUD_APP_PASSWORD")
        
        self.auth = HTTPBasicAuth(self.username, self.app_password)
        self.headers = {
            "OCS-APIRequest": "true",
            "Accept": "application/json",
        }
    
    def _request(self, method: str, endpoint: str, **kwargs: Any) -> Optional[Dict[str, Any]]:
        """Send request to Notes API."""
        url = f"{self.url}/index.php/apps/notes/api/v1/{endpoint}"
        try:
            response = requests.request(method, url, auth=self.auth, headers=self.headers, timeout=30, **kwargs)
            if response.status_code in {200, 201}:
                return response.json()
            return {"ok": False, "error": f"HTTP {response.status_code}", "message": response.text[:200]}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    def list_notes(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all notes."""
        params: Dict[str, Any] = {}
        if category:
            params["category"] = category
        result = self._request("GET", "notes", params=params)
        if isinstance(result, list):
            return result
        return []
    
    def get_note(self, note_id: int) -> Dict[str, Any]:
        """Get note by ID."""
        result = self._request("GET", f"notes/{note_id}")
        return result if isinstance(result, dict) else {"ok": False, "error": "Note not found"}
    
    def create_note(self, title: str, content: str, category: Optional[str] = None) -> Dict[str, Any]:
        """Create new note."""
        data = {"title": title, "content": content}
        if category:
            data["category"] = category
        result = self._request("POST", "notes", json=data)
        return result if isinstance(result, dict) else {"ok": False, "error": "Failed to create note"}
    
    def update_note(self, note_id: int, title: Optional[str] = None, content: Optional[str] = None, category: Optional[str] = None) -> Dict[str, Any]:
        """Update note."""
        data: Dict[str, Any] = {}
        if title is not None:
            data["title"] = title
        if content is not None:
            data["content"] = content
        if category is not None:
            data["category"] = category
        result = self._request("PUT", f"notes/{note_id}", json=data)
        return result if isinstance(result, dict) else {"ok": False, "error": "Failed to update note"}
    
    def delete_note(self, note_id: int) -> Dict[str, Any]:
        """Delete note."""
        result = self._request("DELETE", f"notes/{note_id}")
        return result if isinstance(result, dict) else {"ok": False, "error": "Failed to delete note"}


def _out(data: Dict[str, Any]) -> None:
    """Output JSON."""
    print(json.dumps(data, indent=2, default=str))
    sys.exit(0)


def _die(message: str) -> None:
    """Output error JSON."""
    print(json.dumps({"ok": False, "error": message}, indent=2))
    sys.exit(1)


def cmd_list(args: argparse.Namespace) -> None:
    """List notes."""
    if not HAS_REQUESTS:
        _die("requests library required. Install: pip install requests")
    
    client = NotesClient()
    notes = client.list_notes(category=getattr(args, 'category', None))
    
    _out({"ok": True, "count": len(notes), "notes": [
        {
            "id": n.get("id"),
            "title": n.get("title"),
            "category": n.get("category"),
            "modified": n.get("modified"),
        } for n in notes
    ]})


def cmd_get(args: argparse.Namespace) -> None:
    """Get note."""
    if not HAS_REQUESTS:
        _die("requests library required")
    
    client = NotesClient()
    note = client.get_note(args.id)
    
    if note.get("ok") is False:
        _die(note.get("error", "Note not found"))
    
    _out({"ok": True, "note": {
        "id": note.get("id"),
        "title": note.get("title"),
        "content": note.get("content"),
        "category": note.get("category"),
        "modified": note.get("modified"),
    }})


def cmd_create(args: argparse.Namespace) -> None:
    """Create note."""
    if not HAS_REQUESTS:
        _die("requests library required")
    
    client = NotesClient()
    note = client.create_note(args.title, args.content or "", category=getattr(args, 'category', None))
    
    if note.get("ok") is False:
        _die(note.get("error", "Failed to create note"))
    
    _out({"ok": True, "message": "Note created", "note": {
        "id": note.get("id"),
        "title": note.get("title"),
        "category": note.get("category"),
    }})


def cmd_update(args: argparse.Namespace) -> None:
    """Update note."""
    if not HAS_REQUESTS:
        _die("requests library required")
    
    client = NotesClient()
    note = client.update_note(
        args.id,
        title=getattr(args, 'title', None),
        content=getattr(args, 'content', None),
        category=getattr(args, 'category', None),
    )
    
    if note.get("ok") is False:
        _die(note.get("error", "Failed to update note"))
    
    _out({"ok": True, "message": "Note updated", "note": {
        "id": note.get("id"),
        "title": note.get("title"),
        "category": note.get("category"),
    }})


def cmd_delete(args: argparse.Namespace) -> None:
    """Delete note."""
    if not HAS_REQUESTS:
        _die("requests library required")
    
    client = NotesClient()
    result = client.delete_note(args.id)
    
    if isinstance(result, dict) and result.get("ok") is False:
        _die(result.get("error", "Failed to delete note"))
    
    _out({"ok": True, "message": "Note deleted", "id": args.id})


def setup_parser(subparsers: Any) -> None:
    """Setup notes subparser for Nextcloud."""
    parser = subparsers.add_parser("notes", help="Nextcloud Notes (CRUD)")
    sub = parser.add_subparsers(dest="notes_command")
    
    p_list = sub.add_parser("list", help="List notes")
    p_list.add_argument("--category", help="Filter by category")
    p_list.set_defaults(func=cmd_list)
    
    p_get = sub.add_parser("get", help="Get note")
    p_get.add_argument("--id", required=True, type=int, help="Note ID")
    p_get.set_defaults(func=cmd_get)
    
    p_create = sub.add_parser("create", help="Create note")
    p_create.add_argument("--title", required=True, help="Note title")
    p_create.add_argument("--content", help="Note content")
    p_create.add_argument("--category", help="Note category")
    p_create.set_defaults(func=cmd_create)
    
    p_update = sub.add_parser("update", help="Update note")
    p_update.add_argument("--id", required=True, type=int, help="Note ID")
    p_update.add_argument("--title", help="New title")
    p_update.add_argument("--content", help="New content")
    p_update.add_argument("--category", help="New category")
    p_update.set_defaults(func=cmd_update)
    
    p_delete = sub.add_parser("delete", help="Delete note")
    p_delete.add_argument("--id", required=True, type=int, help="Note ID")
    p_delete.set_defaults(func=cmd_delete)
