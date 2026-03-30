"""
Renewal Reminder System for MSP Module.
Handles daily reminders for contract renewals.
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from exchange.logger import get_logger
from .contracts import ContractManager

_logger = get_logger()


class RenewalReminder:
    """Daily reminder system for contract renewals.
    
    Integrates with:
    - Exchange email (via exchange module)
    - Cron scheduling (via OpenClaw cron)
    """
    
    def __init__(
        self,
        db_path: Optional[Path] = None,
        log_path: Optional[Path] = None
    ):
        """Initialize reminder system.
        
        Args:
            db_path: Optional custom database path
            log_path: Optional custom renewal log path
        """
        self.contract_manager = ContractManager(db_path, log_path)
    
    def run_daily_check(
        self,
        send_email: bool = True,
        recipient: Optional[str] = None
    ) -> Dict[str, Any]:
        """Run daily check for contract renewals.
        
        This is the main entry point for cron jobs.
        
        Args:
            send_email: Whether to send email notification
            recipient: Email recipient (default: from env EXCHANGE_EMAIL)
        
        Returns:
            Summary of check results
        """
        summary = self.contract_manager.get_renewal_summary()
        
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "clients_needing_renewal": summary["count"],
            "clients": summary["clients"],
            "email_sent": False
        }
        
        if summary["count"] > 0 and send_email:
            # Get recipient from env or default
            if not recipient:
                recipient = os.environ.get("MSP_REMINDER_EMAIL")
            
            if recipient:
                email = self.contract_manager.generate_reminder_email(recipient)
                
                # Try to send email via Exchange module
                try:
                    from exchange.mail import send_email as exchange_send
                    
                    sent = exchange_send(
                        to=recipient,
                        subject=email["subject"],
                        body=email["body"]
                    )
                    result["email_sent"] = sent
                    result["email_subject"] = email["subject"]
                except Exception as e:
                    _logger.error(f"Failed to send email: {e}")
                    result["error"] = str(e)
            else:
                _logger.warning("No recipient email configured")
                result["error"] = "No recipient email configured"
        
        return result
    
    def add_client_for_renewal(
        self,
        client_id: str,
        renewal_date: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add client to renewal tracking.
        
        Convenience method that wraps ContractManager.
        
        Args:
            client_id: Client ID
            renewal_date: Optional renewal deadline
            notes: Optional notes
        
        Returns:
            Result dictionary
        """
        client = self.contract_manager.set_renewal_required(
            client_id=client_id,
            renewal_date=renewal_date,
            notes=notes
        )
        
        if client:
            return {"ok": True, "client": client}
        else:
            return {"ok": False, "error": f"Client {client_id} not found"}
    
    def resolve_renewal(
        self,
        client_id: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Mark client renewal as resolved.
        
        Args:
            client_id: Client ID
            notes: Optional notes about resolution
        
        Returns:
            Result dictionary
        """
        client = self.contract_manager.set_contract_valid(
            client_id=client_id,
            notes=notes
        )
        
        if client:
            return {"ok": True, "client": client}
        else:
            return {"ok": True, "error": f"Client {client_id} not found"}
    
    def get_status(self) -> Dict[str, Any]:
        """Get current reminder system status.
        
        Returns:
            Status dictionary
        """
        summary = self.contract_manager.get_renewal_summary()
        history = self.contract_manager.get_reminder_history(limit=5)
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "clients_needing_renewal": summary["count"],
            "recent_reminders": len(history),
            "last_reminder": history[-1] if history else None
        }


def main():
    """CLI entry point for reminders module."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Contract Renewal Reminders")
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # Run daily check (for cron)
    check_parser = subparsers.add_parser("check", help="Run daily renewal check")
    check_parser.add_argument("--no-email", action="store_true", help="Skip email")
    check_parser.add_argument("--to", help="Email recipient")
    
    # Status
    subparsers.add_parser("status", help="Get reminder system status")
    
    # Add client for renewal
    add_parser = subparsers.add_parser("add", help="Add client for renewal tracking")
    add_parser.add_argument("--id", required=True, help="Client ID")
    add_parser.add_argument("--date", help="Renewal deadline")
    add_parser.add_argument("--notes", help="Notes")
    
    # Resolve renewal
    resolve_parser = subparsers.add_parser("resolve", help="Mark renewal resolved")
    resolve_parser.add_argument("--id", required=True, help="Client ID")
    resolve_parser.add_argument("--notes", help="Resolution notes")
    
    args = parser.parse_args()
    reminder = RenewalReminder()
    
    if args.command == "check":
        result = reminder.run_daily_check(
            send_email=not args.no_email,
            recipient=args.to
        )
        print(json.dumps(result, indent=2))
    
    elif args.command == "status":
        status = reminder.get_status()
        print(json.dumps({"ok": True, **status}, indent=2))
    
    elif args.command == "add":
        result = reminder.add_client_for_renewal(
            client_id=args.id,
            renewal_date=args.date,
            notes=args.notes
        )
        print(json.dumps(result, indent=2))
    
    elif args.command == "resolve":
        result = reminder.resolve_renewal(client_id=args.id, notes=args.notes)
        print(json.dumps(result, indent=2))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()