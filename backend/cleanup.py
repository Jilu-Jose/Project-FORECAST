import sqlite3
conn = sqlite3.connect('forecast.db')
conn.execute("UPDATE audit_runs SET status='error', error_message='Interrupted by server restart' WHERE status='running'")
conn.commit()
conn.close()
