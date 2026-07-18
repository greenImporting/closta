from pathlib import Path
from PIL import Image
from time import sleep
import closta.window.main as cwin
import pystray
import threading
import os

#TODO: when you spam the tray to open it, you are able to 'refresh'.
# basically need to make it so it wont be affected after one click, and two rapid clicks
# will close it.

def spawn_closta(icon, item):
    threading.Thread(target=cwin.spawn_window, daemon=True).start()

def exit_sequence(icon, item):
    cwin._i_am_closed = True
    icon.stop()
    # just incase tray lingers, force exit
    os._exit(0)


def build_menu(ico):
    return pystray.Menu(
        pystray.MenuItem("spawn closta", spawn_closta, default=True),
        pystray.MenuItem("exit", exit_sequence)
    )


def create_tray():
    imgpath = Path(__file__).resolve().parent / ".." / ".." / ".." / "media" / "exampletrayicon.png"
    trayico = Image.open(imgpath)
    closta_tray = pystray.Icon("uhhh", icon=trayico)
    closta_tray.menu = build_menu(closta_tray)
    threading.Thread(target=closta_tray.run, daemon=True).start()

create_tray()
for i in range(1,10):
    sleep(10) #debug