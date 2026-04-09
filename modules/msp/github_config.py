"""
GitHub checker configuration helpers for MSP module.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_CONFIG_PATH = Path(__file__).parent.parent.parent / "data" / "msp-github-repos.json"
DEFAULT_STATE_PATH = Path(__file__).parent.parent.parent / "data" / "msp-github-releases-state.json"


def _normalize_repos(repos: Optional[List[str]]) -> List[str]:
    """Normalize and deduplicate owner/repo values."""
    if not repos:
        return []

    normalized: List[str] = []
    seen = set()
    for repo in repos:
        value = str(repo).strip()
        if not value or "/" not in value:
            continue
        if value in seen:
            continue
        seen.add(value)
        normalized.append(value)
    return normalized


def load_github_config(
    config_path: Optional[Path] = None,
    repo_overrides: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Load GitHub checker configuration.

    Priority:
    1. explicit repo overrides
    2. JSON config file
    3. MSP_GITHUB_REPOS env var (comma-separated)
    """
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH

    config: Dict[str, Any] = {
        "enabled": False,
        "recipient": os.environ.get("MSP_GITHUB_RECIPIENT"),
        "repos": [],
        "config_path": str(path),
        "state_path": str(DEFAULT_STATE_PATH),
    }

    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as handle:
                raw = json.load(handle)
            if isinstance(raw, dict):
                config["enabled"] = bool(raw.get("enabled", True))
                config["recipient"] = raw.get("recipient") or config["recipient"]
                config["state_path"] = str(raw.get("state_path") or DEFAULT_STATE_PATH)
                config["repos"] = _normalize_repos(raw.get("repos", []))
        except (json.JSONDecodeError, OSError):
            config["enabled"] = False
            config["error"] = f"Failed to load config from {path}"

    env_repos = os.environ.get("MSP_GITHUB_REPOS")
    if env_repos and not config["repos"]:
        config["repos"] = _normalize_repos(env_repos.split(","))
        config["enabled"] = True

    if repo_overrides:
        config["repos"] = _normalize_repos(repo_overrides)
        config["enabled"] = True

    if not config["repos"]:
        config["enabled"] = False

    return config
