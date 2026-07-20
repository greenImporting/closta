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

_last_spawn_time = 0

def spawn_closta(icon, item):
    global _last_spawn_time
    
    now = time.time()
    if now - _last_spawn_time < 1.0:
        return
    _last_spawn_time = now

    if state.WINDOW_RUNNING:
        return
    else:
        state._spawn_pos = pyautogui.position()
        threading.Thread(target=cwin.spawn_window, daemon=True).start()

def exit_sequence(icon, item):
    state._graceful_tray_exit = True
    icon.stop()
    # just incase tray lingers, force exit
    os._exit(0)


def build_menu(ico):
    return pystray.Menu(
        pystray.MenuItem("spawn closta", spawn_closta, default=True),
        pystray.MenuItem("exit", exit_sequence)
    )


def create_tray():
    imgpath = Path(__file__).resolve().parent / ".." / ".." / ".." / "assets" / "exampletrayicon.png"
    trayico = Image.open(imgpath)
    closta_tray = pystray.Icon("uhhh", icon=trayico)
    closta_tray.menu = build_menu(closta_tray)
    threading.Thread(target=closta_tray.run, daemon=True).start()

create_tray()
while True:
    sleep(3600)