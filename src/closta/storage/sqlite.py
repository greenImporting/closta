# use sqlite3 to save task name, description, importance
import sqlite3
import dearpygui.dearpygui as dpg

db_name = 'closta.db'

def init_db():
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute(''' CREATE TABLE IF NOT EXISTS tasks
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            importance INTEGER)''')

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