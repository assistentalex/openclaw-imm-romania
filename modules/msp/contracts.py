"""
Contract Management for MSP Module.
Track contract status, renewal dates, and generate reminders.
"""

import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from exchange.logger import get_logger
from .clients import ClientDB

# Default renewal log path
DEFAULT_RENEWAL_LOG = Path(__file__).parent.parent.parent / "data" / "contract-renewals.jsonl"

_logger = get_logger()


class ContractManager:
    """Manage contract renewals and tracking.
    
    Provides functionality for:
    - Tracking contract renewal dates
    - Generating renewal reminders
    - Logging reminder history
    """
    
    def __init__(
        self,
        db_path: Optional[Path] = None,
        log_path: Optional[Path] = None
    ):
        """Initialize contract manager.
        
        Args:
            db_path: Optional custom database path
            log_path: Optional custom renewal log path
        """
        self.client_db = ClientDB(db_path)
        self.log_path = log_path or DEFAULT_RENEWAL_LOG
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _log_renewal(
        self,
        clients: List[str],
        reminder_type: str = "daily",
        message: Optional[str] = None
    ) -> bool:
        """Log renewal reminder.
        
        Args:
            clients: List of client names needing renewal
            reminder_type: Type of reminder (daily, weekly, monthly)
            message: Optional custom message
        
        Returns:
            True if logged successfully
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": reminder_type,
            "clients": clients,
            "message": message or "Contract renewal reminder"
        }
        
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
            return True
        except IOError as e:
            _logger.error(f"Failed to log renewal: {e}")
            return False
    
    def set_renewal_required(
        self,
        client_id: str,
        renewal_date: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Mark client as needing contract renewal.
        
        Args:
            client_id: Client ID
            renewal_date: Optional renewal deadline
            notes: Optional notes about renewal
        
        Returns:
            Updated client or None
        """
        return self.client_db.update_client(
            client_id=client_id,
            contract_status="renewal_required",
            contract_renewal_date=renewal_date,
            contract_notes=notes
        )
    
    def set_contract_valid(
        self,
        client_id: str,
        notes: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Mark client contract as valid (renewed).
        
        Args:
            client_id: Client ID
            notes: Optional notes about renewal
        
        Returns:
            Updated client or None
        """
        return self.client_db.update_client(
            client_id=client_id,
            contract_status="valid",
            contract_renewal_date=None,
            contract_notes=notes or "Contract renewed"
        )
    
    def get_renewal_clients(self) -> List[Dict[str, Any]]:
        """Get all clients needing renewal.
        
        Returns:
            List of clients with contract_status == 'renewal_required'
        """
        return self.client_db.get_clients_for_renewal()
    
    def get_renewal_summary(self) -> Dict[str, Any]:
        """Get summary of clients needing renewal.
        
        Returns:
            Summary with count and client list
        """
        clients = self.get_renewal_clients()
        
        return {
            "count": len(clients),
            "clients": [
                {
                    "id": c["id"],
                    "name": c["name"],
                    "industry": c.get("industry", "Unknown"),
                    "contract_notes": c.get("contract_notes"),
                    "contract_renewal_date": c.get("contract_renewal_date")
                }
                for c in clients
            ],
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def generate_reminder_email(
        self,
        recipient: str
    ) -> Dict[str, Any]:
        """Generate email content for renewal reminder.
        
        Args:
            recipient: Email recipient
        
        Returns:
            Email data with subject and body
        """
        summary = self.get_renewal_summary()
        
        if summary["count"] == 0:
            return {
                "subject": "✅ Contract Renewal Check - All Contracts Valid",
                "body": "All client contracts are up to date. No renewals needed.",
                "has_renewals": False
            }
        
        client_list = "\n".join([
            f"  - {c['name']} ({c['industry']})"
            + (f" - {c['contract_notes']}" if c.get('contract_notes') else "")
            for c in summary["clients"]
        ])
        
        subject = f"⚠️ Contract Renewal Required - {summary['count']} Client(s)"
        
        body = f"""Contract Renewal Reminder
========================

The following client(s) require IT contract renewal:

{client_list}

Action Required:
- Contact each client for contract renewal discussion
- Update contract status after renewal is complete
- Use: imm-romania msp contracts resolve --id CLIENT_ID

---
Generated: {summary['generated_at']}
"""
        
        # Log this reminder
        self._log_renewal(
            clients=[c["name"] for c in summary["clients"]],
            reminder_type="daily",
            message=f"Sent reminder to {recipient}"
        )
        
        return {
            "subject": subject,
            "body": body,
            "has_renewals": True,
            "client_count": summary["count"]
        }
    
    def get_reminder_history(
        self,
        limit: int = 30
    ) -> List[Dict[str, Any]]:
        """Get history of renewal reminders.
        
        Args:
            limit: Maximum number of entries to return
        
        Returns:
            List of reminder log entries
        """
        if not self.log_path.exists():
            return []
        
        entries = []
        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        entries.append(json.loads(line.strip()))
                    except json.JSONDecodeError:
                        continue
        except IOError:
            pass
        
        return entries[-limit:]
    
    def mark_client_contacted(
        self,
        client_id: str,
        notes: str
    ) -> Optional[Dict[str, Any]]:
        """Mark that client has been contacted about renewal.
        
        Args:
            client_id: Client ID
            notes: Notes about contact
        
        Returns:
            Updated client or None
        """
        return self.client_db.add_note(
            client_id=client_id,
            note=f"[CONTACTED] {notes}"
        )


def main():
    """CLI entry point for contracts module."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Contract Management")
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # List renewal clients
    subparsers.add_parser("list", help="List clients needing renewal")
    
    # Summary
    subparsers.add_parser("summary", help="Get renewal summary")
    
    # Set renewal required
    set_parser = subparsers.add_parser("set-required", help="Mark client for renewal")
    set_parser.add_argument("--id", required=True, help="Client ID")
    set_parser.add_argument("--date", help="Renewal deadline")
    set_parser.add_argument("--notes", help="Notes")
    
    # Resolve (mark as renewed)
    resolve_parser = subparsers.add_parser("resolve", help="Mark contract as renewed")
    resolve_parser.add_argument("--id", required=True, help="Client ID")
    resolve_parser.add_argument("--notes", help="Notes")
    
    # Generate email
    email_parser = subparsers.add_parser("email", help="Generate reminder email")
    email_parser.add_argument("--to", required=True, help="Recipient email")
    
    # History
    history_parser = subparsers.add_parser("history", help="Get reminder history")
    history_parser.add_argument("--limit", type=int, default=30, help="Max entries")
    
    # Mark contacted
    contact_parser = subparsers.add_parser("contacted", help="Mark client contacted")
    contact_parser.add_argument("--id", required=True, help="Client ID")
    contact_parser.add_argument("--notes", required=True, help="Contact notes")
    
    args = parser.parse_args()
    manager = ContractManager()
    
    if args.command == "list":
        clients = manager.get_renewal_clients()
        print(json.dumps({"ok": True, "count": len(clients), "clients": clients}, indent=2))
    
    elif args.command == "summary":
        summary = manager.get_renewal_summary()
        print(json.dumps({"ok": True, **summary}, indent=2))
    
    elif args.command == "set-required":
        client = manager.set_renewal_required(
            client_id=args.id,
            renewal_date=args.date,
            notes=args.notes
        )
        if client:
            print(json.dumps({"ok": True, "client": client}, indent=2))
        else:
            print(json.dumps({"ok": False, "error": f"Client {args.id} not found"}, indent=2))
    
    elif args.command == "resolve":
        client = manager.set_contract_valid(client_id=args.id, notes=args.notes)
        if client:
            print(json.dumps({"ok": True, "client": client}, indent=2))
        else:
            print(json.dumps({"ok": False, "error": f"Client {args.id} not found"}, indent=2))
    
    elif args.command == "email":
        email = manager.generate_reminder_email(recipient=args.to)
        print(json.dumps({"ok": True, **email}, indent=2))
    
    elif args.command == "history":
        history = manager.get_reminder_history(limit=args.limit)
        print(json.dumps({"ok": True, "count": len(history), "history": history}, indent=2))
    
    elif args.command == "contacted":
        client = manager.mark_client_contacted(client_id=args.id, notes=args.notes)
        if client:
            print(json.dumps({"ok": True, "client": client}, indent=2))
        else:
            print(json.dumps({"ok": False, "error": f"Client {args.id} not found"}, indent=2))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()