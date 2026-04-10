#!/usr/bin/env python3
"""Unit tests for the Nextcloud module."""

import os
import sys
import unittest
from io import StringIO
from unittest.mock import patch

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from modules.nextcloud.nextcloud import NextcloudClient, run_cli


class FakeResponse:
    """Simple fake HTTP response for tests."""

    def __init__(self, status_code=200, content=b"", text="", chunks=None):
        self.status_code = status_code
        self.content = content
        self.text = text
        self._chunks = chunks or []

    def iter_content(self, chunk_size=8192):
        """Yield configured chunks."""
        del chunk_size
        for chunk in self._chunks:
            yield chunk


class NextcloudTestCase(unittest.TestCase):
    """Base helpers for Nextcloud tests."""

    ENV = {
        "NEXTCLOUD_URL": "https://cloud.example.com",
        "NEXTCLOUD_USERNAME": "alex",
        "NEXTCLOUD_APP_PASSWORD": "app-pass",
    }

    def create_client(self):
        """Create a client with user ID resolution stubbed."""
        with patch.dict(os.environ, self.ENV, clear=False):
            with patch.object(
                NextcloudClient,
                "_resolve_user_id",
                lambda self: setattr(self, "user_id", "alex-id"),
            ):
                return NextcloudClient()


class TestNextcloudClient(NextcloudTestCase):
    """Tests for Nextcloud client behavior."""

    def test_get_full_url_uses_user_id_and_normalized_path(self):
        client = self.create_client()

        result = client._get_full_url("Documents//Offers/")

        self.assertEqual(
            result,
            "https://cloud.example.com/remote.php/dav/files/alex-id/Documents/Offers",
        )

    def test_list_recursive_collects_nested_entries(self):
        client = self.create_client()

        with patch.object(client, "_list_directory") as mock_list_directory:
            mock_list_directory.side_effect = [
                [
                    {"name": "Docs", "type": "folder", "path": "/Docs", "size": 0, "modified": "-", "mime_type": ""},
                    {"name": "root.txt", "type": "file", "path": "/root.txt", "size": 10, "modified": "-", "mime_type": "text/plain"},
                ],
                [
                    {"name": "Nested", "type": "folder", "path": "/Docs/Nested", "size": 0, "modified": "-", "mime_type": ""},
                    {"name": "offer.pdf", "type": "file", "path": "/Docs/offer.pdf", "size": 20, "modified": "-", "mime_type": "application/pdf"},
                ],
                [
                    {"name": "notes.md", "type": "file", "path": "/Docs/Nested/notes.md", "size": 30, "modified": "-", "mime_type": "text/markdown"},
                ],
            ]

            results = client.list("/", recursive=True)

        self.assertEqual([item["path"] for item in results], [
            "/Docs",
            "/root.txt",
            "/Docs/Nested",
            "/Docs/offer.pdf",
            "/Docs/Nested/notes.md",
        ])

    def test_search_filters_case_insensitive_results(self):
        client = self.create_client()

        with patch.object(client, "list", return_value=[
            {"name": "Contract.pdf", "type": "file", "path": "/Clients/Contract.pdf", "size": 10, "modified": "-", "mime_type": "application/pdf"},
            {"name": "notes.txt", "type": "file", "path": "/Clients/notes.txt", "size": 5, "modified": "-", "mime_type": "text/plain"},
        ]):
            results = client.search("contract")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["path"], "/Clients/Contract.pdf")

    def test_create_share_link_returns_share_metadata(self):
        client = self.create_client()
        xml_response = b"""
        <ocs>
          <meta><status>ok</status><statuscode>100</statuscode><message>OK</message></meta>
          <data>
            <id>44</id>
            <url>https://cloud.example.com/s/abc123</url>
            <token>abc123</token>
            <path>/Clients/offer.pdf</path>
            <permissions>1</permissions>
          </data>
        </ocs>
        """

        with patch("modules.nextcloud.nextcloud.requests.request", return_value=FakeResponse(status_code=200, content=xml_response)):
            result = client.create_share_link("/Clients/offer.pdf", password="secret", expire_date="2026-04-30")

        self.assertEqual(result["id"], "44")
        self.assertEqual(result["url"], "https://cloud.example.com/s/abc123")
        self.assertEqual(result["path"], "/Clients/offer.pdf")
        self.assertTrue(result["password_protected"])

    def test_list_share_links_returns_only_public_links(self):
        client = self.create_client()
        xml_response = b"""
        <ocs>
          <meta><status>ok</status><statuscode>100</statuscode><message>OK</message></meta>
          <data>
            <element>
              <id>10</id>
              <share_type>3</share_type>
              <path>/Public/report.pdf</path>
              <url>https://cloud.example.com/s/report</url>
              <permissions>1</permissions>
            </element>
            <element>
              <id>11</id>
              <share_type>0</share_type>
              <path>/Private/internal.txt</path>
              <permissions>1</permissions>
            </element>
          </data>
        </ocs>
        """

        with patch("modules.nextcloud.nextcloud.requests.request", return_value=FakeResponse(status_code=200, content=xml_response)):
            results = client.list_share_links()

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "10")
        self.assertEqual(results[0]["path"], "/Public/report.pdf")

    def test_revoke_share_link_returns_true_on_success(self):
        client = self.create_client()
        xml_response = b"""
        <ocs>
          <meta><status>ok</status><statuscode>100</statuscode><message>OK</message></meta>
          <data/>
        </ocs>
        """

        with patch("modules.nextcloud.nextcloud.requests.request", return_value=FakeResponse(status_code=200, content=xml_response)):
            result = client.revoke_share_link("55")

        self.assertTrue(result)


class TestNextcloudCli(NextcloudTestCase):
    """Tests for Nextcloud CLI behavior."""

    def test_run_cli_requires_search_query(self):
        with patch.dict(os.environ, self.ENV, clear=False):
            with patch("sys.stdout", new_callable=StringIO) as stdout:
                exit_code = run_cli(["search"])

        self.assertEqual(exit_code, 1)
        self.assertIn("Usage: nextcloud.py search <query> [remote_path]", stdout.getvalue())

    def test_run_cli_list_recursive_prints_results(self):
        fake_result = [
            {"name": "Docs", "type": "folder", "path": "/Docs", "size": 0, "modified": "Wed, 10 Apr 2026 12:00:00 GMT", "mime_type": ""}
        ]

        with patch.dict(os.environ, self.ENV, clear=False):
            with patch.object(
                NextcloudClient,
                "_resolve_user_id",
                lambda self: setattr(self, "user_id", "alex-id"),
            ):
                with patch.object(NextcloudClient, "list", return_value=fake_result):
                    with patch("sys.stdout", new_callable=StringIO) as stdout:
                        exit_code = run_cli(["list", "/", "--recursive"])

        self.assertEqual(exit_code, 0)
        self.assertIn("Docs", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
