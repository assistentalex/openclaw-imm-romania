"""
Utility functions for Exchange Mailbox skill.
Common functions used across all modules.
"""

import json
import sys
import os
from datetime import datetime
from typing import List, Optional, Dict, Any


def out(data: Dict[str, Any]) -> None:
    """Output JSON to stdout and exit successfully."""
    print(json.dumps(data, indent=2, default=str))
    sys.exit(0)


def die(message: str) -> None:
    """Output error JSON to stdout and exit with error code."""
    print(json.dumps({"ok": False, "error": message}, indent=2))
    sys.exit(1)


def parse_datetime(date_str: Optional[str]) -> Optional[datetime]:
    """
    Parse various date formats into datetime object.
    
    Supports:
    - ISO format: 2024-01-15T10:30:00
    - Date only: 2024-01-15
    - Relative: +1d, +7d, -1d (days from now)
    
    Returns None if input is None or empty.
    """
    if not date_str:
        return None
    
    date_str = date_str.strip()
    
    # Handle relative dates
    if date_str.startswith("+") or date_str.startswith("-"):
        try:
            # Parse +1d, -7d, etc.
            if date_str.startswith("+"):
                days = int(date_str[1:-1])
            else:
                days = int(date_str[:-1]) * -1
            
            return datetime.now() + __import__('datetime').timedelta(days=days)
        except (ValueError, IndexError):
            pass
    
    # Try various date formats
    formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    # Try parsing as timestamp
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        pass
    
    die(f"Invalid date format: {date_str}. Use YYYY-MM-DD or YYYY-MM-DD HH:MM")


def parse_recipients(recipients_str: Optional[str]) -> List[str]:
    """
    Parse comma or semicolon separated email addresses.
    
    Examples:
    - "user@example.com"
    - "user1@example.com, user2@example.com"
    - "user1@example.com; user2@example.com"
    
    Returns empty list if input is None or empty.
    """
    if not recipients_str:
        return []
    
    # Split by comma or semicolon
    recipients = []
    for r in recipients_str.replace(";", ",").split(","):
        r = r.strip()
        if r and "@" in r:
            recipients.append(r)
    
    return recipients


def format_datetime(dt: Optional[datetime]) -> Optional[str]:
    """Format datetime for display."""
    if not dt:
        return None
    return dt.strftime("%Y-%m-%d %H:%M")


def truncate(text: Optional[str], max_length: int = 100) -> Optional[str]:
    """Truncate text with ellipsis."""
    if not text:
        return None
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def validate_email(email: str) -> bool:
    """Basic email validation."""
    if not email:
        return False
    return "@" in email and "." in email.split("@")[1]


def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get environment variable with optional default."""
    return os.environ.get(key, default)


def mask_email(email: str) -> str:
    """Mask email for logging (show first char and domain)."""
    if not email or "@" not in email:
        return "***"
    local, domain = email.split("@", 1)
    return f"{local[0]}***@{domain}"