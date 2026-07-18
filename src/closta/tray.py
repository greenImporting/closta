from pathlib import Path
from PIL import Image
import pystray
import threading

def create_tray():
    imgpath = Path(__file__).resolve().parent / ".." / ".." / "media" / "exampletrayicon.png"
    trayico = Image.open(imgpath)
    ico = pystray.Icon(
        "uhhh",
        icon=trayico,
        menu=pystray.Menu(pystray.MenuItem("exit", lambda icon, item: ico.stop()))
    )

    threading.Thread(target=ico.run).start()
    #run icon as a seperate thread to not block main thread, does not close with dpg win close

create_tray()