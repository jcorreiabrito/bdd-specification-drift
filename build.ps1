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
#   * The official iSys class `sbc2025.cls` comments out `\RequirePackage{lmodern}`,
#     leaving T1-encoded bitmap fonts; microtype then dies with
#     "pdfTeX error (font expansion): auto expansion is only possible with scalable
#     fonts". The document MUST load `\usepackage{lmodern}` in its preamble.
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
$paperDir = Join-Path $PSScriptRoot 'paper'
if (-not (Test-Path (Join-Path $paperDir $Main))) {
    if (Test-Path (Join-Path $PSScriptRoot $Main)) { $paperDir = $PSScriptRoot }
    else { throw "Cannot find '$Main' under '$paperDir' or '$PSScriptRoot'." }
}

Push-Location $paperDir
try {
    $job = [System.IO.Path]::GetFileNameWithoutExtension($Main)
    $installerFlag = if ($AllowInstall) { @('--enable-installer') } else { @('--disable-installer') }

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
        $log = & pdflatex @installerFlag -interaction=batchmode -halt-on-error -file-line-error $Main 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "build: pdflatex FAILED ($Label), exit $LASTEXITCODE" -ForegroundColor Red
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
