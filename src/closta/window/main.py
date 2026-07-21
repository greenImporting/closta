import dearpygui.dearpygui as dpg
import pywinctl as pwc
import sqlite3
import threading
import time
import logging
import pymonctl
from closta import state
from closta.storage.sqlite import delete_callback, save_task, init_db, db_name, edit_task, get_setting, save_setting
from pathlib import Path

logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")


_lock = threading.Lock()
"""

current issues.
- TODO: fix close then reopen when clicking on tray icon after 1sec debounce.
    i guess this happens becuase you unfocus, closing it, then reopen from left clicking on tray.
- if you are lookign through this code im so sorry.
- 

"""
def newbie_checker():
    # checks if youre new. if so, init db. TODO: give lovely welcome message.
    db_path = Path(__file__).resolve().parent / ".." / ".." / ".."
    uhh = db_path / "closta.db"
    if not uhh.is_file():
        print("welcome! initialising a db.")
        init_db()

def build_task(task_id, heading, description, importance: int, parent="task_container"):
    """
    function to be ran to create a task. arguments to be
    title, description, importance TODO:extra metadata such as time
    """
    with dpg.child_window(height=200,horizontal_scrollbar=False, parent=parent):
        dpg.add_text(heading,tag=f"heading_{task_id}", wrap=0 )
        dpg.add_separator()
        dpg.add_text(description,tag=f"desc_{task_id}", wrap=0 )

        dpg.add_spacer(height=2)
        dpg.add_separator()
        dpg.add_spacer(height=2)
        with dpg.group(tag=f"mod_btns_{task_id}", horizontal=True):
            dpg.add_checkbox(label="completed")
            dpg.add_spacer(height=20)
            dpg.add_button(label="edit", user_data=task_id, callback=edit_callback)
            dpg.add_button(label="delete", user_data=task_id, callback=delete_callback)

def load_tasks_ui(parent="task_container"):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('SELECT id, name, description, importance FROM tasks')
    rows = c.fetchall()
    conn.close()
    for row in rows:
        build_task(row[0], row[1], row[2], row[3], parent=parent)


def new_task(sender, app_data):
    if dpg.does_item_exist("new_task_win"):
        dpg.focus_item("new_task_win")
        return

    def refresh_task_list():
        dpg.delete_item("task_container", children_only=True)
        load_tasks_ui()

    def save_new_task_callback(sender, app_data):
        heading = dpg.get_value("heading_input")
        description = dpg.get_value("desc_input")
        importance = dpg.get_value("imp_dropdown")
        save_task(heading, description, importance)
        dpg.delete_item("new_task_win")
        refresh_task_list()

    win_height = 200
    win_width = 250
    current_height = int(get_setting('window_height', '600'))
    y = (current_height - win_height) // 2
    x = (300 - win_width) // 2 # 300 is width of viewport

    with dpg.window(tag="new_task_win", label="new task", width=win_width, height=win_height,
                    no_title_bar=True, no_move=False, no_resize=True):
        with dpg.group(horizontal=True):
            dpg.add_input_text(tag="heading_input", hint="heading")
            dpg.add_spacer(width=36)
            dpg.add_button(label="x", callback=lambda: dpg.delete_item("new_task_win"))
        dpg.add_input_text(tag="desc_input", hint="description", multiline=True)
        dpg.add_combo(items=[0,1,2], tag="imp_dropdown", default_value=0, label="importance")
        dpg.add_button(label="add task", callback=save_new_task_callback)
    
    dpg.set_item_pos("new_task_win", (x, y))

def edit_callback(sender,app_data,usr_data):
    task_id = usr_data
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute('SELECT name, description, importance FROM tasks WHERE id=?', (task_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return # :P
    
    def save_edit(task_id):
        heading = dpg.get_value(f"edit_heading_{task_id}")
        description = dpg.get_value(f"edit_desc_{task_id}")
        importance = dpg.get_value(f"edit_imp_{task_id}")
        edit_task(heading, description, importance, task_id)
        dpg.delete_item(f"edit_win_{task_id}")
        dpg.delete_item("task_container", children_only=True)
        load_tasks_ui()
    
    win_height = 200
    win_width = 250
    current_height = int(get_setting('window_height', '600'))
    y = (current_height - win_height) // 2
    x = (300 - win_width) // 2 # 300 is width of viewport

    with dpg.window(tag=f"edit_win_{task_id}", label="edit task", width=win_width, height=win_height,
                    no_title_bar=True, no_move=False, no_resize=True):
        with dpg.group(horizontal=True):
            dpg.add_input_text(tag=f"edit_heading_{task_id}", hint="heading", default_value=row[0])
        dpg.add_input_text(tag=f"edit_desc_{task_id}", hint="description", default_value=row[1] or "", multiline=True)
        dpg.add_combo(items=[0,1,2],tag=f"edit_imp_{task_id}", default_value=row[2], label="importance")
        dpg.add_button(label="save", callback=lambda: save_edit(task_id))
    
    dpg.set_item_pos(f"edit_win_{task_id}", (x, y))
    parent_group = dpg.get_item_parent(sender)
    task_window = dpg.get_item_parent(parent_group)
    dpg.delete_item(task_window)

def settings_callback(sender, app_data, usr_data):
    if dpg.does_item_exist("settings_window"):
        dpg.focus_item("settings_window")
        return

    current_height = int(get_setting('window_height', '600'))
    current_offset = int(get_setting('viewport_offset', '40'))

    def apply_settings():
        new_height = dpg.get_value("height_slider")
        new_offset = dpg.get_value("offset_slider")
        #save
        save_setting('window_height', new_height)
        save_setting('viewport_offset', new_offset)
        # apply to viewport
        dpg.set_viewport_height(new_height)
        dpg.set_viewport_pos(calc_window_pos(new_offset))
        dpg.delete_item("settings_window")
    
    def reset_settings():
        save_setting('window_height', '600')
        save_setting('viewport_offset', '40')
        dpg.set_viewport_height(600)
        dpg.set_viewport_pos(calc_window_pos(40))
        dpg.delete_item("settings_window")

    win_height = 200
    win_width = 250
    y = (current_height - win_height) // 2
    x = (300 - win_width) // 2 # 300 is width of viewport

    with dpg.window(tag="settings_window", label="settings", width=win_width, height=win_height,
                    no_title_bar=True, no_move=False, no_resize=True):
        with dpg.group(horizontal=True):
            dpg.add_text("settings", indent=10)
            dpg.add_spacer(width=win_width - 118)
            dpg.add_button(label="x", callback=lambda: dpg.delete_item("settings_window"))
        dpg.add_separator()
        dpg.add_text("window height")
        dpg.add_slider_int(tag="height_slider", default_value=current_height, min_value=200, max_value=600, width=-1, label="")
        dpg.add_text("viewport offset")
        dpg.add_slider_int(tag="offset_slider", default_value=current_offset, min_value=0, max_value=150, width=-1, label="")
        with dpg.group(horizontal=True):
            dpg.add_button(label="apply", callback=apply_settings)
            dpg.add_button(label="reset settings", callback=reset_settings)

        dpg.set_item_pos("settings_window", (x, y))


def calc_window_pos(offset=40):
    vpw, vph = dpg.get_viewport_width(), dpg.get_viewport_height()
    
    try:
        primary = pymonctl.getPrimary()
        if primary:
            screen_width, screen_height = primary.size
        else:
            monitors = pymonctl.getAllMonitors()
            if monitors:
                screen_width, screen_height = monitors[0].size
            else:
                screen_width, screen_height = 1920, 1080
    except Exception:
        screen_width, screen_height = 1920, 1080

    x, y = state._spawn_pos
    left = max(0, min(x - vpw // 2, screen_width - vpw))
    top = max(0, min(y - vph - offset, screen_height - vph))
    return left, top

def create_window():

    newbie_checker()
    #load settings
    win_height = int(get_setting('window_height','600'))
    offset = int(get_setting('viewport_offset','600'))
    # accent_color = get_setting('accent_color','ff7f0e')


    dpg.create_context()
    dpg.create_viewport(title="closta", width=300, height=win_height, decorated=False)
    dpg.set_viewport_pos(calc_window_pos(offset))
    # apply accent color here

    with dpg.window(tag="closta"):
        dpg.add_text("closta", tag="h")
        with dpg.group(horizontal=True):
            dpg.add_button(label="add task", callback=new_task)
            dpg.add_button(label="settings", callback=settings_callback)
    
        with dpg.group(tag="task_container"):
            pass
            # this will allow us to isolate task display into a single container
            # itll make it dead easy to clear existing task widgets when we add a new task.
    load_tasks_ui()



def spawn_window():
    
    def set_fonts():
        with dpg.font_registry():
            heading_font = dpg.add_font("C:/Windows/Fonts/arial.ttf", size=24)
            dpg.bind_item_font("h", heading_font)

    with _lock:
        if state.WINDOW_RUNNING:
            logging.info("window is running")
            return
        state._graceful_tray_exit = False
        state.WINDOW_RUNNING = True
        # fyi: checking using is dearpygui running before creating everythign will give it a heart attack
        try:
            create_window()
            dpg.setup_dearpygui()

            dpg.show_viewport()
            set_fonts()
            dpg.set_primary_window("closta", True)

            
            # ---- focus logic start ----
            # debugging this was hell, spent like 3 hours figuring out that i needed .activate() ;)
            # breaks if window isnt focused.
            closta_windows = pwc.getWindowsWithTitle('closta')
            if closta_windows:
                closta_win = closta_windows[0]
                closta_win.activate()
            
            _first_focus = False
            while dpg.is_dearpygui_running():
                dpg.render_dearpygui_frame()
                if state._graceful_tray_exit:
                    break

                if closta_win.isActive:
                    _first_focus = True
                elif _first_focus:
                    break
        finally:
            dpg.destroy_context()
            state.WINDOW_RUNNING = False
        
if __name__ == "__main__":
    spawn_window()

