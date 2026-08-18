# closta

> stands for concise, light, open source tracking app

simple little tracking app that lives in your tray.

<img width="270" height="480" src="closta_showcase.gif" alt="closta showcase" />

currently only supports windows. make with python using [DearPyGui](https://github.com/hoffstadt/DearPyGui), and a simple sqlite db in appdata.

note: closta has only been tested on 1080p screens (100% scale) on Windows 11. please report any issues [here](https://github.com/greenImporting/closta/issues)

## usage

### download from releases

you can download an archive from the releases, containing all libraries you may need to run. it is recommended to extract the contents first before use.

### building an exe with nuitka

i've provided a ps1 file to build your own exe using nuitka using your cloned repo. this exe isn't liked by defender, so you most likely will have it flagged. i would think it's because it isn't signed.

*run the following in a cmd*

1. `git clone https://github.com/greenImporting/closta.git`
2. run `.\BUILD_NUITKA_ONEFILE.ps1`

### running from source

*run the following in a cmd*

1. install [uv](https://docs.astral.sh/uv/getting-started/installation/)

2. `git clone https://github.com/greenImporting/closta.git && cd closta`
3. `uv sync && .venv\scripts\activate`
4. `.\src\closta\tray\tray.py`

## info

see the [todo.md](todo.md)

## acknowledgement

<small>this project used deepseek for assistance with library documentation (win32 lib primarily!!1). minor amounts of the code were generated with ai, but subsequently reviewed and changed by me (greenImporting) </small>