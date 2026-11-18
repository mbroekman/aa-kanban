$ErrorActionPreference = "Stop"

$FrontendDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PluginDir = Split-Path -Parent $FrontendDir
$OutDir = Join-Path $PluginDir "aa_kanban\static\aa_kanban\spa"
$BuildDir = Join-Path $env:LOCALAPPDATA "aa-kanban-frontend-build"

Write-Host "Syncing frontend sources to local NTFS build dir: $BuildDir"
New-Item -ItemType Directory -Force -Path $BuildDir | Out-Null
Copy-Item -Path (Join-Path $FrontendDir "package.json") -Destination $BuildDir -Force
Copy-Item -Path (Join-Path $FrontendDir "tsconfig.json") -Destination $BuildDir -Force
Copy-Item -Path (Join-Path $FrontendDir "vite.config.ts") -Destination $BuildDir -Force
Copy-Item -Path (Join-Path $FrontendDir "components.json") -Destination $BuildDir -Force

$TargetSrc = Join-Path $BuildDir "src"
if (Test-Path $TargetSrc) { Remove-Item $TargetSrc -Recurse -Force }
Copy-Item -Path (Join-Path $FrontendDir "src") -Destination $TargetSrc -Recurse -Force

Push-Location $BuildDir
try {
    if (-not (Test-Path (Join-Path $BuildDir "node_modules"))) {
        Write-Host "Installing npm dependencies..."
        npm install
    }
    Write-Host "Building Vite + React + shadcn/ui SPA..."
    npm run build
}
finally {
    Pop-Location
}

$BuiltAssets = Join-Path $BuildDir "..\aa_kanban\static\aa_kanban\spa"
# Because vite.config.ts outputs to ../aa_kanban/static/aa_kanban/spa relative to BuildDir:
$LocalOut = Join-Path (Split-Path -Parent $BuildDir) "aa_kanban\static\aa_kanban\spa"
Write-Host "Copying built bundle to $OutDir"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
if (Test-Path (Join-Path $OutDir "assets")) {
    Remove-Item (Join-Path $OutDir "assets") -Recurse -Force
}
Copy-Item -Path (Join-Path $LocalOut "assets") -Destination (Join-Path $OutDir "assets") -Recurse -Force
Write-Host "Done! Built SPA assets at $OutDir"
