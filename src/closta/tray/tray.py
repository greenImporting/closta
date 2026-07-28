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

_last_spawn_time = 0
_window_thread = None
_thread_lock = threading.Lock()


def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).resolve().parent.parent.parent  # adjust for dev
    return base / relative_path

def spawn_closta(icon, item):
    global _last_spawn_time, _window_thread
    
    now = time.time()
    if now - _last_spawn_time < 1.0:
        return
    _last_spawn_time = now

    with _thread_lock:
        if _window_thread is not None and _window_thread.is_alive():
            return
        state._spawn_pos = pyautogui.position()
        _window_thread = threading.Thread(target=cwin.spawn_window, daemon=True)
        _window_thread.start()

def exit_sequence(icon, item):
    state._graceful_tray_exit = True
    icon.stop()
    os._exit(0)


def build_menu(ico):
    return pystray.Menu(
        pystray.MenuItem("spawn closta", spawn_closta, default=True),
        pystray.MenuItem("exit", exit_sequence)
    )


def create_tray():
    imgpath = resource_path("assets/closta_tray.png")
    trayico = Image.open(imgpath)
    closta_tray = pystray.Icon("uhhh", icon=trayico)
    closta_tray.menu = build_menu(closta_tray)
    threading.Thread(target=closta_tray.run, daemon=True).start()

create_tray()
while True:
    sleep(3600)