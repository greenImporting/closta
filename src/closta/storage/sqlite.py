import sqlite3
import dearpygui.dearpygui as dpg

db_name = 'closta.db'

def init_db():
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    # tasks 
    c.execute(''' CREATE TABLE IF NOT EXISTS tasks
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            importance INTEGER)''')

    # settings
    c.execute('''CREATE TABLE IF NOT EXISTS settings
            (key STRING PRIMARY KEY, value TEXT)''')

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

def edit_task(name, description, importance, task_id):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute('UPDATE tasks SET name=?, description=?, importance=? WHERE id=?',
             (name,description,importance,task_id)
    ) 

    conn.commit()
    conn.close()

def get_setting(key, default=None):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute('SELECT value FROM settings WHERE key=?', (key,))
    row = c.fetchone()

    conn.close()
    return row[0] if row else default

def save_setting(key, value):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute('REPLACE INTO settings (key, value) VALUES (?, ?)', (key, str(value)))

    conn.commit()
    conn.close()
    
def delete_callback(sender, app_data, usr_data):
    task_id = usr_data
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute('DELETE FROM tasks WHERE id = ?', (task_id,))

    conn.commit()
    conn.close()

    parent_group = dpg.get_item_parent(sender)
    task_window = dpg.get_item_parent(parent_group)
    dpg.delete_item(task_window)