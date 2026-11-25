# build.ps1 — iSys LaTeX build for bdd-specification-drift
#
# WHY THIS SCRIPT EXISTS (measured on this host, 2026-11-25):
#   * `latexmk` is UNUSABLE: no Perl installed. Do not reintroduce it.
#   * The shell is Windows PowerShell 5.1; there is no `pwsh` binary on PATH.
#     Do not invoke `pwsh` from inside this script.
#   * MiKTeX 25.12 with auto-install enabled HANGS indefinitely when it decides a
#     package is missing, because its installer cannot write to its user data
#     directories under the file sandbox. We therefore pass --disable-installer
#     so a missing package becomes a fast, visible error instead of a hang.
#   * The official iSys class `sbc2025.cls` loads TeX Gyre Termes (`tgtermes`)
#     and `FiraSans`. On MiKTeX hosts where `pdftex.map` is stale, `main.tex`
#     registers `qtm.map`, `fira.map`, and `fontawesome.map` via `\pdfmapfile`
#     so scalable Type 1 fonts are embedded without overriding class typography.
#   * The iSys bibliography style is `apalike-sol.bst` (APA-based) driven by BIBTEX,
#     not biber.
#
# USAGE
#   Set-ExecutionPolicy -Scope Process Bypass -Force
#   .\build.ps1 -Main main.tex -Clean
#
[CmdletBinding()]
param(
    [string]$Main    = 'main.tex',
    [switch]$Clean,
    [switch]$AllowInstall,
    [string]$OutDir  = 'out'
)

$ErrorActionPreference = 'Stop'

# Resolve the manuscript robustly. Accept either "-Main main.tex" (the file lives in
# .\paper\) or an explicit relative path such as "paper\main.tex", and always run
# pdflatex from the directory that contains the .tex so that \input, \bibliography and
# the .aux files resolve consistently.
$candidates = @(
    (Join-Path $PSScriptRoot $Main),
    (Join-Path (Join-Path $PSScriptRoot 'paper') $Main),
    (Join-Path (Join-Path $PSScriptRoot 'paper') (Split-Path $Main -Leaf))
)
$texPath = $candidates | Where-Object { Test-Path -LiteralPath $_ -PathType Leaf } | Select-Object -First 1
if (-not $texPath) {
    throw "Cannot find manuscript '$Main'. Looked in:`n  $($candidates -join "`n  ")"
}
$texPath  = (Resolve-Path -LiteralPath $texPath).Path
$paperDir = Split-Path -Parent $texPath
$Main     = Split-Path -Leaf $texPath
Write-Host "build: manuscript = $texPath" -ForegroundColor DarkGray

Push-Location $paperDir
try {
    $job = [System.IO.Path]::GetFileNameWithoutExtension($Main)
    # NOTE: a one-element array produced by an if-expression is UNROLLED to a string by
    # PowerShell, and `@var` splatting a string throws. Keep this a plain string.
    $installerFlag = if ($AllowInstall) { '--enable-installer' } else { '--disable-installer' }

    if ($Clean) {
        Get-ChildItem -File | Where-Object {
            $_.Extension -in '.aux', '.bbl', '.blg', '.log', '.out', '.toc', '.lof', '.lot', '.fls', '.fdb_latexmk', '.synctex.gz', '.run.xml', '.bcf', '.nav', '.snm', '.vrb'
        } | Remove-Item -Force -ErrorAction SilentlyContinue
        Remove-Item -Recurse -Force $OutDir -ErrorAction SilentlyContinue
        Write-Host "build: cleaned intermediates." -ForegroundColor DarkGray
    }
    New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

    function Invoke-Pass {
        param([string]$Label)
        Write-Host "build: $Label" -ForegroundColor Cyan
        # MiKTeX writes log4cxx "access denied" notices about its own log file to
        # stderr. With $ErrorActionPreference='Stop' and 2>&1 redirection, PowerShell
        # promotes those notices to terminating errors and the pass aborts even
        # though pdflatex succeeded. Relax the policy for the duration of the call and
        # judge success only by the exit code.
        $prevEap = $ErrorActionPreference
        $ErrorActionPreference = 'Continue'
        try {
            $log = & pdflatex $installerFlag -interaction=batchmode -halt-on-error -file-line-error $Main 2>&1
            $code = $LASTEXITCODE
        } finally {
            $ErrorActionPreference = $prevEap
        }
        if ($code -ne 0) {
            Write-Host "build: pdflatex FAILED ($Label), exit $code" -ForegroundColor Red
            if (Test-Path "$job.log") {
                Get-Content "$job.log" | Select-String -Pattern '^\./.*:\d+:|^!' | Select-Object -First 40 |
                    ForEach-Object { Write-Host ("  " + $_.Line) -ForegroundColor Red }
            }
            throw "pdflatex failed at $Label"
        }
    }

    Invoke-Pass 'pass 1 (structure + .aux)'

    if (Test-Path "$job.aux") {
        $auxText = Get-Content "$job.aux" -Raw
        if ($auxText -match '\\citation\{') {
            Write-Host "build: bibtex (apalike-sol.bst)" -ForegroundColor Cyan
            $bib = & bibtex $job 2>&1
            $bib | Out-File -FilePath "$job.blg.stdout.txt" -Encoding utf8
            if ($LASTEXITCODE -ne 0) {
                Write-Host "build: BIBTEX FAILED" -ForegroundColor Red
                $bib | Select-Object -First 30 | ForEach-Object { Write-Host ("  " + $_) -ForegroundColor Red }
                throw 'bibtex failed'
            }
            $warn = $bib | Select-String -Pattern 'Warning--|error'
            if ($warn) { Write-Host "build: bibtex warnings:" -ForegroundColor Yellow; $warn | ForEach-Object { Write-Host ("  " + $_.Line) -ForegroundColor Yellow } }
        } else {
            Write-Host "build: no citations, skipping bibtex." -ForegroundColor DarkGray
        }
    }

    Invoke-Pass 'pass 2 (resolve refs)'
    Invoke-Pass 'pass 3 (stabilise)'

    if (-not (Test-Path "$job.pdf")) { throw "No PDF produced." }

    Copy-Item "$job.pdf" (Join-Path $OutDir "$job.pdf") -Force
    $pages = (Select-String -Path "$job.log" -Pattern 'Output written on .* \((\d+) page' |
              Select-Object -Last 1).Matches.Groups[1].Value
    $sizeKB = [int]((Get-Item (Join-Path $OutDir "$job.pdf")).Length / 1KB)
    Write-Host "build: OK -> $OutDir\$job.pdf  ($pages pages, $sizeKB KB)" -ForegroundColor Green

    # iSys requires a MINIMUM of 15 pages; flag it loudly rather than failing,
    # because during drafting the document is legitimately shorter.
    if ($pages -and [int]$pages -lt 15) {
        Write-Host "build: NOTE venue minimum is 15 pages; currently $pages." -ForegroundColor Yellow
    }

    $undef = Select-String -Path "$job.log" -Pattern 'Reference .* undefined|Citation .* undefined'
    if ($undef) {
        Write-Host "build: unresolved references remain:" -ForegroundColor Yellow
        $undef | Select-Object -First 20 | ForEach-Object { Write-Host ("  " + $_.Line) -ForegroundColor Yellow }
    }
} finally {
    Pop-Location
}
