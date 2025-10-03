from database import ReminderDatabase
db = ReminderDatabase()
reminders = db.get_all_reminders()
print(f'Database returned {len(reminders)} reminders')
for r in reminders:
    print(f'ID: {r[0]}, Message: {r[1][:20]}...')