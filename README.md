# closta

> concise, light, open source tracking app.

simple tracker to track little tasks that you might set yourself.

made using python and dearpygui gui lib. currently only windows :P

tested on a 1080p screen with 100% scale. untested issues may arise with larger screens/scales

## usage guide

### building an exe with nuitka

1. `git clone https://github.com/greenImporting/closta.git`
2. run `.\BUILD_NUITKA_ONEFILE.ps1`

### running from source

1. check if uv is installed. if not: install using (open powershell):
   ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```
2. `uv sync`
3. `.venv\scripts\activate`
4. run `src\closta\tray\tray.py`


## known issues

- no text wrap for creating and editing tasks; issue with dearpygui
- fixed task child window height; skill issue/dearpygui issue (just imagine its like a post-it note)