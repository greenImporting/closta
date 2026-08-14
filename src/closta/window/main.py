import dearpygui.dearpygui as dpg
import sqlite3
import threading
import time
import ctypes
import win32gui
import win32con
from closta import state
from closta.storage.sqlite import delete_callback, save_task, init_db, edit_task, get_setting, save_setting, update_task_completion
from closta.paths import DB_PATH


IMP_MAP = {"low":0, "medium":1, "high": 2} # map for importance, as i save it as an int.
REV_IMP = {0:"low", 1:"medium", 2:"high"} # reverse importance map, for editing callback.
user32 = ctypes.windll.user32
old_wndproc = None
state._window_ready = threading.Event()

def get_centered_pos(win_width: int, win_height: int, first_run=False) -> tuple[int, int]:
    # look at this this is cute and fun and epic
    if not first_run:
        current_height = int(get_setting('window_height', '600'))
        y = (current_height - win_height) // 2
    else:
        y = (600 - win_height) // 2 # only for first run 

    x = (300 - win_width) // 2
    return x, y

def newbie_checker():
    def welcome_popup():
        win_height = 150
        win_width = 250
        x,y = get_centered_pos(win_height=win_height, win_width=win_width, first_run=True)
        with dpg.window(tag="welcome_win", label="welcome", height=win_height, width=win_width):
            dpg.add_text("hey! thanks for using closta,")
            dpg.add_text("the concise, light, open source \ntracking app!")
            dpg.add_text("made with love \nby greenImporting")
        dpg.set_item_pos("welcome_win", (x,y))
        return
    
        
    # checks if youre new. if so, init db.
    if not DB_PATH.is_file():
        print("welcome! initialising a db.")
        init_db()
        welcome_popup()
        # just setting initial settings
        
    return 


def build_task(task_id, heading, description, importance: int, completed: int, parent="task_container"):
    """
    function to be ran to create a task. arguments to be
    title, description, importance TODO:extra metadata such as time
    """

    def toggle_completed(sender, app_data, user_data):
        task_id = user_data
        completed = 1 if dpg.get_value(sender) else 0
        update_task_completion(task_id, completed)

    with dpg.child_window(height=200,horizontal_scrollbar=False, parent=parent):
        with dpg.group(horizontal=True):
            # heaiding+ imoprtance
            dpg.add_text(heading,tag=f"heading_{task_id}", wrap=0)
            imp_str = '!' * (importance + 1) # 0: !, 1: !!, 2: !!!
            color_map = {0: (0, 255, 0), 1: (255, 191, 0), 2: (255, 0, 0)}
            dpg.add_text(imp_str, color=color_map[importance], tag=f"imp_{task_id}")

        dpg.add_separator()
        dpg.add_spacer(height=1)
        dpg.add_text(description,tag=f"desc_{task_id}", wrap=0 )

        dpg.add_spacer(height=1)
        dpg.add_separator()
        dpg.add_spacer(height=2)
        with dpg.group(tag=f"mod_btns_{task_id}", horizontal=True):

            dpg.add_checkbox(label="completed",
                            tag=f"completed_{task_id}",
                            default_value = completed == 1,
                            callback=toggle_completed,
                            user_data=task_id)
            dpg.add_spacer(height=20)
            dpg.add_button(label="edit", user_data=task_id, callback=edit_callback, height=20)
            dpg.add_button(label="delete", user_data=task_id, callback=delete_callback, height=20)

def load_tasks_ui(parent="task_container"):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute('SELECT id, name, description, importance, completed FROM tasks')
        rows = c.fetchall()
    finally:
        conn.close()
        for row in rows:
            build_task(row[0], row[1], row[2], row[3], row[4], parent=parent)


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
        if heading or description:
            imp_str = dpg.get_value("imp_dropdown")
            importance = IMP_MAP[imp_str]
            save_task(heading, description, importance)
            dpg.delete_item("new_task_win")
            refresh_task_list()
        else:
            if dpg.does_item_exist("error_win"):
                dpg.focus_item("error_win")
                return
            with dpg.window(tag="error_win", label="error",no_title_bar=True, no_resize=True,no_move=True, width=300):
                dpg.add_text("error:\n")
                dpg.add_text("cannot make a new task without content.")       
                dpg.add_spacer(height=20)         
                dpg.add_button(label="close", callback=lambda: dpg.delete_item("error_win"))

            

    win_height = 200
    win_width = 250
    x,y = get_centered_pos(win_height=win_height,win_width=win_width)

    with dpg.window(tag="new_task_win", label="new task", width=win_width, height=win_height,
                    no_title_bar=True, no_move=False, no_resize=True):
        with dpg.group(horizontal=True):
            dpg.add_input_text(tag="heading_input", hint="heading")
            dpg.add_spacer(width=36)
            dpg.add_button(label="x", callback=lambda: dpg.delete_item("new_task_win"))
        dpg.add_input_text(tag="desc_input", hint="description", multiline=True, width=-1)
        dpg.add_combo(items=["low","medium","high"], tag="imp_dropdown", default_value="low", label="importance")
        dpg.add_button(label="add task", callback=save_new_task_callback)
    
    dpg.set_item_pos("new_task_win", (x, y))

def edit_callback(sender,app_data,usr_data):
    task_id = usr_data
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('SELECT name, description, importance FROM tasks WHERE id=?', (task_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return # :P
    
    def save_edit(task_id):
        heading = dpg.get_value(f"edit_heading_{task_id}")
        description = dpg.get_value(f"edit_desc_{task_id}")
        imp_str = dpg.get_value(f"edit_imp_{task_id}")
        importance = IMP_MAP[imp_str]
        edit_task(heading, description, importance, task_id)
        dpg.delete_item(f"edit_win_{task_id}")
        dpg.delete_item("task_container", children_only=True)
        load_tasks_ui()
    
    win_height = 200
    win_width = 250
    x,y = get_centered_pos(win_height=win_height,win_width=win_width)
    with dpg.window(tag=f"edit_win_{task_id}", label="edit task", width=win_width, height=win_height,
                    no_title_bar=True, no_move=False, no_resize=True):
        with dpg.group(horizontal=True):
            dpg.add_input_text(tag=f"edit_heading_{task_id}", hint="heading", default_value=row[0])
        dpg.add_input_text(tag=f"edit_desc_{task_id}", hint="description", default_value=row[1] or "", multiline=True,  width=-1)
        items = ["low", "medium", "high"]
        default_str = REV_IMP[row[2]]   # row[2] int importance
        dpg.add_combo(items=items, tag=f"edit_imp_{task_id}", default_value=default_str, label="importance")
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
    current_x_offset = int(get_setting('viewport_x_offset', '10'))
    current_y_offset = int(get_setting('viewport_y_offset', '10'))

    def apply_settings():
        new_height = dpg.get_value("height_slider")
        new_x_offset = dpg.get_value("x_offset_slider")
        new_y_offset = dpg.get_value("y_offset_slider")
        #save
        save_setting('window_height', new_height)
        save_setting('viewport_x_offset', new_x_offset)
        save_setting('viewport_y_offset', new_y_offset)
        # apply to viewport
        dpg.set_viewport_height(new_height)
        dpg.set_viewport_pos(calc_window_pos(new_x_offset,new_y_offset))
        dpg.delete_item("settings_window")
    
    def reset_settings():
        save_setting('window_height', '600')
        save_setting('viewport_x_offset', '10')
        save_setting('viewport_y_offset', '10')
        dpg.set_viewport_height(600)
        dpg.set_viewport_pos(calc_window_pos(10,10))
        dpg.delete_item("settings_window")

    win_height = 200
    win_width = 250
    x,y = get_centered_pos(win_height=win_height,win_width=win_width)

    with dpg.window(tag="settings_window", label="settings", width=win_width, height=win_height,
                    no_title_bar=True, no_move=False, no_resize=True):
        with dpg.group(horizontal=True):
            dpg.add_text("settings", indent=10)
            dpg.add_spacer(width=win_width - 118)
            dpg.add_button(label="x", callback=lambda: dpg.delete_item("settings_window"))
        dpg.add_separator()
        dpg.add_text("window height")
        dpg.add_slider_int(tag="height_slider", default_value=current_height, min_value=200, max_value=600, width=-1, label="")
        dpg.add_text("viewport x offset")
        dpg.add_slider_int(tag="x_offset_slider", default_value=current_x_offset, min_value=0, max_value=150, width=-1, label="")
        dpg.add_text("viewport y offset")
        dpg.add_slider_int(tag="y_offset_slider", default_value=current_y_offset, min_value=0, max_value=150, width=-1, label="")
        with dpg.group(horizontal=True):
            dpg.add_button(label="apply", callback=apply_settings)
            dpg.add_button(label="reset settings", callback=reset_settings)

        dpg.set_item_pos("settings_window", (x, y))
    


def calc_window_pos(x_offset=10, y_offset=10):
    '''
    uses systemparametersinfow with spi_getworkarea (0x0030) to retrieve the screen's work area (the desktop excluding the taskbar).
    then positions window to bottom right corner
    '''
    vpw, vph = dpg.get_viewport_width(), dpg.get_viewport_height()

    rect = ctypes.wintypes.RECT()

    ctypes.windll.user32.SystemParametersInfoW(
        0x0030,
        0,
        ctypes.byref(rect),
        0
    )

    x = rect.right - vpw - x_offset
    y = rect.bottom - vph - y_offset
    x = max(rect.left, x)
    y = max(rect.top, y)
    return x, y

    
    
def set_fonts():
    with dpg.font_registry():
        heading_font = dpg.add_font("C:/Windows/Fonts/arial.ttf", size=24)
        dpg.bind_item_font("h", heading_font)


#split viewwindow into show,hide and toggle for readability
def show_window(hwnd):
    state._window_visible = True
    user32.ShowWindowAsync(hwnd, win32con.SW_SHOW)
    user32.SetForegroundWindow(hwnd)


def hide_window(hwnd):
    state._window_visible = False
    user32.ShowWindowAsync(hwnd, win32con.SW_HIDE)

def create_window():
    dpg.create_context()
    #load settings
    newbie_checker()
    win_height = int(get_setting('window_height','600'))
    current_x_offset = int(get_setting('viewport_x_offset', '10'))
    current_y_offset = int(get_setting('viewport_y_offset', '10'))
    # accent_color = get_setting('accent_color','ff7f0e')
    dpg.create_viewport(title="closta", width=300, height=win_height, decorated=False)
    
    dpg.set_viewport_pos(calc_window_pos(current_x_offset, current_y_offset))
    # apply accent color here

    with dpg.window(tag="closta"):
        dpg.add_text("closta", tag="h")
        with dpg.group(horizontal=True):
            dpg.add_button(label="add task", callback=new_task)
            dpg.add_button(label="settings", callback=settings_callback)
    
        with dpg.group(tag="task_container"):
            pass
            # this will allow us to isolate task display into a single container
    load_tasks_ui()

def run_gui():
    create_window()
    dpg.setup_dearpygui()
    dpg.show_viewport()
    state._closta_hwnd = win32gui.FindWindow(None, "closta")
    state._window_ready.set()
    set_fonts()
    dpg.set_primary_window("closta", True)

def closta_wndproc(hwnd, msg, wparam, lparam):
    if msg == win32con.WM_ACTIVATE:
        # wm_activate packs extra info. !! NOT SAFE !!! NOT SAFDE !!!
        # extract manually because haha hex code in python omg wow so amazing
        activation = wparam & 0xFFFF # exrtact low 16 bits 

        if activation == win32con.WA_INACTIVE:
            #ignroe focus event whilst we switch to/from tray
            if time.monotonic() < state._focus_ignore_til:
                return 0
            
            if state._window_visible:
                hide_window(hwnd)
            
        return win32gui.CallWindowProc(old_wndproc, hwnd, msg, wparam, lparam)

    return win32gui.CallWindowProc(old_wndproc, hwnd, msg, wparam, lparam)
    # return og dpg wndproc pointer, bc otherwise dpg sh1ts itself

        
def main():
    global old_wndproc
    run_gui()
    old_wndproc = win32gui.SetWindowLong(state._closta_hwnd, win32con.GWL_WNDPROC, closta_wndproc)

    hide_window(state._closta_hwnd)
    while dpg.is_dearpygui_running():
        dpg.render_dearpygui_frame()


if __name__ == "__main__":
    main()
