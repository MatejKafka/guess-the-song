$ErrorActionPreference = "Stop"

if ($null -eq $env:VIRTUAL_ENV) {
    Write-Error "This script must be run inside an active python venv!"
    exit 1
}

# --add-data paths are relative to spec file
pyinstaller `
    --onefile `
    --name "guess_the_song" `
    --specpath "./_build/" `
    --distpath "./_build/guess" `
    --workpath "./_build/build" `
    --add-data "../bin/ffplay.exe;." `
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
Copy-Item -Force ./LICENSE.txt ./_build/guess/

Set-Location _build
Compress-Archive -Force ./guess ./guess.zip
Set-Location ..