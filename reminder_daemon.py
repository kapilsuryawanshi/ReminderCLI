#!/usr/bin/env python3
"""
Reminder Daemon
This script runs in the background to check and display reminders.
"""
import time
import sqlite3
from datetime import datetime
from reminder_dialog import show_reminder_dialog
from database import ReminderDatabase


def main():
    """Main daemon loop."""
    print("Reminder daemon started. Press Ctrl+C to stop.")
    
    try:
        while True:
            try:
                # Reinitialize database connection in each loop to handle potential connection issues
                db = ReminderDatabase()
                
                # Check for active reminders that should be shown now
                active_reminders = db.get_active_reminders()
                
                for reminder in active_reminders:
                    try:
                        rid, message, scheduled_time, last_shown, status, snooze_until, duration = reminder
                        
                        # Show the reminder dialog
                        result = show_reminder_dialog(message, duration, last_shown, scheduled_time)
                        
                        # Handle the user action
                        if result == "stop":
                            # Remove the reminder
                            db.remove_reminder(rid)
                        elif result == "snooze":
                            # Snooze for 5 minutes
                            from datetime import datetime, timedelta
                            snooze_until = datetime.now() + timedelta(minutes=5)
                            db.update_reminder_times(rid, last_shown=datetime.now(), snooze_until=snooze_until)
                            db.update_reminder_status(rid, "snoozed")
                        elif result == "repeat":
                            # Calculate next occurrence based on original duration
                            from datetime import datetime, timedelta
                            import re
                            
                            if ":" in duration:  # Time format (hh:mm)
                                hour, minute = map(int, duration.split(":"))
                                now = datetime.now()
                                next_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                                if next_time <= now:
                                    next_time += timedelta(days=1)
                                db.update_reminder_times(rid, last_shown=datetime.now(), scheduled_time=next_time)
                            elif duration.lower().endswith("m"):  # Minutes format (Nm)
                                minutes = int(duration[:-1])
                                next_time = datetime.now() + timedelta(minutes=minutes)
                                db.update_reminder_times(rid, last_shown=datetime.now(), scheduled_time=next_time)
                            elif duration.lower().endswith("h"):  # Hours format (Nh)
                                hours = int(duration[:-1])
                                next_time = datetime.now() + timedelta(hours=hours)
                                db.update_reminder_times(rid, last_shown=datetime.now(), scheduled_time=next_time)
                    except Exception as e:
                        print(f"Error processing reminder: {e}")
                        # Continue with next reminder instead of stopping the entire daemon
                        continue
            
            except Exception as e:
                print(f"Error in daemon loop: {e}")
                # Show error popup
                try:
                    import tkinter as tk
                    from tkinter import messagebox
                    root = tk.Tk()
                    root.withdraw()  # Hide the main window
                    messagebox.showerror("Reminder Daemon Error", f"The reminder daemon encountered an error:\n{str(e)}\n\nThe daemon will attempt to continue running.")
                    root.destroy()
                except:
                    # If tkinter fails, just continue
                    pass
                # Wait a bit before trying again to avoid rapid error loops
                time.sleep(10)
                continue
            
            # Sleep for a short period before checking again
            time.sleep(30)  # Check every 30 seconds

    except KeyboardInterrupt:
        print("\nReminder daemon stopped by user.")
        return
    except Exception as e:
        # Show error popup for unexpected errors
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            messagebox.showerror("Reminder Daemon Fatal Error", f"The reminder daemon encountered a fatal error:\n{str(e)}\n\nDaemon will now exit.")
            root.destroy()
        except:
            print(f"Reminder daemon encountered a fatal error: {e}")
        return


if __name__ == "__main__":
    main()
