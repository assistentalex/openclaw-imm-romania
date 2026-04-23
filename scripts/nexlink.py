#!/usr/bin/env python3
"""
NexLink - Unified CLI for Email, Calendar, Tasks, and Files.

Orchestrates Exchange (mail, calendar, tasks) and Nextcloud (files) operations.
"""

import sys
import os

# Add skill root to path so 'modules' package is importable
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
sys.path.insert(0, SKILL_ROOT)


def main():
    """Main entry point for NexLink CLI."""
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    module = sys.argv[1]
    args = sys.argv[2:]

    if module in ('mail', 'cal', 'calendar', 'tasks', 'analytics', 'sync', 'contacts'):
        # Route to Exchange module
        from modules.exchange.cli import main as exchange_main
        # Normalize 'cal' to 'calendar'
        normalized_module = 'calendar' if module == 'cal' else module
        # Set sys.argv for exchange module and call main()
        sys.argv = [sys.argv[0], normalized_module] + args
        exchange_main()

    elif module in ('files', 'nextcloud', 'nc', 'notes'):
        from modules.nextcloud.nextcloud import run_cli as nextcloud_run_cli

        if module == 'notes':
            from modules.nextcloud.notes import setup_parser
            import argparse
            parser = argparse.ArgumentParser(prog='nexlink notes')
            subparsers = parser.add_subparsers(dest='notes_command')
            setup_parser(subparsers)
            try:
                parsed = parser.parse_args(args)
                if hasattr(parsed, 'func'):
                    parsed.func(parsed)
                else:
                    parser.print_help()
                    sys.exit(1)
            except SystemExit as e:
                sys.exit(e.code if isinstance(e.code, int) else 1)
            return

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
NexLink - Unified CLI for Email, Calendar, Tasks, and Files

Usage:
    nexlink <module> <command> [options]

Modules:
    mail        Email operations (Exchange)
    cal         Calendar operations (Exchange)
    tasks       Task management (Exchange)
    analytics   Email analytics and statistics (Exchange)
    sync        Task sync and reminders (Exchange)
    files       File operations (Nextcloud)

Email Commands:
    nexlink mail connect              Test Exchange connection
    nexlink mail read [--folder FOLDER] [--limit N] [--unread]
    nexlink mail send --to EMAIL --subject SUBJECT --body BODY
    nexlink mail reply --id EMAIL_ID --body BODY
    nexlink mail forward --id EMAIL_ID --to EMAIL

Calendar Commands:
    nexlink cal today                 Show today's events
    nexlink cal week                  Show this week's events
    nexlink cal list [--days N]
    nexlink cal create --subject SUBJECT --start DATETIME [--duration MIN]

Task Commands:
    nexlink tasks list [--overdue] [--status STATUS]
    nexlink tasks create --subject SUBJECT [--due DATE] [--priority LEVEL]
    nexlink tasks complete --id TASK_ID
    nexlink tasks trash --id TASK_ID

Sync Commands:
    nexlink sync sync                 Sync tasks with Exchange
    nexlink sync status               Show sync status
    nexlink sync reminders [--hours N] [--dry-run]

Analytics Commands:
    nexlink analytics stats --days N     Email statistics
    nexlink analytics response-time      Response time analysis
    nexlink analytics top-senders        Top senders by count
    nexlink analytics heatmap            Activity heatmap
    nexlink analytics folders            Folder statistics
    nexlink analytics report             Full analytics report

File Commands:
    nexlink files list [PATH] [--recursive] List files in directory
    nexlink files search QUERY [PATH]       Search files/folders by name
    nexlink files extract-text PATH         Extract readable text from one file
    nexlink files summarize PATH            Summarize one file
    nexlink files ask-file PATH QUESTION    Answer a question from one file
    nexlink files extract-actions PATH      Extract workflow actions from one file
    nexlink files create-tasks-from-file PATH [--mailbox EMAIL] [--priority LEVEL] [--select 1,2] [--execute]
    nexlink files upload LOCAL REMOTE       Upload file to Nextcloud
    nexlink files download REMOTE LOCAL     Download file from Nextcloud
    nexlink files mkdir PATH                Create directory
    nexlink files delete PATH               Delete file or directory
    nexlink files move OLD NEW              Move/rename file
    nexlink files copy SRC DEST             Copy file
    nexlink files info PATH                 Get file info
    nexlink files shared                    List items shared with current user
    nexlink files share-create PATH [--password VALUE] [--expire-date YYYY-MM-DD] [--public-upload]
    nexlink files share-list [PATH]         List public share links
    nexlink files share-revoke SHARE_ID     Revoke public share link

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
    nexlink mail send --to client@example.com --subject "Offer" --body "Please find attached..."

    # Create calendar event
    nexlink cal create --subject "Meeting" --start "2024-01-15 14:00" --duration 60

    # Create task
    nexlink tasks create --subject "Follow-up" --due "+7d" --priority high

    # Upload file to Nextcloud
    nexlink files upload /local/report.pdf /Documents/

    # Search files in Nextcloud
    nexlink files search contract /Clients/

    # Extract / summarize / ask a file
    nexlink files extract-text /Clients/contract.docx
    nexlink files summarize /Clients/contract.docx
    nexlink files ask-file /Clients/contract.docx When is the renewal due?

    # Extract workflow actions and preview/create tasks
    nexlink files extract-actions /Clients/contract.txt
    nexlink files create-tasks-from-file /Clients/contract.txt
    nexlink files create-tasks-from-file /Clients/contract.txt --select 1,2 --execute

    # Create a share link
    nexlink files share-create /Contracts/offer.pdf --expire-date 2026-04-30

For more information, see references/setup.md
""")


if __name__ == '__main__':
    main()