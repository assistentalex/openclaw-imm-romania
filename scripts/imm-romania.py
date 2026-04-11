#!/usr/bin/env python3
"""
IMM-Romania - Unified CLI for Email, Calendar, Tasks, and Files.

Orchestrates Exchange (mail, calendar, tasks) and Nextcloud (files) operations.
"""

import sys
import os

# Add skill root to path so 'modules' package is importable
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
sys.path.insert(0, SKILL_ROOT)


def main():
    """Main entry point for IMM-Romania CLI."""
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    module = sys.argv[1]
    args = sys.argv[2:]

    if module in ('mail', 'cal', 'calendar', 'tasks', 'analytics', 'sync'):
        # Route to Exchange module
        from modules.exchange.cli import main as exchange_main
        # Normalize 'cal' to 'calendar'
        normalized_module = 'calendar' if module == 'cal' else module
        # Set sys.argv for exchange module and call main()
        sys.argv = [sys.argv[0], normalized_module] + args
        exchange_main()

    elif module in ('files', 'nextcloud', 'nc'):
        from modules.nextcloud.nextcloud import run_cli as nextcloud_run_cli

        if len(args) < 1:
            print("Error: No command specified for files.")
            print(
                "Available commands: list, search, upload, download, mkdir, "
                "delete, move, copy, info, shared, share-create, share-list, share-revoke"
            )
            sys.exit(1)

        sys.exit(nextcloud_run_cli(args))

    elif module in ('help', '-h', '--help'):
        print_usage()

    else:
        print(f"Error: Unknown module: {module}")
        print_usage()
        sys.exit(1)


def print_usage():
    """Print usage information."""
    print("""
IMM-Romania - Unified CLI for Email, Calendar, Tasks, and Files

Usage:
    imm-romania <module> <command> [options]

Modules:
    mail        Email operations (Exchange)
    cal         Calendar operations (Exchange)
    tasks       Task management (Exchange)
    analytics   Email analytics and statistics (Exchange)
    sync        Task sync and reminders (Exchange)
    files       File operations (Nextcloud)

Email Commands:
    imm-romania mail connect              Test Exchange connection
    imm-romania mail read [--folder FOLDER] [--limit N] [--unread]
    imm-romania mail send --to EMAIL --subject SUBJECT --body BODY
    imm-romania mail reply --id EMAIL_ID --body BODY
    imm-romania mail forward --id EMAIL_ID --to EMAIL

Calendar Commands:
    imm-romania cal today                 Show today's events
    imm-romania cal week                  Show this week's events
    imm-romania cal list [--days N]
    imm-romania cal create --subject SUBJECT --start DATETIME [--duration MIN]

Task Commands:
    imm-romania tasks list [--overdue] [--status STATUS]
    imm-romania tasks create --subject SUBJECT [--due DATE] [--priority LEVEL]
    imm-romania tasks complete --id TASK_ID
    imm-romania tasks delete --id TASK_ID

Sync Commands:
    imm-romania sync sync                 Sync tasks with Exchange
    imm-romania sync status               Show sync status
    imm-romania sync reminders [--hours N] [--dry-run]

Analytics Commands:
    imm-romania analytics stats --days N     Email statistics
    imm-romania analytics response-time      Response time analysis
    imm-romania analytics top-senders        Top senders by count
    imm-romania analytics heatmap            Activity heatmap
    imm-romania analytics folders            Folder statistics
    imm-romania analytics report             Full analytics report

File Commands:
    imm-romania files list [PATH] [--recursive] List files in directory
    imm-romania files search QUERY [PATH]       Search files/folders by name
    imm-romania files upload LOCAL REMOTE       Upload file to Nextcloud
    imm-romania files download REMOTE LOCAL     Download file from Nextcloud
    imm-romania files mkdir PATH                Create directory
    imm-romania files delete PATH               Delete file or directory
    imm-romania files move OLD NEW              Move/rename file
    imm-romania files copy SRC DEST             Copy file
    imm-romania files info PATH                 Get file info
    imm-romania files shared                    List items shared with current user
    imm-romania files share-create PATH [--password VALUE] [--expire-date YYYY-MM-DD] [--public-upload]
    imm-romania files share-list [PATH]         List public share links
    imm-romania files share-revoke SHARE_ID     Revoke public share link

Configuration:
    Set environment variables:
        EXCHANGE_SERVER    - Exchange EWS URL
        EXCHANGE_USERNAME  - Exchange username
        EXCHANGE_PASSWORD  - Exchange password
        EXCHANGE_EMAIL     - Exchange email address
        NEXTCLOUD_URL      - Nextcloud base URL
        NEXTCLOUD_USERNAME - Nextcloud username
        NEXTCLOUD_APP_PASSWORD - Nextcloud app password

    Or use config.yaml in skill directory.

Examples:
    # Send email
    imm-romania mail send --to client@example.com --subject "Offer" --body "Please find attached..."

    # Create calendar event
    imm-romania cal create --subject "Meeting" --start "2024-01-15 14:00" --duration 60

    # Create task
    imm-romania tasks create --subject "Follow-up" --due "+7d" --priority high

    # Upload file to Nextcloud
    imm-romania files upload /local/report.pdf /Documents/

    # Search files in Nextcloud
    imm-romania files search contract /Clients/

    # Create a share link
    imm-romania files share-create /Contracts/offer.pdf --expire-date 2026-04-30

For more information, see references/setup.md
""")


if __name__ == '__main__':
    main()