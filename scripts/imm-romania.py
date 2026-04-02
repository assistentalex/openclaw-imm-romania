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
        # Route to Nextcloud module
        from modules.nextcloud.nextcloud import NextcloudClient
        if len(args) < 1:
            print("Error: No command specified for files.")
            print("Available commands: list, upload, download, mkdir, delete, move, copy, info")
            sys.exit(1)

        client = NextcloudClient()
        command = args[0]
        command_args = args[1:]

        # Map commands to methods
        if command == 'list':
            path = command_args[0] if command_args else '/'
            results = client.list(path)
            if results:
                from modules.nextcloud.nextcloud import print_list
                print_list(results)
            else:
                print("(empty)")
        elif command == 'upload':
            if len(command_args) < 2:
                print("Error: upload requires <local_file> <remote_path>")
                sys.exit(1)
            client.upload(command_args[0], command_args[1])
        elif command == 'download':
            if len(command_args) < 2:
                print("Error: download requires <remote_file> <local_dir>")
                sys.exit(1)
            client.download(command_args[0], command_args[1])
        elif command == 'mkdir':
            if len(command_args) < 1:
                print("Error: mkdir requires <remote_path>")
                sys.exit(1)
            client.mkdir(command_args[0])
        elif command == 'delete':
            if len(command_args) < 1:
                print("Error: delete requires <remote_path>")
                sys.exit(1)
            client.delete(command_args[0])
        elif command == 'move':
            if len(command_args) < 2:
                print("Error: move requires <old_path> <new_path>")
                sys.exit(1)
            client.move(command_args[0], command_args[1])
        elif command == 'copy':
            if len(command_args) < 2:
                print("Error: copy requires <source_path> <dest_path>")
                sys.exit(1)
            client.copy(command_args[0], command_args[1])
        elif command == 'info':
            if len(command_args) < 1:
                print("Error: info requires <remote_path>")
                sys.exit(1)
            client.info(command_args[0])
        else:
            print(f"Error: Unknown files command: {command}")
            sys.exit(1)

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
    imm-romania files list [PATH]         List files in directory
    imm-romania files upload LOCAL REMOTE Upload file to Nextcloud
    imm-romania files download REMOTE LOCAL Download file from Nextcloud
    imm-romania files mkdir PATH          Create directory
    imm-romania files delete PATH         Delete file or directory
    imm-romania files move OLD NEW       Move/rename file
    imm-romania files copy SRC DEST       Copy file

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

For more information, see references/setup.md
""")


if __name__ == '__main__':
    main()