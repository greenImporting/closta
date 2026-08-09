from pathlib import Path
from PIL import Image
from time import sleep
from closta import state
import closta.window.main as cwin
import threading
import os
import time
import pyautogui
import sys
import ctypes
import win32api
import win32con
import win32gui


# icon not working, spawn closta. 
user32 = ctypes.windll.user32

def wndproc(hwnd, msg, wp, lp):
    if msg == win32con.WM_USER + 20: # basically "if this tray interactuion is a tray icon click event:"
        if lp == win32con.WM_LBUTTONDOWN:
            show_closta()
            return 0
        if lp == win32con.WM_RBUTTONDOWN:
            win32gui.SetForegroundWindow(hwnd)
            menu = win32gui.CreatePopupMenu()
            win32gui.AppendMenu(menu, win32con.MF_STRING, 1, "spawn closta")
            win32gui.AppendMenu(menu, win32con.MF_STRING, 2, "exit")
            x, y = win32gui.GetCursorPos()
            cmd = win32gui.TrackPopupMenu(menu, win32con.TPM_RETURNCMD, x, y, 0, hwnd, None)
            win32gui.DestroyMenu(menu)
            if cmd == 1:
                show_closta()
            if cmd == 2:
                win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, notify_info)
                win32gui.PostQuitMessage(0)
            return 0
    return win32gui.DefWindowProc(hwnd, msg, wp, lp)

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


def create_tray():
    # big credits to https://github.com/hiroshil/Win32Gui_learning/blob/main/Shell32__Shell_NotifyIcon_ex1.py
    # great file to understand the tray loguic
    global notify_info
    win32gui.LoadImage(0, str(resource_path("assets/closta_tray.ico")), win32con.IMAGE_ICON, 0, 0, win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE)
    wc = win32gui.WNDCLASS()
    wc.hInstance = win32api.GetModuleHandle()
    wc.lpszClassName = "closta"
    wc.lpfnWndProc = wndproc
    wc.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
    cls = win32gui.RegisterClass(wc)

    hwnd = win32gui.CreateWindow(cls, "", win32con.WS_SYSMENU, 0, 0, 0, 0, 0, 0, wc.hInstance, None)
    hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
    notify_info = (hwnd, 1, win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP,
                win32con.WM_USER + 20, hicon, "closta")
    win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, notify_info)
    


    

def main():
    create_tray()
    init_closta()
    win32gui.PumpMessages()
    # no more while true <3

if __name__ == "__main__":
    main()