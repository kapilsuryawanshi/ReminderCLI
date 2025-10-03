"""
Reminder Dialog Module
This module handles the modal dialog windows for displaying reminders.
"""
import tkinter as tk
from tkinter import messagebox
from datetime import datetime


def show_reminder_dialog(message, duration, last_shown, scheduled_time):
    """
    Show a modal reminder dialog with the reminder information and action buttons.
    
    Args:
        message: The reminder message
        duration: The original duration/time setting
        last_shown: When the reminder was last shown
        scheduled_time: When the reminder is scheduled for
        
    Returns:
        String indicating the user action: "stop" (when Remove button is clicked), "snooze", or "repeat"
    """
    root = tk.Tk()
    root.title("Reminder")
    
    # Make the window stay on top
    root.attributes('-topmost', True)
    
    # Center the window on the screen
    window_width = 400
    window_height = 300
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f'{window_width}x{window_height}+{x}+{y}')
    
    # Create and pack the widgets
    message_label = tk.Label(root, text=message, wraplength=350, font=("Arial", 12))
    message_label.pack(pady=20)
    
    # Display reminder info
    info_text = f"Duration/Time: {duration}\n"
    if last_shown:
        info_text += f"Last shown: {last_shown}\n"
    else:
        info_text += "Last shown: Never\n"
    info_text += f"Scheduled for: {scheduled_time}"
    
    info_label = tk.Label(root, text=info_text, justify=tk.LEFT)
    info_label.pack(pady=10)
    
    # Store the result of the dialog
    result = {"action": None}
    
    def on_remove():
        result["action"] = "stop"  # Keep "stop" as the action identifier since daemon expects it
        root.destroy()
    
    def on_snooze():
        result["action"] = "snooze"
        root.destroy()
    
    def on_repeat():
        result["action"] = "repeat"
        root.destroy()
    
    # Create buttons frame
    button_frame = tk.Frame(root)
    button_frame.pack(pady=20)
    
    # Create buttons
    remove_button = tk.Button(button_frame, text="Remove", command=on_remove, width=10)
    remove_button.pack(side=tk.LEFT, padx=5)
    
    snooze_button = tk.Button(button_frame, text="Snooze for 5 min", command=on_snooze, width=15)
    snooze_button.pack(side=tk.LEFT, padx=5)
    
    repeat_button = tk.Button(button_frame, text="Repeat", command=on_repeat, width=10)
    repeat_button.pack(side=tk.LEFT, padx=5)
    
    # Wait for the window to be destroyed
    root.mainloop()
    
    # Return the action taken by the user
    return result["action"]


if __name__ == "__main__":
    # Test the dialog
    action = show_reminder_dialog("Test message", "10:30", "2023-01-01 10:00:00", "2023-01-01 10:30:00")
    print(f"User action: {action}")