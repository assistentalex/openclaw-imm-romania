#!/bin/bash

# Contract Renewal Reminder Script
# Runs daily to check for clients needing contract renewal
# and sends email notification via Exchange

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
MSP_CLI="$PROJECT_DIR/modules/msp/cli.py"

# Set Exchange environment variables (if not already set)
export EXCHANGE_SERVER="${EXCHANGE_SERVER:-https://autoconfig.firmade.it/EWS/Exchange.asmx}"
export EXCHANGE_USERNAME="${EXCHANGE_USERNAME:-asistent.alex}"
export EXCHANGE_PASSWORD="${EXCHANGE_PASSWORD:-P@ssw0rdrobot}"
export EXCHANGE_EMAIL="${EXCHANGE_EMAIL:-asistent.alex@firmade.it}"

# Set MSP reminder recipient
export MSP_REMINDER_EMAIL="${MSP_REMINDER_EMAIL:-alex.bogdan@firmade.it}"

# Run the check
python3 "$MSP_CLI" reminders check

exit $?