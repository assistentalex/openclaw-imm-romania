#!/usr/bin/env python3
"""
Unit tests for IMM-Romania skill.
Run with: python3 -m pytest tests/test_all.py -v
"""

import os
import sys
import json
import unittest
from unittest.mock import patch, MagicMock

# Add scripts dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestUtils(unittest.TestCase):
    """Tests for utility functions."""
    
    def test_out_function(self):
        """Test JSON output."""
        from utils import out
        # out() calls sys.exit(0), so we can't test it directly
        # But we can verify the function exists
        self.assertTrue(callable(out))
    
    def test_die_function(self):
        """Test error output."""
        from utils import die
        self.assertTrue(callable(die))
    
    def test_parse_datetime_iso(self):
        """Test ISO datetime parsing."""
        from utils import parse_datetime
        result = parse_datetime("2024-01-15T10:30:00")
        self.assertIsNotNone(result)
        self.assertEqual(result.year, 2024)
        self.assertEqual(result.month, 1)
        self.assertEqual(result.day, 15)
    
    def test_parse_datetime_date(self):
        """Test date-only parsing."""
        from utils import parse_datetime
        result = parse_datetime("2024-01-15")
        self.assertIsNotNone(result)
        self.assertEqual(result.year, 2024)
    
    def test_parse_datetime_relative(self):
        """Test relative date parsing."""
        from utils import parse_datetime
        from datetime import datetime, timedelta
        
        result = parse_datetime("+1d")
        expected = datetime.now() + timedelta(days=1)
        # Allow 1 minute difference for test execution time
        self.assertAlmostEqual(result.timestamp(), expected.timestamp(), delta=60)
    
    def test_parse_datetime_none(self):
        """Test None input."""
        from utils import parse_datetime
        result = parse_datetime(None)
        self.assertIsNone(result)
    
    def test_parse_recipients_single(self):
        """Test single recipient parsing."""
        from utils import parse_recipients
        result = parse_recipients("user@example.com")
        self.assertEqual(result, ["user@example.com"])
    
    def test_parse_recipients_multiple(self):
        """Test multiple recipients parsing."""
        from utils import parse_recipients
        result = parse_recipients("user1@example.com, user2@example.com")
        self.assertEqual(result, ["user1@example.com", "user2@example.com"])
    
    def test_parse_recipients_semicolon(self):
        """Test semicolon-separated recipients."""
        from utils import parse_recipients
        result = parse_recipients("user1@example.com; user2@example.com")
        self.assertEqual(result, ["user1@example.com", "user2@example.com"])
    
    def test_format_datetime(self):
        """Test datetime formatting."""
        from utils import format_datetime
        from datetime import datetime
        
        result = format_datetime(datetime(2024, 1, 15, 10, 30))
        self.assertEqual(result, "2024-01-15 10:30")
    
    def test_format_datetime_none(self):
        """Test None datetime formatting."""
        from utils import format_datetime
        result = format_datetime(None)
        self.assertIsNone(result)
    
    def test_validate_email_valid(self):
        """Test valid email validation."""
        from utils import validate_email
        self.assertTrue(validate_email("user@example.com"))
        self.assertTrue(validate_email("user.name@domain.org"))
    
    def test_validate_email_invalid(self):
        """Test invalid email validation."""
        from utils import validate_email
        self.assertFalse(validate_email(""))
        self.assertFalse(validate_email("invalid"))
        self.assertFalse(validate_email("no@domain"))
    
    def test_mask_email(self):
        """Test email masking."""
        from utils import mask_email
        result = mask_email("user@example.com")
        self.assertEqual(result, "u***@example.com")


class TestConfig(unittest.TestCase):
    """Tests for configuration management."""
    
    def test_get_env(self):
        """Test environment variable retrieval."""
        from utils import get_env
        
        # Test with existing env var
        os.environ["TEST_VAR"] = "test_value"
        result = get_env("TEST_VAR")
        self.assertEqual(result, "test_value")
        
        # Test with default
        result = get_env("NONEXISTENT_VAR", "default")
        self.assertEqual(result, "default")
        
        # Cleanup
        del os.environ["TEST_VAR"]
    
    @patch.dict(os.environ, {
        "EXCHANGE_SERVER": "https://test.com/EWS",
        "EXCHANGE_USERNAME": "testuser",
        "EXCHANGE_PASSWORD": "testpass",
        "EXCHANGE_EMAIL": "test@test.com"
    })
    def test_config_from_env(self):
        """Test config loading from environment."""
        from config import get_config
        
        config = get_config()
        self.assertEqual(config["server"], "https://test.com/EWS")
        self.assertEqual(config["username"], "testuser")
        self.assertEqual(config["password"], "testpass")
        self.assertEqual(config["email"], "test@test.com")


class TestMail(unittest.TestCase):
    """Tests for mail module structure."""
    
    def test_mail_functions_exist(self):
        """Test that all mail functions exist."""
        from mail import cmd_connect, cmd_read, cmd_get, cmd_send
        
        self.assertTrue(callable(cmd_connect))
        self.assertTrue(callable(cmd_read))
        self.assertTrue(callable(cmd_get))
        self.assertTrue(callable(cmd_send))
    
    def test_add_parser_exists(self):
        """Test that add_parser function exists."""
        from mail import add_parser
        self.assertTrue(callable(add_parser))


class TestCalendar(unittest.TestCase):
    """Tests for calendar module structure."""
    
    def test_calendar_functions_exist(self):
        """Test that all calendar functions exist."""
        from cal import cmd_connect, cmd_list, cmd_today, cmd_create
        
        self.assertTrue(callable(cmd_connect))
        self.assertTrue(callable(cmd_list))
        self.assertTrue(callable(cmd_today))
        self.assertTrue(callable(cmd_create))
    
    def test_add_parser_exists(self):
        """Test that add_parser function exists."""
        from cal import add_parser
        self.assertTrue(callable(add_parser))


class TestTasks(unittest.TestCase):
    """Tests for tasks module structure."""
    
    def test_tasks_functions_exist(self):
        """Test that all tasks functions exist."""
        from tasks import cmd_connect, cmd_list, cmd_create, cmd_complete
        
        self.assertTrue(callable(cmd_connect))
        self.assertTrue(callable(cmd_list))
        self.assertTrue(callable(cmd_create))
        self.assertTrue(callable(cmd_complete))
    
    def test_add_parser_exists(self):
        """Test that add_parser function exists."""
        from tasks import add_parser
        self.assertTrue(callable(add_parser))


class TestCLI(unittest.TestCase):
    """Tests for CLI module."""
    
    def test_cli_imports(self):
        """Test that CLI module imports successfully."""
        from cli import main
        self.assertTrue(callable(main))
    
    def test_cli_help(self):
        """Test CLI help output."""
        from cli import main
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "cli", "--help"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
        )
        self.assertIn("imm-romania", result.stdout)


if __name__ == "__main__":
    unittest.main()