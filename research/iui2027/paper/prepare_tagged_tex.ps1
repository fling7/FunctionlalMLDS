param(
    [string]$Destination
)

$ErrorActionPreference = "Stop"

$paperDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
$miktexDirectory = Join-Path $env:LOCALAPPDATA "Programs\MiKTeX\miktex\bin\x64"
$latex = Join-Path $miktexDirectory "latex.exe"
$tagName = "latex-lab-2025-11-01a"
$expectedCommit = "c5afb829ef326a0469435da85636c973cc258b3f"

if ([string]::IsNullOrWhiteSpace($Destination)) {
    $Destination = Join-Path $paperDirectory ".latex-toolchain\latex2e-2025-11"
}
$Destination = [System.IO.Path]::GetFullPath($Destination)
$destinationParent = Split-Path -Parent $Destination

if (-not (Test-Path -LiteralPath $latex)) {
    throw "latex.exe was not found. Install MiKTeX or update this script."
}

New-Item -ItemType Directory -Force -Path $destinationParent | Out-Null
if (-not (Test-Path -LiteralPath $Destination)) {
    & git clone --depth 1 --branch $tagName `
        https://github.com/latex3/latex2e.git $Destination
    if ($LASTEXITCODE -ne 0) {
        throw "Could not clone the pinned latex2e tag."
    }
}

if (-not (Test-Path -LiteralPath (Join-Path $Destination ".git"))) {
    throw "Destination exists but is not the expected Git checkout: $Destination"
}

$actualCommit = (& git -C $Destination rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $actualCommit -ne $expectedCommit) {
    throw "Expected latex2e commit $expectedCommit, found '$actualCommit'."
}

$latexLabDirectory = Join-Path $Destination "required\latex-lab"
Push-Location $latexLabDirectory
try {
    & $latex -interaction=nonstopmode -halt-on-error latex-lab.ins
    if ($LASTEXITCODE -ne 0) {
        throw "Could not extract the pinned latex-lab package files."
    }
}
finally {
    Pop-Location
}

$requiredPaths = @(
    (Join-Path $latexLabDirectory "latex-lab-testphase-latest.sty"),
    (Join-Path $Destination "texmf\tex\latex\pdfmanagement-testphase"),
    (Join-Path $Destination "texmf\tex\latex\tagpdf")
)
foreach ($requiredPath in $requiredPaths) {
    if (-not (Test-Path -LiteralPath $requiredPath)) {
        throw "Pinned tagged-PDF dependency is missing: $requiredPath"
    }
}

Write-Output "Pinned tagged-PDF TeX tree is ready."
Write-Output "Commit: $actualCommit"
Write-Output "Path: $Destination"
