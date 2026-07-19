# use sqlite3 to save task name, description, importance
import sqlite3

db_name = 'closta.db'

def init_db():
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute(
        ''' CREATE TABLE IF NOT EXISTS tasks
            (id INTEGER PRIMARY KEY AUTOINCREMEMNT,
            name TEXT NOT NULL
            description TEXT,
            importance INTEGER)'''
        )

    conn.commit()
    conn.close()

def save_task(name, description=None, importance=0):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute('INSERT INTO tasks (name, description, importance) values (?, ?, ?)',
              (name, description, importance)
    )

    conn.commit()
    conn.close()
    
def load_tasks():
    conn = sqlite3.connect(db_name)
    c = conn.cursor()     

    c.execute('SELECT id, name, description, importance FROM tasks')
    rows = c.fetchall()

    conn.close()

    for row in rows:
        build_task(row[0], row[1], row[2], row[3])

def delete_callback(sender, app_data, usr_data):
    task_id = usr_data
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute('DELETE FROM tasks WHERE id = ?', (task_id,))

    conn.commit()
    conn.close()

    dpg.delete_item(dpg.get_parent(sender))