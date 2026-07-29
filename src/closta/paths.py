import os
from pathlib import Path

APP_DIR = Path(os.environ["LOCALAPPDATA"]) / "closta"
APP_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = APP_DIR / "closta.db"