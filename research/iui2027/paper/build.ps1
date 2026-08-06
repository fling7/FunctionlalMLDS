param(
    [switch]$ValidatePdfUa,
    [string]$TaggedTexRoot = $env:IUI2027_LATEX2E_ROOT,
    [string]$VeraPdfBat = $env:VERAPDF_BAT
)

$ErrorActionPreference = "Stop"

$paperDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
$buildDirectory = Join-Path $paperDirectory "build"
$miktexDirectory = Join-Path $env:LOCALAPPDATA "Programs\MiKTeX\miktex\bin\x64"
$lualatex = Join-Path $miktexDirectory "lualatex.exe"
$bibtex = Join-Path $miktexDirectory "bibtex.exe"
$expectedLatexCommit = "c5afb829ef326a0469435da85636c973cc258b3f"

if ([string]::IsNullOrWhiteSpace($TaggedTexRoot)) {
    $TaggedTexRoot = Join-Path $paperDirectory ".latex-toolchain\latex2e-2025-11"
}
$TaggedTexRoot = [System.IO.Path]::GetFullPath($TaggedTexRoot)

if (-not (Test-Path -LiteralPath $lualatex)) {
    throw "lualatex.exe was not found. Install MiKTeX or update the build script."
}
if (-not (Test-Path -LiteralPath $bibtex)) {
    throw "bibtex.exe was not found. Install MiKTeX or update the build script."
}
if (-not (Test-Path -LiteralPath (Join-Path $TaggedTexRoot ".git"))) {
    throw "The pinned tagged-PDF TeX tree is missing. Run prepare_tagged_tex.ps1 first."
}

$actualLatexCommit = (& git -C $TaggedTexRoot rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $actualLatexCommit -ne $expectedLatexCommit) {
    throw "Tagged TeX tree must be pinned to commit $expectedLatexCommit; found '$actualLatexCommit'."
}

$latexLabDirectory = Join-Path $TaggedTexRoot "required\latex-lab"
$pdfManagementDirectory = Join-Path $TaggedTexRoot "texmf\tex\latex\pdfmanagement-testphase"
$tagPdfDirectory = Join-Path $TaggedTexRoot "texmf\tex\latex\tagpdf"
foreach ($requiredDirectory in @(
    $latexLabDirectory,
    $pdfManagementDirectory,
    $tagPdfDirectory
)) {
    if (-not (Test-Path -LiteralPath $requiredDirectory)) {
        throw "Required tagged-PDF TeX directory is missing: $requiredDirectory"
    }
}

$oldTexInputs = $env:TEXINPUTS
$oldLuaInputs = $env:LUAINPUTS
$env:TEXINPUTS = "$latexLabDirectory;$pdfManagementDirectory;$tagPdfDirectory;;"
$env:LUAINPUTS = "$pdfManagementDirectory;$tagPdfDirectory;;"

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

    & $lualatex @latexArguments
    if ($LASTEXITCODE -ne 0) {
        throw "Initial LuaLaTeX build failed with exit code $LASTEXITCODE."
    }

    $auxiliaryFile = Join-Path $buildDirectory "main.aux"
    $hasCitations = Select-String -LiteralPath $auxiliaryFile -SimpleMatch "\citation" -Quiet
    if ($hasCitations) {
        & $bibtex (Join-Path $buildDirectory "main")
        if ($LASTEXITCODE -ne 0) {
            throw "BibTeX build failed with exit code $LASTEXITCODE."
        }
    }

    foreach ($pass in 2..4) {
        & $lualatex @latexArguments
        if ($LASTEXITCODE -ne 0) {
            throw "LuaLaTeX pass $pass failed with exit code $LASTEXITCODE."
        }
    }

    $logFile = Join-Path $buildDirectory "main.log"
    $unstable = Select-String -LiteralPath $logFile -Quiet -Pattern (
        "Rerun to get cross-references right|" +
        "Label\(s\) may have changed|" +
        "There were undefined (references|citations)"
    )
    if ($unstable) {
        throw "LaTeX references are not stable after four passes."
    }
}
finally {
    Pop-Location
    $env:TEXINPUTS = $oldTexInputs
    $env:LUAINPUTS = $oldLuaInputs
}

$pdfFile = Join-Path $buildDirectory "main.pdf"
if ($ValidatePdfUa) {
    if ([string]::IsNullOrWhiteSpace($VeraPdfBat) -or
        -not (Test-Path -LiteralPath $VeraPdfBat)) {
        throw "Set VERAPDF_BAT or pass -VeraPdfBat with a veraPDF 1.30.2 batch file."
    }

    $veraOutput = & $VeraPdfBat -f ua2 --format text --verbose `
        --maxfailuresdisplayed 50 $pdfFile 2>&1
    $veraExitCode = $LASTEXITCODE
    $veraOutput | Write-Output
    $veraText = $veraOutput -join [Environment]::NewLine
    if ($veraExitCode -ne 0 -or $veraText -notmatch "(?m)^PASS\b") {
        throw "PDF/UA-2 validation failed."
    }
}

Write-Output $pdfFile
