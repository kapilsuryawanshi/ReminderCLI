"""
Database module for the reminder application.
Handles SQLite database operations for storing and managing reminders.
"""
import sqlite3
import os
from datetime import datetime
import re


class ReminderDatabase:
    def __init__(self, db_path=None):
        """Initialize the database connection."""
        if db_path is None:
            # Use a default database file in the user's home directory
            db_path = os.path.join(os.path.expanduser("~"), ".reminders.db")
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize the database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            # Create reminders table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message TEXT NOT NULL,
                    scheduled_time TIMESTAMP,
                    last_shown TIMESTAMP,
                    status TEXT DEFAULT 'active',  -- 'active', 'snoozed'
                    snooze_until TIMESTAMP,
                    duration TEXT,  -- stores the original duration format (e.g. '5m', '1h', '10:30')
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

    def add_reminder(self, message, scheduled_time, duration):
        """Add a new reminder to the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO reminders (message, scheduled_time, duration)
                VALUES (?, ?, ?)
            ''', (message, scheduled_time, duration))

            reminder_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            return reminder_id

    def get_all_reminders(self):
        """Retrieve all reminders from the database.
        Also updates the status of any expired snoozed reminders and paused reminders back to active."""
        with sqlite3.connect(self.db_path) as conn:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Update any snoozed reminders that have expired to be active again
            conn.execute('''
                UPDATE reminders 
                SET status = 'active', snooze_until = NULL
                WHERE status = 'snoozed' 
                AND snooze_until IS NOT NULL 
                AND snooze_until <= ?
            ''', (now,))
            
            # Update any paused reminders to active (since pause functionality is removed)
            conn.execute('''
                UPDATE reminders
                SET status = 'active'
                WHERE status = 'paused'
            ''')
            
            result = conn.execute('''
                SELECT id, message, scheduled_time, last_shown, status, snooze_until, duration
                FROM reminders
                ORDER BY scheduled_time
            ''')

            return result.fetchall()

    def get_reminder_by_id(self, reminder_id):
        """Get a specific reminder by ID.
        Also updates the status of any expired snoozed reminders and paused reminders back to active."""
        with sqlite3.connect(self.db_path) as conn:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Update any snoozed reminders that have expired to be active again
            conn.execute('''
                UPDATE reminders 
                SET status = 'active', snooze_until = NULL
                WHERE status = 'snoozed' 
                AND snooze_until IS NOT NULL 
                AND snooze_until <= ?
            ''', (now,))
            
            # Update any paused reminders to active (since pause functionality is removed)
            conn.execute('''
                UPDATE reminders
                SET status = 'active'
                WHERE status = 'paused'
            ''')
            
            result = conn.execute('''
                SELECT id, message, scheduled_time, last_shown, status, snooze_until, duration
                FROM reminders
                WHERE id = ?
            ''', (reminder_id,))

            return result.fetchone()

    def remove_reminder(self, reminder_id):
        """Remove a reminder by ID."""
        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute('DELETE FROM reminders WHERE id = ?', (reminder_id,))
            return result.rowcount > 0

    

    def update_reminder_status(self, reminder_id, status):
        """Update the status of a reminder."""
        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute('''
                UPDATE reminders 
                SET status = ?
                WHERE id = ?
            ''', (status, reminder_id))
            
            return result.rowcount > 0

    def update_reminder_times(self, reminder_id, last_shown=None, scheduled_time=None, snooze_until=None):
        """Update times for a reminder."""
        with sqlite3.connect(self.db_path) as conn:
            # Build the update query based on provided parameters
            fields = []
            values = []

            if last_shown is not None:
                fields.append('last_shown = ?')
                values.append(last_shown)

            if scheduled_time is not None:
                fields.append('scheduled_time = ?')
                values.append(scheduled_time)

            if snooze_until is not None:
                fields.append('snooze_until = ?')
                values.append(snooze_until)

            if fields:
                query = f"UPDATE reminders SET {', '.join(fields)} WHERE id = ?"
                values.append(reminder_id)
                
                result = conn.execute(query, values)
                return result.rowcount > 0
            else:
                return False

    def get_active_reminders(self):
        """Get all active reminders (snoozed until after now).
        Also updates the status of any expired snoozed reminders back to active."""
        with sqlite3.connect(self.db_path) as conn:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Update any snoozed reminders that have expired to be active again
            conn.execute('''
                UPDATE reminders 
                SET status = 'active', snooze_until = NULL
                WHERE status = 'snoozed' 
                AND snooze_until IS NOT NULL 
                AND snooze_until <= ?
            ''', (now,))
            
            result = conn.execute('''
                SELECT id, message, scheduled_time, last_shown, status, snooze_until, duration
                FROM reminders
                WHERE (snooze_until IS NULL OR snooze_until <= ?)
                AND scheduled_time <= ?
            ''', (now, now))

            return result.fetchall()