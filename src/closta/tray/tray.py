from pathlib import Path
from PIL import Image
from closta.window.mainwin import spawn_window
import pystray
import threading


def spawn_closta(icon, item):
    spawn_window()
    print("DEBUG: spawned closta")
    pass

def build_menu(icon):
    return pystray.Menu(
        pystray.MenuItem("spawn closta", spawn_closta, default=True),
        pystray.MenuItem("exit", lambda icon, item: ico.stop()),
    )


def create_tray():
    imgpath = Path(__file__).resolve().parent / ".." / ".." / ".." / "media" / "exampletrayicon.png"
    trayico = Image.open(imgpath)
    ico = pystray.Icon("uhhh", icon=trayico)
    ico.menu = build_menu(ico)
    threading.Thread(target=ico.run).start()
    #TODO: fix tray closing after main window closure
    #run icon as a seperate thread to not block main thread, does not close with dpg win close

create_tray()