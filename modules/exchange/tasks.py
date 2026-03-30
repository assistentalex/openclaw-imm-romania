"""
Task operations for Exchange Mailbox skill.
Supports creating, listing, updating, and deleting tasks.
Tasks can be assigned to self or to other users.
"""

import argparse
import sys
import os
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any

# Add scripts directory to path for imports FIRST
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from exchangelib.items import Task

    HAS_EXCHANGELIB = True
except ImportError:
    HAS_EXCHANGELIB = False

from connection import get_account
from utils import out, die, parse_datetime, format_datetime

# Task status mapping
STATUS_MAP = {
    "not_started": "NotStarted",
    "in_progress": "InProgress",
    "completed": "Completed",
    "waiting": "WaitingOnOthers",
    "deferred": "Deferred",
}

STATUS_REVERSE = {v: k for k, v in STATUS_MAP.items()}


def cmd_connect(args: argparse.Namespace) -> None:
    """Test connection to Exchange and show task folder info."""
    from connection import test_connection

    result = test_connection()
    out({"ok": True, "message": "Connected successfully", **result})


def cmd_list(args: argparse.Namespace) -> None:
    """List tasks from the tasks folder."""
    account = get_account()

    # Build query
    query = account.tasks.all()

    # Note: EWS doesn't support filtering on status field for tasks
    # We'll filter client-side instead

    # Order by due date
    query = query.order_by("due_date")

    # Limit
    limit = args.limit or 20
    items = list(query[: limit * 2])  # Fetch more to account for filtering

    # Filter by status (client-side)
    if args.status:
        status_value = STATUS_MAP.get(args.status.lower())
        items = [t for t in items if str(t.status) == status_value]

    # Filter by completion
    if args.completed_only:
        items = [t for t in items if str(t.status) == "Completed"]
    elif not args.include_completed:
        # Default: exclude completed
        items = [t for t in items if str(t.status) != "Completed"]

    # Filter by overdue
    if args.overdue:
        now = datetime.now()
        items = [
            t
            for t in items
            if t.due_date and t.due_date < now and str(t.status) != "Completed"
        ]

    # Apply limit after filtering
    items = items[:limit]

    tasks = []
    for item in items:
        tasks.append(task_to_dict(item))

    out({"ok": True, "count": len(tasks), "tasks": tasks})


def cmd_get(args: argparse.Namespace) -> None:
    """Get details of a specific task."""
    account = get_account()

    try:
        task = account.tasks.get(id=args.id)
        out({"ok": True, "task": task_to_dict(task, detailed=True)})
    except Exception:
        die(f"Task not found: {args.id}")


def cmd_create(args: argparse.Namespace) -> None:
    """Create a new task in the account's Tasks folder."""
    account = get_account()

    # Parse dates - EWS requires EWSDate for tasks (not EWSDateTime)
    from exchangelib import EWSDate

    if args.start:
        start_dt = parse_datetime(args.start)
        if start_dt:
            start_date = EWSDate(start_dt.year, start_dt.month, start_dt.day)
    else:
        start_date = None

    if args.due:
        due_dt = parse_datetime(args.due)
        if due_dt:
            due_date = EWSDate(due_dt.year, due_dt.month, due_dt.day)
    else:
        due_date = None

    # Create task object
    task = Task(
        account=account,
        folder=account.tasks,
        subject=args.subject,
        body=args.body or "",
    )

    # Set dates
    if start_date:
        task.start_date = start_date
    if due_date:
        task.due_date = due_date

    # Set priority
    if args.priority:
        priority_map = {"low": "Low", "normal": "Normal", "high": "High"}
        task.importance = priority_map.get(args.priority.lower(), "Normal")

    # Note: Task assignment to others requires TaskRequest which is not fully
    # supported by exchangelib. Tasks are created locally in the account's Tasks folder.
    # If you need to notify someone about a task, send a separate email.

    # Save
    try:
        task.save()
    except Exception as e:
        die(f"Failed to create task: {e}")

    out(
        {"ok": True, "message": "Task created successfully", "task": task_to_dict(task)}
    )


def cmd_update(args: argparse.Namespace) -> None:
    """Update an existing task."""
    account = get_account()

    try:
        task = account.tasks.get(id=args.id)
    except Exception:
        die(f"Task not found: {args.id}")

    # Update fields
    updated = []

    if args.subject:
        task.subject = args.subject
        updated.append("subject")

    if args.body:
        task.body = args.body
        updated.append("body")

    if args.due:
        task.due_date = parse_datetime(args.due)
        updated.append("due_date")

    if args.start:
        task.start_date = parse_datetime(args.start)
        updated.append("start_date")

    if args.priority:
        priority_map = {"low": "Low", "normal": "Normal", "high": "High"}
        task.importance = priority_map.get(args.priority.lower(), "Normal")
        updated.append("importance")

    if args.status:
        task.status = STATUS_MAP.get(args.status.lower(), args.status)
        updated.append("status")

        # If completed, set completion
        if args.status.lower() == "completed":
            task.percent_complete = Decimal("100")
            # complete_date is read-only - Exchange sets it automatically

    if args.percent:
        task.percent_complete = min(100, max(0, args.percent))
        updated.append("percent_complete")

        # Auto-update status based on percent
        if task.percent_complete == 100:
            task.status = "Completed"
            task.percent_complete = Decimal("100")
            # complete_date is read-only - Exchange sets it automatically
        elif task.percent_complete > 0:
            task.status = "InProgress"

    if not updated:
        die(
            "No fields to update. Use --subject, --body, --due, --start, --priority, --status, or --percent"
        )

    try:
        task.save(update_fields=updated)
    except Exception as e:
        die(f"Failed to update task: {e}")

    out(
        {
            "ok": True,
            "message": "Task updated successfully",
            "updated_fields": updated,
            "task": task_to_dict(task),
        }
    )


def cmd_complete(args: argparse.Namespace) -> None:
    """Mark a task as completed."""
    account = get_account()

    try:
        task = account.tasks.get(id=args.id)
    except Exception:
        die(f"Task not found: {args.id}")

    task.status = "Completed"
    task.percent_complete = Decimal("100")
    # complete_date is read-only - Exchange sets it automatically

    try:
        task.save(update_fields=["status", "percent_complete"])
    except Exception as e:
        die(f"Failed to complete task: {e}")

    out({"ok": True, "message": "Task marked as completed", "task": task_to_dict(task)})


def cmd_delete(args: argparse.Namespace) -> None:
    """Delete a task."""
    account = get_account()

    try:
        task = account.tasks.get(id=args.id)
    except Exception:
        die(f"Task not found: {args.id}")

    subject = task.subject

    if args.hard:
        task.delete()
    else:
        task.move_to_trash()

    out({"ok": True, "message": f"Task '{subject}' deleted", "id": args.id})


def task_to_dict(task: Task, detailed: bool = False) -> Dict[str, Any]:
    """Convert Task object to dictionary."""
    result = {
        "id": task.id,
        "subject": task.subject,
        "status": STATUS_REVERSE.get(str(task.status), str(task.status)),
        "percent_complete": task.percent_complete or 0,
        "due_date": format_datetime(task.due_date),
        "start_date": format_datetime(task.start_date),
    }

    if detailed:
        result.update(
            {
                "body": task.body if task.body else None,
                "owner": task.owner,
                "delegation_state": (
                    str(task.delegation_state) if task.delegation_state else None
                ),
                "date_completed": format_datetime(task.date_completed),
                "importance": str(task.importance),
                "created": format_datetime(task.datetime_created),
                "modified": format_datetime(task.datetime_received),
            }
        )

    return result


def add_parser(subparsers: argparse.ArgumentParser) -> None:
    """Add task commands to the CLI parser."""

    # connect
    p_connect = subparsers.add_parser("connect", help="Test connection to Exchange")
    p_connect.set_defaults(func=cmd_connect)

    # list
    p_list = subparsers.add_parser("list", help="List tasks")
    p_list.add_argument(
        "--limit", "-n", type=int, default=20, help="Maximum number of tasks to return"
    )
    p_list.add_argument(
        "--status",
        choices=["not_started", "in_progress", "completed", "waiting", "deferred"],
        help="Filter by status",
    )
    p_list.add_argument(
        "--completed",
        action="store_true",
        dest="completed_only",
        help="Show only completed tasks",
    )
    p_list.add_argument(
        "--all",
        "-a",
        action="store_true",
        dest="include_completed",
        help="Include completed tasks",
    )
    p_list.add_argument(
        "--overdue", action="store_true", help="Show only overdue tasks"
    )
    p_list.set_defaults(func=cmd_list)

    # get
    p_get = subparsers.add_parser("get", help="Get task details")
    p_get.add_argument("--id", "-i", required=True, help="Task ID")
    p_get.set_defaults(func=cmd_get)

    # create
    p_create = subparsers.add_parser("create", help="Create a new task")
    p_create.add_argument("--subject", "-s", required=True, help="Task subject")
    p_create.add_argument("--body", "-b", help="Task body/description")
    p_create.add_argument("--due", "-d", help="Due date (YYYY-MM-DD or +Nd for N days)")
    p_create.add_argument("--start", help="Start date (YYYY-MM-DD)")
    p_create.add_argument(
        "--priority",
        "-p",
        choices=["low", "normal", "high"],
        default="normal",
        help="Task priority",
    )
    p_create.set_defaults(func=cmd_create)

    # update
    p_update = subparsers.add_parser("update", help="Update a task")
    p_update.add_argument("--id", "-i", required=True, help="Task ID")
    p_update.add_argument("--subject", "-s", help="New subject")
    p_update.add_argument("--body", "-b", help="New body")
    p_update.add_argument("--due", "-d", help="New due date")
    p_update.add_argument("--start", help="New start date")
    p_update.add_argument(
        "--priority", "-p", choices=["low", "normal", "high"], help="New priority"
    )
    p_update.add_argument(
        "--status",
        choices=["not_started", "in_progress", "completed", "waiting", "deferred"],
        help="New status",
    )
    p_update.add_argument("--percent", type=int, help="Completion percentage (0-100)")
    p_update.set_defaults(func=cmd_update)

    # complete
    p_complete = subparsers.add_parser("complete", help="Mark task as completed")
    p_complete.add_argument("--id", "-i", required=True, help="Task ID")
    p_complete.set_defaults(func=cmd_complete)

    # delete
    p_delete = subparsers.add_parser("delete", help="Delete a task")
    p_delete.add_argument("--id", "-i", required=True, help="Task ID")
    p_delete.add_argument(
        "--hard", action="store_true", help="Permanently delete (no trash)"
    )
    p_delete.set_defaults(func=cmd_delete)


def main() -> None:
    """Main entry point for standalone execution."""
    parser = argparse.ArgumentParser(
        prog="tasks.py",
        description="Task operations for Exchange Mailbox",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    subparsers.required = True

    add_parser(subparsers)

    args = parser.parse_args()

    # Load configuration
    from config import get_config

    get_config()

    # Execute command
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
