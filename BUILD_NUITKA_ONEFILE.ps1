if (-not $env:VIRTUAL_ENV) {
    write-host 'please activate venv'
    exit 1
}

python -m nuitka `
    --onefile `
    --windows-console-mode=disable `
    --windows-icon-from-ico=src/assets/closta_tray.ico `
    --include-data-dir=src/assets=assets `
    --output-filename=closta.exe `
    src/closta/tray/tray.py

if ($LASTEXITCODE -ne 0) {
    write-host 'build failed'
    exit $LASTEXITCODE
}

$choice = read-host 'run at startup? (y/n)'
if ($choice -eq 'y') {
    $startup = [environment]::getfolderpath('startup')
    $dest = join-path $startup 'closta.exe'
    copy-item .\closta.exe $dest -force
    start-process $dest
}