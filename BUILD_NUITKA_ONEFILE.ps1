$ErrorActionPreference = 'Stop'

# check for uv
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    write-host 'uv not found. installing...'

    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

    # refresh path for this powershell process
    $env:Path = [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';' +
                [System.Environment]::GetEnvironmentVariable('Path', 'Machine')

    if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
        write-host 'failed to install uv or uv is not on PATH'
        exit 1
    }
}

# create venv if it doesn't exist
if (-not (Test-Path '.\.venv')) {
    write-host 'creating virtual environment...'
    uv venv
}

# activate venv
if (-not $env:VIRTUAL_ENV) {
    write-host 'activating virtual environment...'
    .\.venv\Scripts\Activate.ps1
}

# install/update dependencies
uv pip install -r requirements.txt

# build
python -m nuitka `
    --onefile `
    --windows-console-mode=disable `
    --windows-icon-from-ico=src/assets/closta_tray.ico `
    --include-data-dir=src/assets=assets `
    --output-filename=closta.exe `
    src/closta

if ($LASTEXITCODE -ne 0) {
    write-host 'build failed'
    exit $LASTEXITCODE
}

$choice = read-host 'run at startup? (y/n)'
if ($choice -eq 'y') {
    $startup = [environment]::GetFolderPath('Startup')
    $dest = Join-Path $startup 'closta.exe'
    Copy-Item '.\closta.exe' $dest -Force
    Start-Process $dest
}

write-host 'thanks for building & using my app! you might get it stolen by defender though.'