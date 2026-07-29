from pathlib import Path
from PIL import Image
from time import sleep
from closta import state
import closta.window.main as cwin
import pystray
import threading
import os
import time
import pyautogui
import sys

def resource_path(relative_path):
    return Path(__file__).resolve().parent.parent.parent / relative_path
    
def show_closta():
    if state._window_ready:
        state._show_requested = True
        

def init_closta():
    state._spawn_pos = pyautogui.position()
    _window_thread = threading.Thread(target=cwin.main, daemon=True)
    _window_thread.start()
    if state._window_ready.wait(timeout=5):

        cwin.view_window(show=False, hwnd=state._hwnd)



def exit_sequence(icon, item):
    state._graceful_tray_exit = True
    icon.stop()
    os._exit(0)


def build_menu(ico):
    return pystray.Menu(
        pystray.MenuItem("show closta", show_closta, default=True),
        pystray.MenuItem("exit", exit_sequence)
    )


def create_tray():
    imgpath = resource_path("assets/closta_tray.png")
    trayico = Image.open(imgpath)
    closta_tray = pystray.Icon("uhhh", icon=trayico)
    closta_tray.menu = build_menu(closta_tray)
    threading.Thread(target=closta_tray.run, daemon=True).start()

def main():
    create_tray()
    init_closta()

    while True:
        sleep(3600)

if __name__ == "__main__":
    main()