# Reminder CLI Application

A lightweight command-line reminder management application built in Python. This tool is designed to be simple to use, with low cognitive load, and effective for students or employees during work hours.

## Features

- Command-line interface for easy use
- Stores all data in a local SQLite database
- Supports timed reminders (hh:mm format)
- Supports duration-based reminders (Nm for minutes, Nh for hours)
- Reminder daemon that runs in the background
- Interactive dialog for handling reminders
- Ability to stop, snooze, or repeat reminders
- Pause and remove reminders

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

#### `reminder list`
Lists all existing reminders, showing:
- Reminder ID
- Message
- Scheduled time
- Last shown time
- Status (including if snoozed)
- Duration setting
- Daemon status (Active/Inactive)

#### `reminder start`
Starts the reminder daemon process in the background.

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

#### `reminder pause <id>[,<id>,...]`
Pauses reminders using comma-separated reminder IDs.

Example:
```bash
reminder pause 3,7
```

### Reminder Behavior

When the application daemon determines that a reminder should be shown, a modal dialog appears with:
- Reminder message
- Reminder duration/time setting
- Last time the reminder was shown
- Future reminder time (if repeated)

The dialog includes these buttons:
- **Stop**: Dismisses the reminder and prevents it from showing again
- **Snooze for 5 min**: Dismisses the reminder and shows it again after 5 minutes
- **Repeat**: Dismisses the reminder but repeats it after the original duration or at the original time

## Project Structure

- `reminder.py`: Main entry point and command-line interface
- `database.py`: SQLite database operations
- `reminder_daemon.py`: Background daemon process
- `reminder_dialog.py`: Modal dialog implementation
- `requirements.txt`: Python dependencies

## Example Usage

```bash
# Add a reminder to take a break in 10 minutes
reminder add "Take a break" 10m

# List all reminders
reminder list

# Start the daemon to show reminders
reminder start

# Pause a reminder with ID 2
reminder pause 2

# Remove a reminder with ID 1
reminder remove 1
```

## Requirements

- Python 3.6 or higher
- psutil library
- tkinter (part of standard Python installation)
- SQLite (comes with Python)