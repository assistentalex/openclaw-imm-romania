"""Exchange contacts management."""

import argparse
import json
import sys
import os
from typing import Dict, Any, List, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from exchangelib.items import Contact
    HAS_EXCHANGELIB = True
except ImportError:
    HAS_EXCHANGELIB = False

from connection import get_account, get_account_for
from utils import out, die, parse_datetime, format_datetime


def contact_to_dict(contact: Any, detailed: bool = False) -> Dict[str, Any]:
    """Convert Contact to dict."""
    if not HAS_EXCHANGELIB or contact is None:
        return {}
    
    result: Dict[str, Any] = {
        "id": contact.id,
        "display_name": getattr(contact, 'display_name', None),
        "email_addresses": [e.email for e in (contact.email_addresses or []) if e and e.email] or None,
        "phone_numbers": [p.phone_number for p in (contact.phone_numbers or []) if p and p.phone_number] or None,
        "company_name": getattr(contact, 'company_name', None),
        "job_title": getattr(contact, 'job_title', None),
    }
    
    if detailed:
        result.update({
            "given_name": getattr(contact, 'given_name', None),
            "surname": getattr(contact, 'surname', None),
            "body": getattr(contact, 'body', None),
            "changekey": getattr(contact, 'changekey', None),
        })
    
    return result


def cmd_list(args: argparse.Namespace) -> None:
    """List contacts."""
    account = get_account_for(args.mailbox) if getattr(args, 'mailbox', None) else get_account()
    
    query = account.contacts.all().order_by("display_name")
    limit = args.limit or 20
    items = list(query[:limit])
    
    contacts = [contact_to_dict(c) for c in items]
    out({"ok": True, "count": len(contacts), "mailbox": account.primary_smtp_address, "contacts": contacts})


def cmd_get(args: argparse.Namespace) -> None:
    """Get contact by ID."""
    account = get_account_for(args.mailbox) if getattr(args, 'mailbox', None) else get_account()
    
    try:
        contact = account.contacts.get(id=args.id)
        out({"ok": True, "mailbox": account.primary_smtp_address, "contact": contact_to_dict(contact, detailed=True)})
    except Exception as e:
        die(f"Contact not found: {args.id} ({e})")


def cmd_search(args: argparse.Namespace) -> None:
    """Search contacts."""
    account = get_account_for(args.mailbox) if getattr(args, 'mailbox', None) else get_account()
    
    query = account.contacts.all().order_by("display_name")
    limit = args.limit or 20
    items = list(query[:limit * 2])
    
    query_lower = args.query.lower()
    results = []
    for c in items:
        name = (c.display_name or "").lower()
        email = " ".join(e.email for e in (c.email_addresses or []) if e).lower()
        if query_lower in name or query_lower in email:
            results.append(contact_to_dict(c))
        if len(results) >= limit:
            break
    
    out({"ok": True, "count": len(results), "mailbox": account.primary_smtp_address, "contacts": results})


def _set_email(contact: Any, email: str) -> None:
    """Set primary email on contact."""
    if not email:
        return
    try:
        from exchangelib.indexed_properties import EmailAddress
        contact.email_addresses = [EmailAddress(email=email, label="EmailAddress1")]
    except Exception:
        pass


def _set_phone(contact: Any, phone: str) -> None:
    """Set primary phone on contact."""
    if not phone:
        return
    try:
        from exchangelib.indexed_properties import PhoneNumber
        contact.phone_numbers = [PhoneNumber(phone_number=phone, label="BusinessPhone")]
    except Exception:
        pass


def cmd_create(args: argparse.Namespace) -> None:
    """Create contact."""
    account = get_account_for(args.mailbox) if getattr(args, 'mailbox', None) else get_account()
    
    contact = Contact(
        account=account,
        folder=account.contacts,
        display_name=args.name,
    )
    
    if args.email:
        _set_email(contact, args.email)
    if args.phone:
        _set_phone(contact, args.phone)
    if args.company:
        contact.company_name = args.company
    if args.title:
        contact.job_title = args.title
    
    try:
        contact.save()
    except Exception as e:
        die(f"Failed to create contact: {e}")
    
    out({"ok": True, "message": "Contact created", "contact": contact_to_dict(contact, detailed=True), "mailbox": account.primary_smtp_address})


def cmd_update(args: argparse.Namespace) -> None:
    """Update contact."""
    account = get_account_for(args.mailbox) if getattr(args, 'mailbox', None) else get_account()
    
    try:
        contact = account.contacts.get(id=args.id)
    except Exception as e:
        die(f"Contact not found: {args.id} ({e})")
    
    if args.name:
        contact.display_name = args.name
    if args.email:
        _set_email(contact, args.email)
    if args.phone:
        _set_phone(contact, args.phone)
    if args.company is not None:
        contact.company_name = args.company
    if args.title is not None:
        contact.job_title = args.title
    
    try:
        contact.save()
    except Exception as e:
        die(f"Failed to update contact: {e}")
    
    out({"ok": True, "message": "Contact updated", "contact": contact_to_dict(contact, detailed=True), "mailbox": account.primary_smtp_address})


def cmd_delete(args: argparse.Namespace) -> None:
    """Delete (move to trash) contact."""
    account = get_account_for(args.mailbox) if getattr(args, 'mailbox', None) else get_account()
    
    try:
        contact = account.contacts.get(id=args.id)
        contact.move_to_trash()
        out({"ok": True, "message": "Contact moved to trash", "id": args.id, "mailbox": account.primary_smtp_address})
    except Exception as e:
        die(f"Failed to delete contact: {e}")


def setup_parser(subparsers: Any) -> None:
    """Setup contacts subparser."""
    parser = subparsers.add_parser("contacts", help="Exchange contacts management")
    sub = parser.add_subparsers(dest="contacts_command")
    
    # list
    p_list = sub.add_parser("list", help="List contacts")
    p_list.add_argument("--limit", type=int, help="Max results")
    p_list.add_argument("--mailbox", help="Delegate mailbox")
    p_list.set_defaults(func=cmd_list)
    
    # get
    p_get = sub.add_parser("get", help="Get contact details")
    p_get.add_argument("--id", required=True, help="Contact ID")
    p_get.add_argument("--mailbox", help="Delegate mailbox")
    p_get.set_defaults(func=cmd_get)
    
    # search
    p_search = sub.add_parser("search", help="Search contacts")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--limit", type=int, help="Max results")
    p_search.add_argument("--mailbox", help="Delegate mailbox")
    p_search.set_defaults(func=cmd_search)
    
    # create
    p_create = sub.add_parser("create", help="Create contact")
    p_create.add_argument("--name", required=True, help="Display name")
    p_create.add_argument("--email", help="Email address")
    p_create.add_argument("--phone", help="Phone number")
    p_create.add_argument("--company", help="Company name")
    p_create.add_argument("--title", help="Job title")
    p_create.add_argument("--mailbox", help="Delegate mailbox")
    p_create.set_defaults(func=cmd_create)
    
    # update
    p_update = sub.add_parser("update", help="Update contact")
    p_update.add_argument("--id", required=True, help="Contact ID")
    p_update.add_argument("--name", help="Display name")
    p_update.add_argument("--email", help="Email address")
    p_update.add_argument("--phone", help="Phone number")
    p_update.add_argument("--company", help="Company name")
    p_update.add_argument("--title", help="Job title")
    p_update.add_argument("--mailbox", help="Delegate mailbox")
    p_update.set_defaults(func=cmd_update)
    
    # delete
    p_delete = sub.add_parser("delete", help="Delete contact")
    p_delete.add_argument("--id", required=True, help="Contact ID")
    p_delete.add_argument("--mailbox", help="Delegate mailbox")
    p_delete.set_defaults(func=cmd_delete)
