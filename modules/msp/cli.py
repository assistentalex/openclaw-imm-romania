"""
MSP CLI Entry Point.
Unified command-line interface for MSP module.
"""

import argparse
import json
import sys
import os

# Add modules directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from exchange.logger import get_logger
from msp.clients import ClientDB
from msp.contracts import ContractManager
from msp.reminders import RenewalReminder

_logger = get_logger()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="MSP Manager - Managed Service Provider Client Management",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="module", help="Module")
    
    # ===== CLIENTS =====
    clients_parser = subparsers.add_parser("clients", help="Client management")
    clients_sub = clients_parser.add_subparsers(dest="command", help="Command")
    
    # clients init
    clients_sub.add_parser("init", help="Initialize empty database")
    
    # clients list
    clients_list = clients_sub.add_parser("list", help="List clients")
    clients_list.add_argument("--status", help="Filter by status")
    clients_list.add_argument("--contract-status", help="Filter by contract status")
    clients_list.add_argument("--industry", help="Filter by industry")
    
    # clients add
    clients_add = clients_sub.add_parser("add", help="Add client")
    clients_add.add_argument("--name", required=True, help="Client name")
    clients_add.add_argument("--industry", default="Unknown", help="Industry")
    clients_add.add_argument("--status", default="active", help="Client status")
    clients_add.add_argument("--contract-status", default="valid", help="Contract status")
    clients_add.add_argument("--notes", help="Notes")
    
    # clients get
    clients_get = clients_sub.add_parser("get", help="Get client")
    clients_get.add_argument("--id", help="Client ID")
    clients_get.add_argument("--name", help="Client name (alternative to ID)")
    
    # clients update
    clients_update = clients_sub.add_parser("update", help="Update client")
    clients_update.add_argument("--id", required=True, help="Client ID")
    clients_update.add_argument("--name", help="New name")
    clients_update.add_argument("--industry", help="New industry")
    clients_update.add_argument("--status", help="New status")
    clients_update.add_argument("--contract-status", help="New contract status")
    clients_update.add_argument("--contract-notes", help="Contract notes")
    
    # clients delete
    clients_delete = clients_sub.add_parser("delete", help="Delete client")
    clients_delete.add_argument("--id", required=True, help="Client ID")
    
    # clients export
    clients_sub.add_parser("export", help="Export clients as JSON")
    
    # clients contact
    clients_contact = clients_sub.add_parser("contact", help="Add contact to client")
    clients_contact.add_argument("--id", required=True, help="Client ID")
    clients_contact.add_argument("--name", required=True, help="Contact name")
    clients_contact.add_argument("--email", required=True, help="Contact email")
    clients_contact.add_argument("--role", help="Contact role")
    clients_contact.add_argument("--phone", help="Contact phone")
    clients_contact.add_argument("--primary", action="store_true", help="Set as primary contact")
    
    # clients asset
    clients_asset = clients_sub.add_parser("asset", help="Add asset to client")
    clients_asset.add_argument("--id", required=True, help="Client ID")
    clients_asset.add_argument("--type", required=True, help="Asset type (domain, server, license)")
    clients_asset.add_argument("--value", required=True, help="Asset value")
    clients_asset.add_argument("--notes", help="Notes")
    
    # ===== CONTRACTS =====
    contracts_parser = subparsers.add_parser("contracts", help="Contract management")
    contracts_sub = contracts_parser.add_subparsers(dest="command", help="Command")
    
    # contracts list
    contracts_sub.add_parser("list", help="List clients needing renewal")
    
    # contracts summary
    contracts_sub.add_parser("summary", help="Get renewal summary")
    
    # contracts set-required
    contracts_set = contracts_sub.add_parser("set-required", help="Mark client for renewal")
    contracts_set.add_argument("--id", required=True, help="Client ID")
    contracts_set.add_argument("--date", help="Renewal deadline")
    contracts_set.add_argument("--notes", help="Notes")
    
    # contracts resolve
    contracts_resolve = contracts_sub.add_parser("resolve", help="Mark contract renewed")
    contracts_resolve.add_argument("--id", required=True, help="Client ID")
    contracts_resolve.add_argument("--notes", help="Notes")
    
    # contracts email
    contracts_email = contracts_sub.add_parser("email", help="Generate reminder email")
    contracts_email.add_argument("--to", help="Recipient email (default: MSP_REMINDER_EMAIL)")
    
    # contracts history
    contracts_history = contracts_sub.add_parser("history", help="Get reminder history")
    contracts_history.add_argument("--limit", type=int, default=30, help="Max entries")
    
    # ===== REMINDERS =====
    reminders_parser = subparsers.add_parser("reminders", help="Daily reminders")
    reminders_sub = reminders_parser.add_subparsers(dest="command", help="Command")
    
    # reminders check (for cron)
    reminders_check = reminders_sub.add_parser("check", help="Run daily check")
    reminders_check.add_argument("--no-email", action="store_true", help="Skip email")
    reminders_check.add_argument("--to", help="Email recipient")
    
    # reminders status
    reminders_sub.add_parser("status", help="Get reminder status")
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.module:
        parser.print_help()
        return
    
    # Initialize modules
    client_db = ClientDB()
    contract_manager = ContractManager()
    reminder_system = RenewalReminder()
    
    # Handle commands
    if args.module == "clients":
        handle_clients(args, client_db)
    elif args.module == "contracts":
        handle_contracts(args, contract_manager)
    elif args.module == "reminders":
        handle_reminders(args, reminder_system)
    else:
        parser.print_help()


def handle_clients(args, client_db: ClientDB):
    """Handle clients commands."""
    
    if args.command == "init":
        client_db.init_db()
        print(json.dumps({"ok": True, "message": "Database initialized"}, indent=2))
    
    elif args.command == "list":
        clients = client_db.list_clients(
            status=args.status,
            contract_status=args.contract_status,
            industry=args.industry
        )
        print(json.dumps({"ok": True, "count": len(clients), "clients": clients}, indent=2))
    
    elif args.command == "add":
        client = client_db.add_client(
            name=args.name,
            industry=args.industry,
            status=args.status,
            contract_status=args.contract_status,
            notes=args.notes
        )
        print(json.dumps({"ok": True, "client": client}, indent=2))
    
    elif args.command == "get":
        if args.id:
            client = client_db.get_client(args.id)
        elif args.name:
            client = client_db.get_client_by_name(args.name)
        else:
            client = None
        
        if client:
            print(json.dumps({"ok": True, "client": client}, indent=2))
        else:
            print(json.dumps({"ok": False, "error": "Client not found"}, indent=2))
    
    elif args.command == "update":
        client = client_db.update_client(
            client_id=args.id,
            name=args.name,
            industry=args.industry,
            status=args.status,
            contract_status=args.contract_status,
            contract_notes=args.contract_notes
        )
        if client:
            print(json.dumps({"ok": True, "client": client}, indent=2))
        else:
            print(json.dumps({"ok": False, "error": f"Client {args.id} not found"}, indent=2))
    
    elif args.command == "delete":
        if client_db.delete_client(args.id):
            print(json.dumps({"ok": True, "message": f"Client {args.id} deleted"}, indent=2))
        else:
            print(json.dumps({"ok": False, "error": f"Client {args.id} not found"}, indent=2))
    
    elif args.command == "export":
        print(client_db.export_clients())
    
    elif args.command == "contact":
        client = client_db.add_contact(
            client_id=args.id,
            name=args.name,
            email=args.email,
            role=args.role,
            phone=args.phone,
            is_primary=args.primary
        )
        if client:
            print(json.dumps({"ok": True, "client": client}, indent=2))
        else:
            print(json.dumps({"ok": False, "error": f"Client {args.id} not found"}, indent=2))
    
    elif args.command == "asset":
        client = client_db.add_asset(
            client_id=args.id,
            asset_type=args.type,
            value=args.value,
            notes=args.notes
        )
        if client:
            print(json.dumps({"ok": True, "client": client}, indent=2))
        else:
            print(json.dumps({"ok": False, "error": f"Client {args.id} not found"}, indent=2))
    
    else:
        print(json.dumps({"ok": False, "error": "Unknown command"}, indent=2))


def handle_contracts(args, manager: ContractManager):
    """Handle contracts commands."""
    
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
        recipient = args.to or os.environ.get("MSP_REMINDER_EMAIL")
        if not recipient:
            print(json.dumps({"ok": False, "error": "No recipient email configured"}, indent=2))
            return
        
        email = manager.generate_reminder_email(recipient=recipient)
        print(json.dumps({"ok": True, **email}, indent=2))
    
    elif args.command == "history":
        history = manager.get_reminder_history(limit=args.limit)
        print(json.dumps({"ok": True, "count": len(history), "history": history}, indent=2))
    
    else:
        print(json.dumps({"ok": False, "error": "Unknown command"}, indent=2))


def handle_reminders(args, reminder: RenewalReminder):
    """Handle reminders commands."""
    
    if args.command == "check":
        result = reminder.run_daily_check(
            send_email=not args.no_email,
            recipient=args.to
        )
        print(json.dumps(result, indent=2))
    
    elif args.command == "status":
        status = reminder.get_status()
        print(json.dumps({"ok": True, **status}, indent=2))
    
    else:
        print(json.dumps({"ok": False, "error": "Unknown command"}, indent=2))


if __name__ == "__main__":
    main()