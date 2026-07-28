$ErrorActionPreference = "Stop"

$paperDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
$buildDirectory = Join-Path $paperDirectory "build"
$miktexDirectory = Join-Path $env:LOCALAPPDATA "Programs\MiKTeX\miktex\bin\x64"
$pdflatex = Join-Path $miktexDirectory "pdflatex.exe"
$bibtex = Join-Path $miktexDirectory "bibtex.exe"

if (-not (Test-Path -LiteralPath $pdflatex)) {
    throw "pdflatex.exe was not found. Install MiKTeX or update the build script."
}

New-Item -ItemType Directory -Force -Path $buildDirectory | Out-Null

Push-Location $paperDirectory
try {
    $latexArguments = @(
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-file-line-error",
        "-output-directory=$buildDirectory",
        "main.tex"
    )

    & $pdflatex @latexArguments
    if ($LASTEXITCODE -ne 0) {
        throw "Initial LaTeX build failed with exit code $LASTEXITCODE."
    }

    $auxiliaryFile = Join-Path $buildDirectory "main.aux"
    $hasCitations = Select-String -LiteralPath $auxiliaryFile -SimpleMatch "\citation" -Quiet
    if ($hasCitations) {
        & $bibtex (Join-Path $buildDirectory "main")
        if ($LASTEXITCODE -ne 0) {
            throw "BibTeX build failed with exit code $LASTEXITCODE."
        }
    }

    & $pdflatex @latexArguments
    if ($LASTEXITCODE -ne 0) {
        throw "Second LaTeX build failed with exit code $LASTEXITCODE."
    }

    & $pdflatex @latexArguments
    if ($LASTEXITCODE -ne 0) {
        throw "Final LaTeX build failed with exit code $LASTEXITCODE."
    }
}
finally {
    Pop-Location
}

Write-Output (Join-Path $buildDirectory "main.pdf")
