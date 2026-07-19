import dearpygui.dearpygui as dpg
import pywinctl as pwc

WINDOW_RUNNING = False
_i_am_closed = False

def build_table():
    with dpg.table(header_row=False):
        dpg.add_table_column()
        #TODO: if logic here if first run
        with dpg.table_row():
            with dpg.table_cell():
                dpg.add_text("example data :P")

def build_task():
    """
    function to be ran to create a task. arguments to be
    title, description, importance TODO:extra metadata such as time

    will just add those into main window as like a list, with a button of completed and delete.
    """
    #example data
    _example_head = "Lorem ipsum"
    _example_desc = "dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."
    _example_importance = 1 # 0: !, 1: !!, 2: !!!


def delete_task():
    pass


def create_window():
    dpg.create_context()
    dpg.create_viewport(title="closta", width=300, height=600, decorated=False)
    with dpg.window(tag="closta"):
        dpg.add_text("Lorem ipsum")
        build_table()

def spawn_window():
    global WINDOW_RUNNING, _i_am_closed
    _i_am_closed = False
    if WINDOW_RUNNING == False:
        # add check logic here for if there is win open already 
        # so multiple windows dont open (clicking on tray)
        # checking using is dearpygui running before creating everythign will give it a heart attack

        create_window()
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("closta", True)
        WINDOW_RUNNING = True

        # gotta check for the inial focus to then check for unfocus,
        # otherwise itll kill itself instantly
        while dpg.is_dearpygui_running():
            activ = pwc.getActiveWindowTitle()
            if _i_am_closed:
                break
            if activ == "closta":
                break
            dpg.render_dearpygui_frame()

        # breaks if window isnt focused.
        while dpg.is_dearpygui_running():
            activ = pwc.getActiveWindowTitle()
            if _i_am_closed:
                break
            if activ != "closta":
                break
            dpg.render_dearpygui_frame()
        dpg.destroy_context()
        WINDOW_RUNNING = False
    print("window is runnign!!!!! ")


if __name__ == "__main__":
    print("sanity check")
    spawn_window()

