"""
Unit tests for MSP module.
Run with: python3 -m pytest tests/test_msp.py -v
"""

import os
import sys
import json
import tempfile
import unittest
from pathlib import Path
from datetime import datetime

# Add modules directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))

from msp.clients import ClientDB
from msp.contracts import ContractManager
from msp.reminders import RenewalReminder


class TestClientDB(unittest.TestCase):
    """Tests for ClientDB."""
    
    def setUp(self):
        """Create temp database for each test."""
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
        self.temp_file.close()
        self.db_path = Path(self.temp_file.name)
        self.db = ClientDB(db_path=self.db_path)
    
    def tearDown(self):
        """Clean up temp database."""
        if self.db_path.exists():
            os.unlink(self.temp_file.name)
    
    def test_init_db(self):
        """Test database initialization."""
        data = self.db.init_db()
        self.assertEqual(data["schema_version"], "1.0.0")
        self.assertEqual(len(data["clients"]), 0)
    
    def test_add_client(self):
        """Test adding a client."""
        client = self.db.add_client(
            name="Test Client",
            industry="Technology",
            status="active"
        )
        
        self.assertEqual(client["name"], "Test Client")
        self.assertEqual(client["industry"], "Technology")
        self.assertEqual(client["status"], "active")
        self.assertEqual(client["contract_status"], "valid")
        self.assertIsNotNone(client["id"])
        self.assertTrue(client["id"].startswith("msp_"))
    
    def test_add_duplicate_client(self):
        """Test adding duplicate client."""
        self.db.add_client(name="Duplicate Client")
        result = self.db.add_client(name="Duplicate Client")
        self.assertIn("error", result)
    
    def test_list_clients(self):
        """Test listing clients."""
        self.db.add_client(name="Client 1", industry="Tech")
        self.db.add_client(name="Client 2", industry="Finance")
        
        clients = self.db.list_clients()
        self.assertEqual(len(clients), 2)
        
        # Filter by industry
        tech_clients = self.db.list_clients(industry="Tech")
        self.assertEqual(len(tech_clients), 1)
    
    def test_get_client(self):
        """Test getting client by ID."""
        client = self.db.add_client(name="Get Test")
        retrieved = self.db.get_client(client["id"])
        self.assertEqual(retrieved["name"], "Get Test")
    
    def test_get_client_by_name(self):
        """Test getting client by name."""
        self.db.add_client(name="Name Test")
        client = self.db.get_client_by_name("Name Test")
        self.assertIsNotNone(client)
        
        # Case insensitive
        client = self.db.get_client_by_name("name test")
        self.assertIsNotNone(client)
    
    def test_update_client(self):
        """Test updating client."""
        client = self.db.add_client(name="Update Test")
        updated = self.db.update_client(
            client_id=client["id"],
            industry="Updated Industry",
            status="inactive"
        )
        
        self.assertEqual(updated["industry"], "Updated Industry")
        self.assertEqual(updated["status"], "inactive")
    
    def test_delete_client(self):
        """Test deleting client."""
        client = self.db.add_client(name="Delete Test")
        self.assertTrue(self.db.delete_client(client["id"]))
        
        # Try to delete again
        self.assertFalse(self.db.delete_client(client["id"]))
    
    def test_add_contact(self):
        """Test adding contact to client."""
        client = self.db.add_client(name="Contact Test")
        result = self.db.add_contact(
            client_id=client["id"],
            name="John Doe",
            email="john@example.com",
            role="CEO",
            is_primary=True
        )
        
        self.assertEqual(len(result["contacts"]), 1)
        self.assertEqual(result["contacts"][0]["name"], "John Doe")
        self.assertEqual(result["primary_contact"], "john@example.com")
    
    def test_add_asset(self):
        """Test adding asset to client."""
        client = self.db.add_client(name="Asset Test")
        result = self.db.add_asset(
            client_id=client["id"],
            asset_type="domain",
            value="example.com",
            notes="Main domain"
        )
        
        self.assertEqual(len(result["assets"]), 1)
        self.assertEqual(result["assets"][0]["type"], "domain")
    
    def test_get_clients_for_renewal(self):
        """Test getting clients needing renewal."""
        self.db.add_client(name="Valid Client", contract_status="valid")
        self.db.add_client(name="Renewal Client", contract_status="renewal_required")
        
        renewal_clients = self.db.get_clients_for_renewal()
        self.assertEqual(len(renewal_clients), 1)
        self.assertEqual(renewal_clients[0]["name"], "Renewal Client")


class TestContractManager(unittest.TestCase):
    """Tests for ContractManager."""
    
    def setUp(self):
        """Create temp files for each test."""
        self.db_file = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
        self.log_file = tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False)
        self.db_file.close()
        self.log_file.close()
        
        self.db_path = Path(self.db_file.name)
        self.log_path = Path(self.log_file.name)
        
        self.manager = ContractManager(db_path=self.db_path, log_path=self.log_path)
    
    def tearDown(self):
        """Clean up temp files."""
        for f in [self.db_file.name, self.log_file.name]:
            if os.path.exists(f):
                os.unlink(f)
    
    def test_set_renewal_required(self):
        """Test marking client for renewal."""
        client_db = ClientDB(db_path=self.db_path)
        client = client_db.add_client(name="Test Renewal")
        
        result = self.manager.set_renewal_required(
            client_id=client["id"],
            notes="Contract expiring"
        )
        
        self.assertEqual(result["contract_status"], "renewal_required")
        self.assertEqual(result["contract_notes"], "Contract expiring")
    
    def test_set_contract_valid(self):
        """Test marking contract as valid."""
        client_db = ClientDB(db_path=self.db_path)
        client = client_db.add_client(
            name="Test Valid",
            contract_status="renewal_required"
        )
        
        result = self.manager.set_contract_valid(
            client_id=client["id"],
            notes="Contract renewed"
        )
        
        self.assertEqual(result["contract_status"], "valid")
        self.assertEqual(result["contract_notes"], "Contract renewed")
    
    def test_get_renewal_summary(self):
        """Test getting renewal summary."""
        client_db = ClientDB(db_path=self.db_path)
        client_db.add_client(name="Valid", contract_status="valid")
        client_db.add_client(name="Renewal 1", contract_status="renewal_required")
        client_db.add_client(name="Renewal 2", contract_status="renewal_required")
        
        summary = self.manager.get_renewal_summary()
        
        self.assertEqual(summary["count"], 2)
        self.assertEqual(len(summary["clients"]), 2)
    
    def test_generate_reminder_email(self):
        """Test generating reminder email."""
        client_db = ClientDB(db_path=self.db_path)
        client_db.add_client(name="Valid", contract_status="valid")
        client_db.add_client(
            name="Renewal Client",
            contract_status="renewal_required",
            contract_notes="Needs renewal"
        )
        
        email = self.manager.generate_reminder_email(recipient="test@example.com")
        
        self.assertTrue(email["has_renewals"])
        self.assertIn("Contract Renewal Required", email["subject"])
        self.assertIn("Renewal Client", email["body"])
    
    def test_log_renewal(self):
        """Test logging renewal reminder."""
        client_db = ClientDB(db_path=self.db_path)
        client_db.add_client(name="Test", contract_status="renewal_required")
        
        self.manager.generate_reminder_email(recipient="test@example.com")
        
        history = self.manager.get_reminder_history()
        self.assertEqual(len(history), 1)


class TestRenewalReminder(unittest.TestCase):
    """Tests for RenewalReminder."""
    
    def setUp(self):
        """Create temp files for each test."""
        self.db_file = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
        self.log_file = tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False)
        self.db_file.close()
        self.log_file.close()
        
        self.db_path = Path(self.db_file.name)
        self.log_path = Path(self.log_file.name)
        
        self.reminder = RenewalReminder(db_path=self.db_path, log_path=self.log_path)
    
    def tearDown(self):
        """Clean up temp files."""
        for f in [self.db_file.name, self.log_file.name]:
            if os.path.exists(f):
                os.unlink(f)
    
    def test_run_daily_check_no_renewals(self):
        """Test daily check with no renewals."""
        result = self.reminder.run_daily_check(send_email=False)
        
        self.assertEqual(result["clients_needing_renewal"], 0)
        self.assertFalse(result["email_sent"])
    
    def test_run_daily_check_with_renewals(self):
        """Test daily check with renewals."""
        client_db = ClientDB(db_path=self.db_path)
        client_db.add_client(
            name="Renewal Client",
            contract_status="renewal_required"
        )
        
        result = self.reminder.run_daily_check(send_email=False)
        
        self.assertEqual(result["clients_needing_renewal"], 1)
    
    def test_add_client_for_renewal(self):
        """Test adding client for renewal tracking."""
        client_db = ClientDB(db_path=self.db_path)
        client = client_db.add_client(name="Test Client")
        
        result = self.reminder.add_client_for_renewal(
            client_id=client["id"],
            notes="Contract expiring"
        )
        
        self.assertTrue(result["ok"])
        self.assertEqual(result["client"]["contract_status"], "renewal_required")
    
    def test_resolve_renewal(self):
        """Test resolving renewal."""
        client_db = ClientDB(db_path=self.db_path)
        client = client_db.add_client(
            name="Test Client",
            contract_status="renewal_required"
        )
        
        result = self.reminder.resolve_renewal(
            client_id=client["id"],
            notes="Renewed successfully"
        )
        
        self.assertTrue(result["ok"])
        self.assertEqual(result["client"]["contract_status"], "valid")


if __name__ == "__main__":
    unittest.main()