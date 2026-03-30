"""
MSP Client Database Management.
Generic client management for Managed Service Providers.
"""

import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import sys
import os

# Add modules directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from exchange.logger import get_logger

# Default database path
DEFAULT_DB_PATH = Path(__file__).parent.parent.parent / "data" / "msp-clients.json"

_logger = get_logger()


class ClientDB:
    """Client database management for MSPs.
    
    Provides CRUD operations for client records including
    contacts, assets, and contract information.
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize client database.
        
        Args:
            db_path: Optional custom database path
        """
        self.db_path = db_path or DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _load(self) -> Dict[str, Any]:
        """Load database from file.
        
        Returns:
            Database dictionary with schema_version and clients
        """
        if not self.db_path.exists():
            return {"schema_version": "1.0.0", "clients": []}
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            _logger.error(f"Failed to load database: {e}")
            return {"schema_version": "1.0.0", "clients": []}
    
    def _save(self, data: Dict[str, Any]) -> bool:
        """Save database to file.
        
        Args:
            data: Database dictionary to save
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
            return True
        except IOError as e:
            _logger.error(f"Failed to save database: {e}")
            return False
    
    def _generate_id(self, data: Dict[str, Any]) -> str:
        """Generate next client ID.
        
        Args:
            data: Database dictionary
        
        Returns:
            New client ID (e.g., msp_001)
        """
        existing_ids = [c["id"] for c in data["clients"] if "id" in c]
        if not existing_ids:
            return "msp_001"
        
        # Extract numbers and find max
        max_num = 0
        for id_str in existing_ids:
            try:
                num = int(id_str.split("_")[1])
                max_num = max(max_num, num)
            except (IndexError, ValueError):
                continue
        
        return f"msp_{max_num + 1:03d}"
    
    def init_db(self) -> Dict[str, Any]:
        """Initialize empty database.
        
        Creates an empty database structure.
        
        Returns:
            Empty database structure
        """
        data = {"schema_version": "1.0.0", "clients": []}
        if self._save(data):
            _logger.info(f"Initialized empty database at {self.db_path}")
        return data
    
    def list_clients(
        self,
        status: Optional[str] = None,
        contract_status: Optional[str] = None,
        industry: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List all clients with optional filters.
        
        Args:
            status: Filter by status (active, inactive, prospect)
            contract_status: Filter by contract status
            industry: Filter by industry
        
        Returns:
            List of client dictionaries
        """
        data = self._load()
        clients = data["clients"]
        
        if status:
            clients = [c for c in clients if c.get("status") == status]
        if contract_status:
            clients = [c for c in clients if c.get("contract_status") == contract_status]
        if industry:
            clients = [c for c in clients if c.get("industry") == industry]
        
        return clients
    
    def get_client(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Get client by ID.
        
        Args:
            client_id: Client ID (e.g., msp_001)
        
        Returns:
            Client dictionary or None if not found
        """
        data = self._load()
        for client in data["clients"]:
            if client.get("id") == client_id:
                return client
        return None
    
    def get_client_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get client by name (case-insensitive).
        
        Args:
            name: Client name
        
        Returns:
            Client dictionary or None if not found
        """
        data = self._load()
        name_lower = name.lower()
        for client in data["clients"]:
            if client.get("name", "").lower() == name_lower:
                return client
        return None
    
    def add_client(
        self,
        name: str,
        industry: str = "Unknown",
        status: str = "active",
        contract_status: str = "valid",
        contract_notes: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add new client.
        
        Args:
            name: Client name
            industry: Industry type
            status: Client status (active, inactive, prospect)
            contract_status: Contract status (valid, renewal_required, expired)
            contract_notes: Notes about contract
            notes: General notes
        
        Returns:
            Created client dictionary
        """
        data = self._load()
        
        # Check for duplicate name
        if self.get_client_by_name(name):
            _logger.warning(f"Client '{name}' already exists")
            return {"error": f"Client '{name}' already exists"}
        
        now = datetime.utcnow().isoformat()
        
        client = {
            "id": self._generate_id(data),
            "name": name,
            "slug": name.lower().replace(" ", "-").replace("'", ""),
            "industry": industry,
            "status": status,
            "contract_status": contract_status,
            "contract_renewal_date": None,
            "contract_notes": contract_notes,
            "created_at": now,
            "updated_at": None,
            "primary_contact": None,
            "contacts": [],
            "assets": [],
            "exchange": {"domain": None, "users": []},
            "nextcloud": {"folder": None},
            "notes": [{"text": notes, "date": now}] if notes else []
        }
        
        data["clients"].append(client)
        if self._save(data):
            _logger.info(f"Added client '{name}' with ID {client['id']}")
        
        return client
    
    def update_client(
        self,
        client_id: str,
        name: Optional[str] = None,
        industry: Optional[str] = None,
        status: Optional[str] = None,
        contract_status: Optional[str] = None,
        contract_renewal_date: Optional[str] = None,
        contract_notes: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Update client information.
        
        Args:
            client_id: Client ID
            name: New name (optional)
            industry: New industry (optional)
            status: New status (optional)
            contract_status: New contract status (optional)
            contract_renewal_date: Renewal deadline (optional)
            contract_notes: Contract notes (optional)
        
        Returns:
            Updated client or None if not found
        """
        data = self._load()
        
        for client in data["clients"]:
            if client.get("id") == client_id:
                if name:
                    client["name"] = name
                    client["slug"] = name.lower().replace(" ", "-").replace("'", "")
                if industry:
                    client["industry"] = industry
                if status:
                    client["status"] = status
                if contract_status:
                    client["contract_status"] = contract_status
                if contract_renewal_date:
                    client["contract_renewal_date"] = contract_renewal_date
                if contract_notes:
                    client["contract_notes"] = contract_notes
                
                client["updated_at"] = datetime.utcnow().isoformat()
                
                if self._save(data):
                    _logger.info(f"Updated client {client_id}")
                
                return client
        
        _logger.warning(f"Client {client_id} not found")
        return None
    
    def delete_client(self, client_id: str) -> bool:
        """Delete client.
        
        Args:
            client_id: Client ID
        
        Returns:
            True if deleted, False if not found
        """
        data = self._load()
        initial_count = len(data["clients"])
        data["clients"] = [c for c in data["clients"] if c.get("id") != client_id]
        
        if len(data["clients"]) < initial_count:
            if self._save(data):
                _logger.info(f"Deleted client {client_id}")
            return True
        
        _logger.warning(f"Client {client_id} not found for deletion")
        return False
    
    def add_contact(
        self,
        client_id: str,
        name: str,
        email: str,
        role: Optional[str] = None,
        phone: Optional[str] = None,
        is_primary: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Add contact to client.
        
        Args:
            client_id: Client ID
            name: Contact name
            email: Contact email
            role: Contact role (optional)
            phone: Contact phone (optional)
            is_primary: Set as primary contact
        
        Returns:
            Updated client or None if not found
        """
        data = self._load()
        
        for client in data["clients"]:
            if client.get("id") == client_id:
                contact = {
                    "name": name,
                    "email": email,
                    "role": role,
                    "phone": phone,
                    "created_at": datetime.utcnow().isoformat()
                }
                client["contacts"].append(contact)
                
                if is_primary:
                    client["primary_contact"] = email
                
                if self._save(data):
                    _logger.info(f"Added contact '{name}' to client {client_id}")
                
                return client
        
        _logger.warning(f"Client {client_id} not found")
        return None
    
    def add_asset(
        self,
        client_id: str,
        asset_type: str,
        value: str,
        notes: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Add asset to client.
        
        Args:
            client_id: Client ID
            asset_type: Asset type (domain, server, license, etc.)
            value: Asset value (URL, name, etc.)
            notes: Optional notes
        
        Returns:
            Updated client or None if not found
        """
        data = self._load()
        
        for client in data["clients"]:
            if client.get("id") == client_id:
                asset = {
                    "type": asset_type,
                    "value": value,
                    "notes": notes,
                    "created_at": datetime.utcnow().isoformat()
                }
                client["assets"].append(asset)
                
                if self._save(data):
                    _logger.info(f"Added asset '{asset_type}' to client {client_id}")
                
                return client
        
        _logger.warning(f"Client {client_id} not found")
        return None
    
    def add_note(
        self,
        client_id: str,
        note: str
    ) -> Optional[Dict[str, Any]]:
        """Add note to client.
        
        Args:
            client_id: Client ID
            note: Note text
        
        Returns:
            Updated client or None if not found
        """
        data = self._load()
        
        for client in data["clients"]:
            if client.get("id") == client_id:
                client["notes"].append({
                    "text": note,
                    "date": datetime.utcnow().isoformat()
                })
                
                if self._save(data):
                    _logger.info(f"Added note to client {client_id}")
                
                return client
        
        _logger.warning(f"Client {client_id} not found")
        return None
    
    def get_clients_for_renewal(self) -> List[Dict[str, Any]]:
        """Get all clients that need contract renewal.
        
        Returns:
            List of clients with contract_status == 'renewal_required'
        """
        return self.list_clients(contract_status="renewal_required")
    
    def export_clients(self) -> str:
        """Export clients as JSON string.
        
        Returns:
            JSON string of all clients
        """
        data = self._load()
        return json.dumps(data["clients"], indent=2, default=str)


def main():
    """CLI entry point for clients module."""
    import argparse
    
    parser = argparse.ArgumentParser(description="MSP Client Management")
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # Init
    subparsers.add_parser("init", help="Initialize empty database")
    
    # List
    list_parser = subparsers.add_parser("list", help="List clients")
    list_parser.add_argument("--status", help="Filter by status")
    list_parser.add_argument("--contract-status", help="Filter by contract status")
    list_parser.add_argument("--industry", help="Filter by industry")
    
    # Add
    add_parser = subparsers.add_parser("add", help="Add client")
    add_parser.add_argument("--name", required=True, help="Client name")
    add_parser.add_argument("--industry", default="Unknown", help="Industry")
    add_parser.add_argument("--status", default="active", help="Client status")
    add_parser.add_argument("--contract-status", default="valid", help="Contract status")
    add_parser.add_argument("--notes", help="Notes")
    
    # Get
    get_parser = subparsers.add_parser("get", help="Get client")
    get_parser.add_argument("--id", required=True, help="Client ID")
    
    # Update
    update_parser = subparsers.add_parser("update", help="Update client")
    update_parser.add_argument("--id", required=True, help="Client ID")
    update_parser.add_argument("--name", help="New name")
    update_parser.add_argument("--industry", help="New industry")
    update_parser.add_argument("--status", help="New status")
    update_parser.add_argument("--contract-status", help="New contract status")
    update_parser.add_argument("--contract-notes", help="Contract notes")
    
    # Delete
    delete_parser = subparsers.add_parser("delete", help="Delete client")
    delete_parser.add_argument("--id", required=True, help="Client ID")
    
    # Export
    subparsers.add_parser("export", help="Export clients as JSON")
    
    args = parser.parse_args()
    db = ClientDB()
    
    if args.command == "init":
        db.init_db()
        print(json.dumps({"ok": True, "message": "Database initialized"}, indent=2))
    
    elif args.command == "list":
        clients = db.list_clients(
            status=args.status,
            contract_status=args.contract_status,
            industry=args.industry
        )
        print(json.dumps({"ok": True, "count": len(clients), "clients": clients}, indent=2))
    
    elif args.command == "add":
        client = db.add_client(
            name=args.name,
            industry=args.industry,
            status=args.status,
            contract_status=args.contract_status,
            notes=args.notes
        )
        print(json.dumps({"ok": True, "client": client}, indent=2))
    
    elif args.command == "get":
        client = db.get_client(args.id)
        if client:
            print(json.dumps({"ok": True, "client": client}, indent=2))
        else:
            print(json.dumps({"ok": False, "error": f"Client {args.id} not found"}, indent=2))
    
    elif args.command == "update":
        client = db.update_client(
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
        if db.delete_client(args.id):
            print(json.dumps({"ok": True, "message": f"Client {args.id} deleted"}, indent=2))
        else:
            print(json.dumps({"ok": False, "error": f"Client {args.id} not found"}, indent=2))
    
    elif args.command == "export":
        print(db.export_clients())
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()