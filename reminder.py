#!/usr/bin/env python3
"""
Reminder CLI Application
A lightweight command-line reminder management application.
"""

import argparse
import sys
from datetime import datetime, timedelta
import re

from database import ReminderDatabase


def parse_time_input(time_input):
    """Parse time input in various formats: hh:mm, Nm, Nh"""
    # Check if it's in hh:mm format
    if re.match(r"^\d{1,2}:\d{2}$", time_input):
        hour, minute = map(int, time_input.split(":"))
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            now = datetime.now()
            scheduled_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            # If the time has already passed today, schedule for tomorrow
            if scheduled_time <= now:
                scheduled_time += timedelta(days=1)
            return scheduled_time, time_input
        else:
            raise ValueError("Invalid time format. Hours must be 0-23, minutes 0-59.")
    # Check if it's in Nm format (minutes)
    elif re.match(r"^\d{1,3}m$", time_input.lower()):
        minutes = int(time_input[:-1])
        if 1 <= minutes <= 500:
            scheduled_time = datetime.now() + timedelta(minutes=minutes)
            return scheduled_time, time_input
        else:
            raise ValueError("Minutes must be between 1 and 500.")
    # Check if it's in Nh format (hours)
    elif re.match(r"^\d{1,2}h$", time_input.lower()):
        hours = int(time_input[:-1])
        if 1 <= hours <= 24:
            scheduled_time = datetime.now() + timedelta(hours=hours)
            return scheduled_time, time_input
        else:
            raise ValueError("Hours must be between 1 and 24.")
    else:
        raise ValueError("Invalid time format. Use hh:mm, Nm, or Nh.")


def calculate_remaining_time(scheduled_time_str):
    """Calculate remaining time from scheduled time string and return formatted string (e.g. '1h 14m' or '33m')"""
    if not scheduled_time_str:
        return "N/A"
    
    try:
        # Parse the scheduled time string to datetime object
        scheduled_dt = datetime.fromisoformat(scheduled_time_str.replace('Z', '+00:00')) if scheduled_time_str else None
        if not scheduled_dt:
            return "N/A"
        
        # Get current time
        now = datetime.now()
        
        # Calculate the difference
        time_diff = scheduled_dt - now
        
        # If the scheduled time is in the past, return 'Overdue' or just '0m'
        if time_diff.total_seconds() <= 0:
            return "Due"
        
        # Calculate hours and minutes
        total_seconds = int(time_diff.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        
        # Format the output
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    except:
        return "N/A"


def main():
    """Main entry point for the reminder application."""
    parser = argparse.ArgumentParser(
        prog="reminder",
        description="A lightweight command-line reminder management application"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new reminder")
    add_parser.add_argument("message", nargs="+", help="Reminder message")
    add_parser.add_argument("time", help="Time in format hh:mm, Nm (minutes), or Nh (hours)")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all reminders")
    
    # Start/Stop commands
    start_parser = subparsers.add_parser("start", help="Start the reminder daemon")
    stop_parser = subparsers.add_parser("stop", help="Stop the reminder daemon")
    
    # Remove command
    remove_parser = subparsers.add_parser("remove", help="Remove reminder(s) by ID")
    remove_parser.add_argument("ids", help="Comma-separated list of reminder IDs to remove")
    
    
    
    args = parser.parse_args()

    # Initialize database
    db = ReminderDatabase()

    # Handle different commands
    # If no command is provided, default to list
    if not args.command:
        list_reminders(db)
    elif args.command == "list":
        list_reminders(db)
    elif args.command in ["start", "stop"]:
        start_stop_daemon(args.command, db)
    elif args.command == "add":
        message = " ".join(args.message)
        add_reminder(db, message, args.time)
    elif args.command == "remove":
        remove_reminders(db, args.ids)
    
    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()
        sys.exit(1)


def remove_reminders(db, ids_str):
    """Remove reminders by IDs."""
    if not ids_str:
        print("Error: Please provide reminder ID(s) to remove.")
        return
        
    try:
        # Parse comma-separated IDs
        ids = [int(id.strip()) for id in ids_str.split(',')]
        
        # Remove each reminder
        removed_count = 0
        for reminder_id in ids:
            if db.remove_reminder(reminder_id):
                print(f"Reminder {reminder_id} removed successfully")
                removed_count += 1
            else:
                print(f"Reminder {reminder_id} not found")
        
        if removed_count == 0:
            print("No reminders were removed")
        else:
            print(f"Successfully removed {removed_count} reminder(s)")
            
    except ValueError:
        print("Error: Invalid ID format. Use comma-separated integers (e.g., 1,2,5).")
        sys.exit(1)


def add_reminder(db, message, time_input):
    """Add a new reminder."""
    try:
        scheduled_time, duration = parse_time_input(time_input)
        reminder_id = db.add_reminder(message, scheduled_time.strftime("%Y-%m-%d %H:%M:%S"), duration)
        print(f"Reminder added with ID: {reminder_id}")
        print(f"Message: {message}")
        print(f"Scheduled for: {scheduled_time.strftime("%Y-%m-%d %H:%M:%S")}")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


def list_reminders(db):
    """List all reminders."""
    reminders = db.get_all_reminders()
    
    if not reminders:
        print("No reminders found.")
    else:
        print(f"{'ID':<3} {'Message':<30} {'Duration':<10} {'Scheduled Time':<20} {'Remaining Time':<15} {'Last Shown':<20} {'Status':<25}")
        print("-" * 133)
        
        for reminder in reminders:
            rid, message, scheduled_time, last_shown, status, snooze_until, duration = reminder
            message_truncated = (message[:27] + "...") if len(message) > 30 else message
            
            # Format timestamps to show only date and time (yyyy-mm-dd hh:mm), or just time if today
            from datetime import datetime
            today = datetime.now().date()
            try:
                scheduled_dt = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00')) if scheduled_time else None
                if scheduled_dt:
                    if scheduled_dt.date() == today:
                        scheduled_time_str = scheduled_dt.strftime('%H:%M')
                    else:
                        scheduled_time_str = scheduled_dt.strftime('%Y-%m-%d %H:%M')
                else:
                    scheduled_time_str = scheduled_time
            except:
                scheduled_time_str = scheduled_time.split('.')[0] if scheduled_time and '.' in scheduled_time else scheduled_time
                # Try to check if the date part is today
                if scheduled_time_str and ' ' in scheduled_time_str:
                    date_part = scheduled_time_str.split(' ')[0]
                    try:
                        date_obj = datetime.strptime(date_part, '%Y-%m-%d').date()
                        if date_obj == today:
                            scheduled_time_str = scheduled_time_str.split(' ', 1)[1]  # Just the time part
                    except:
                        pass  # Keep original if parsing fails
            
            # Calculate remaining time
            remaining_time_str = calculate_remaining_time(scheduled_time)
            
            if last_shown:
                try:
                    last_shown_dt = datetime.fromisoformat(last_shown.replace('Z', '+00:00')) if last_shown else None
                    if last_shown_dt:
                        if last_shown_dt.date() == today:
                            last_shown_str = last_shown_dt.strftime('%H:%M')
                        else:
                            last_shown_str = last_shown_dt.strftime('%Y-%m-%d %H:%M')
                    else:
                        last_shown_str = last_shown
                except:
                    last_shown_str = last_shown.split('.')[0] if '.' in last_shown else last_shown
                    # Try to check if the date part is today
                    if ' ' in last_shown_str:
                        date_part = last_shown_str.split(' ')[0]
                        try:
                            date_obj = datetime.strptime(date_part, '%Y-%m-%d').date()
                            if date_obj == today:
                                last_shown_str = last_shown_str.split(' ', 1)[1]  # Just the time part
                        except:
                            pass  # Keep original if parsing fails
            else:
                last_shown_str = "Never"
            
            # Determine status display and put it at the end
            if snooze_until:
                # Check if snooze is still in effect or has expired
                from datetime import datetime
                now = datetime.now()
                try:
                    snooze_dt = datetime.fromisoformat(snooze_until.replace('Z', '+00:00')) if snooze_until else None
                    if snooze_dt and now <= snooze_dt:
                        # Still snoozed
                        if snooze_dt.date() == today:
                            status_display = f"Snoozed until {snooze_dt.strftime('%H:%M')}"
                        else:
                            status_display = f"Snoozed until {snooze_until.split('.')[0] if snooze_until and '.' in snooze_until else snooze_until}"
                    else:
                        # Snooze has expired, should be active now (database will update this)
                        status_display = "Active"
                except:
                    # If parsing fails, default to showing as snoozed if there's a value
                    if snooze_until:
                        status_display = f"Snoozed until {snooze_until.split('.')[0] if snooze_until else snooze_until}"
                    else:
                        status_display = status.title()
            else:
                status_display = status.title()
            
            print(f"{rid:<3} {message_truncated:<30} {duration:<10} {scheduled_time_str:<20} {remaining_time_str:<15} {last_shown_str:<20} {status_display:<25}")
    
    # Check daemon status
    import os
    import psutil
    lock_file = os.path.join(os.path.expanduser("~"), ".reminder_daemon.pid")
    
    if os.path.exists(lock_file):
        with open(lock_file, 'r') as f:
            try:
                pid = int(f.read().strip())
                proc = psutil.Process(pid)
                if proc.is_running():
                    daemon_status = "Active"
                else:
                    daemon_status = "Inactive"
            except (psutil.NoSuchProcess, psutil.AccessDenied, ValueError):
                daemon_status = "Inactive"
    else:
        daemon_status = "Inactive"
    
    print(f"\nDaemon Status: {daemon_status}")

def start_stop_daemon(command, db):
    """Start or stop the daemon."""
    import os
    import subprocess
    import psutil
    
    # Define a lock file to track daemon status
    lock_file = os.path.join(os.path.expanduser("~"), ".reminder_daemon.pid")
    
    if command == "start":
        # Check if daemon is already running
        if os.path.exists(lock_file):
            with open(lock_file, "r") as f:
                pid = int(f.read().strip())
            try:
                # Check if the process is actually running
                proc = psutil.Process(pid)
                if proc.is_running():
                    print("Reminder daemon is already running")
                    return
            except (psutil.NoSuchProcess, psutil.AccessDenied, ValueError):
                # Process doesn't exist, remove stale lock file
                os.remove(lock_file)
        
        # Start the daemon
        daemon_script = os.path.join(os.path.dirname(__file__), "reminder_daemon.py")
        
        # Check that the daemon script exists (it should be part of the project)
        if not os.path.exists(daemon_script):
            print(f"Error: Daemon script {daemon_script} not found!")
            sys.exit(1)
        
        # Start the daemon process in the background
        # Use STARTUPINFO to hide the window on Windows
        startupinfo = None
        if os.name == 'nt':  # Windows
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

        process = subprocess.Popen(
            ['python', daemon_script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            startupinfo=startupinfo
        )
        print(f"Reminder daemon started with PID: {process.pid}")
        
        # Write PID to lock file
        with open(lock_file, 'w') as f:
            f.write(str(process.pid))
    
    elif command == "stop":
        # Stop the daemon
        if os.path.exists(lock_file):
            with open(lock_file, "r") as f:
                pid = int(f.read().strip())
            
            try:
                proc = psutil.Process(pid)
                proc.terminate()
                proc.wait(timeout=5)  # Wait up to 5 seconds for graceful shutdown
                print("Reminder daemon stopped")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                print("Error: Could not stop the daemon process")
            except ValueError:
                print("Error: Invalid PID in lock file")
            
            # Remove the lock file
            os.remove(lock_file)
        else:
            print("Reminder daemon is not running")


if __name__ == "__main__":
    main()
