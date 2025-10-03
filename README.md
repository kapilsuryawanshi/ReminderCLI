# Reminder CLI Application

A lightweight command-line reminder management application built in Python. This tool is designed to be simple to use, with low cognitive load, and effective for students or employees during work hours.

## Features

- Command-line interface for easy use
- Stores all data in a local SQLite database
- Supports timed reminders (hh:mm format)
- Supports duration-based reminders (Nm for minutes, Nh for hours)
- Reminder daemon that runs in the background
- Interactive dialog for handling reminders
- Ability to remove, snooze, or repeat reminders
- Daemon crash detection with error message popups
- Graceful error handling to allow daemon to continue running after errors
- When run without arguments, defaults to list command
- Timestamps show only time when date is today, otherwise show full date and time
- Status column shown at the end of the list table
- The 'pause' functionality has been removed
- Uses static daemon script instead of generating it dynamically

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

The application is run as a command-line program:

```bash
reminder [command] [arguments...]
```

### Commands

#### `reminder` or `reminder list`
Lists all existing reminders, showing:
- Reminder ID
- Message
- Duration
- Scheduled time (shows only time when today, otherwise shows full date and time)
- Last shown time (shows only time when today, otherwise shows full date and time)
- Status (Active, Snoozed until [time]) shown at the end
- Daemon status (Active/Inactive)

When run with no arguments, defaults to the list command.

#### `reminder start`
Starts the reminder daemon process in the background.
The daemon will run as a separate process and show reminder dialogs as appropriate.

#### `reminder stop`
Stops the reminder daemon process.

#### `reminder add <reminder text> <hh:mm|Nm|Nh>`
Registers a new reminder with:
- `<reminder text>`: The reminder message
- `<hh:mm>`: Time in 24-hour format (e.g., 10:30)
- `<Nm>`: Number of minutes to wait (N between 1-500, e.g., 5m)
- `<Nh>`: Number of hours to wait (N between 1-24, e.g., 2h)

Examples:
```bash
reminder add "Meeting with team" 14:30
reminder add "Take a break" 15m
reminder add "Finish project" 2h
```

#### `reminder remove <id>[,<id>,...]`
Removes reminders using comma-separated reminder IDs.

Example:
```bash
reminder remove 1,2,5
```

### Reminder Behavior

When the application daemon determines that a reminder should be shown, a modal dialog appears with:
- Reminder message
- Reminder duration/time setting
- Last time the reminder was shown
- Future reminder time (if repeated)

The dialog includes these buttons:
- **Remove**: Dismisses the reminder and prevents it from showing again
- **Snooze for 5 min**: Dismisses the reminder and shows it again after 5 minutes
- **Repeat**: Dismisses the reminder but repeats it after the original duration or at the original time

### Daemon Error Handling

The daemon includes crash detection and error handling:
- If the daemon encounters an error, it displays an error popup to notify the user
- The daemon attempts to continue running after most errors
- If there is a fatal error, a popup is shown before the daemon exits
- The daemon will automatically retry after errors with a short delay

## Project Structure

- `reminder.py`: Main entry point and command-line interface
- `database.py`: SQLite database operations with proper resource management
- `reminder_daemon.py`: Background daemon process with error handling
- `reminder_dialog.py`: Modal dialog implementation
- `requirements.txt`: Python dependencies
- `PRD.txt`: Product Requirements Document
- `README.md`: This documentation file

## Example Usage

```bash
# Add a reminder to take a break in 10 minutes
reminder add "Take a break" 10m

# List all reminders (can be run as just 'reminder')
reminder

# Start the daemon to show reminders
reminder start

# Remove a reminder with ID 1
reminder remove 1

# Stop the daemon
reminder stop
```

## Requirements

- Python 3.6 or higher
- psutil library
- tkinter (part of standard Python installation)
- SQLite (comes with Python)

## Database and Resource Management

- All database operations use 'with' statements for proper resource management
- All database operations use conn.execute() method for better connection handling
- The database automatically updates expired snoozed reminders to active status
- The application maintains data consistency by updating statuses appropriately