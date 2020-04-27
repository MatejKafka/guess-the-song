$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if ($null -eq $env:VIRTUAL_ENV) {
    Write-Output "Activating venv..."
    & .\venv\Scripts\Activate.ps1
    Write-Output "Venv activated"
    $deactivateVenv = $true
} else {
    $deactivateVenv = $false
}

# --add-data paths are relative to spec file
pyinstaller `
    --onefile `
    --name "guess_the_song" `
    --specpath "./_build/" `
    --distpath "./_build/guess" `
    --workpath "./_build/build" `
    --add-data "../bin/ffplay.exe;." `
    --add-data "../bin/ffmpeg.exe;." `
    --add-data "../../config/config.json;." `
    --noconfirm `
    ./launcher.py

if ($LastExitCode -gt 0) {
    Write-Error "Could not run pyinstaller, exiting..."
    exit 11
}

Write-Output "Creating output archive."

if (Test-Path "./_build/guess/example/") {
    Remove-Item ./_build/guess/example/ -Recurse
}
Copy-Item -Force -Recurse ./example ./_build/guess/example
Copy-Item -Force ../LICENSE.txt ./_build/guess/

Set-Location _build
Compress-Archive -Force ./guess ./guess.zip
Set-Location ..


# FIXME: not very robust - when error occurs, venv will stay active
if ($deactivateVenv) {
    deactivate
    Write-Output "Venv deactivated"
}