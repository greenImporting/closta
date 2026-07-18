import dearpygui.dearpygui as dpg
import pywinctl as pwc



def create_window():
    dpg.create_context()
    dpg.create_viewport(title="closta", width=300, height=600, decorated=False)
    with dpg.window(tag="closta"):
        dpg.add_text("Lorem ipsum")



if __name__ == "__main__":
    create_window()
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("closta", True)
    # gotta check for the inial focus to then check for unfocus,
    # otherwise itll kill itself instantly
    while dpg.is_dearpygui_running():
        activ = pwc.getActiveWindowTitle()
        if activ == "closta":
            break
        dpg.render_dearpygui_frame()

    # breaks if window isnt focused.
    while dpg.is_dearpygui_running():
        activ = pwc.getActiveWindowTitle()
        if activ != "closta":
            break
        dpg.render_dearpygui_frame()

    dpg.destroy_context()
    # dpg.start_dearpygui()
    # dpg.destroy_context()

