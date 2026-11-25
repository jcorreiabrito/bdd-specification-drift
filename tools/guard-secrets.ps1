<#
.SYNOPSIS
    Confidentiality Firewall & Secret Scanner for the bdd-specification-drift repository.
.DESCRIPTION
    Scans tracked and untracked-not-ignored files (plus staged git additions when in a git repo)
    for credentials, internal/corporate hostnames, Jira-like internal ticket IDs, unknown email
    addresses, generic confidentiality/financial red-flag terms, and local denylist entries in
    .secrets-denylist.local. Exits 0 if clean, non-zero if any violation or error occurs.
#>
[CmdletBinding()]
param(
    [switch]$VerboseScan,
    [string]$RootPath = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if ([string]::IsNullOrWhiteSpace($RootPath)) {
    $RepoRoot = (Split-Path -Parent $ScriptDir).TrimEnd('\', '/')
} else {
    $RepoRoot = (Resolve-Path -LiteralPath $RootPath).Path.TrimEnd('\', '/')
}

function Get-MaskedSnippet {
    param([string]$Value)
    if ([string]::IsNullOrEmpty($Value)) { return '[REDACTED]' }
    if ($Value.Length -le 4) { return '****' }
    return ($Value.Substring(0, 2) + ('*' * [Math]::Min(8, $Value.Length - 4)) + $Value.Substring($Value.Length - 2))
}

function Test-IsBinaryFile {
    param([string]$FilePath)
    $BinaryExtensions = @(
        '.png', '.jpg', '.jpeg', '.gif', '.webp', '.ico', '.bmp', '.tiff',
        '.pdf', '.zip', '.gz', '.tar', '.tgz', '.7z', '.rar',
        '.exe', '.dll', '.so', '.dylib', '.class', '.jar', '.war',
        '.woff', '.woff2', '.ttf', '.eot', '.otf', '.mp3', '.mp4', '.bin'
    )
    $ext = [System.IO.Path]::GetExtension($FilePath).ToLowerInvariant()
    if ($BinaryExtensions -contains $ext) { return $true }

    try {
        $fs = [System.IO.File]::OpenRead($FilePath)
        try {
            $buf = New-Object byte[] 4096
            $read = $fs.Read($buf, 0, $buf.Length)
            for ($i = 0; $i -lt $read; $i++) {
                if ($buf[$i] -eq 0) { return $true }
            }
        } finally {
            $fs.Close()
        }
    } catch {
        return $true
    }
    return $false
}

# Load optional allowlist files (public issue prefixes, allowed domains, or exact allowlisted regexes)
$AllowedTicketPrefixes = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
foreach ($prefix in @(
    'UTF', 'ISO', 'RFC', 'IEEE', 'CVE', 'CWE', 'PEP', 'JEP', 'PSR', 'ECMA',
    'SHA', 'MD', 'HTTP', 'HTTPS', 'TLS', 'SSL', 'AES', 'RSA', 'SQL', 'UML',
    'API', 'SDK', 'CLI', 'GUI', 'AST', 'BDD', 'TDD', 'COVID', 'WIN', 'ARM',
    'RQ', 'GH', 'PR', 'FIG', 'TAB', 'ALG', 'EQ', 'H1', 'P1'
)) {
    [void]$AllowedTicketPrefixes.Add($prefix)
}

$AllowedEmails = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
foreach ($em in @('git@github.com', 'noreply@github.com')) {
    [void]$AllowedEmails.Add($em)
}

$AllowedEmailDomains = @(
    'example.com', 'example.org', 'example.net', 'test.com', 'localhost',
    'users.noreply.github.com', 'noreply.github.com'
)

$AllowlistRegexes = [System.Collections.Generic.List[regex]]::new()

foreach ($allowFile in @(
    (Join-Path $ScriptDir 'guard-secrets.allowlist'),
    (Join-Path $RepoRoot '.secrets-allowlist.local')
)) {
    if (Test-Path -LiteralPath $allowFile) {
        foreach ($rawLine in Get-Content -LiteralPath $allowFile -Encoding UTF8) {
            $line = $rawLine.Trim()
            if ([string]::IsNullOrWhiteSpace($line) -or $line.StartsWith('#')) { continue }
            if ($line -match '^ticket-prefix:\s*(.+)$') {
                [void]$AllowedTicketPrefixes.Add($Matches[1].Trim())
            } elseif ($line -match '^email:\s*(.+)$') {
                [void]$AllowedEmails.Add($Matches[1].Trim())
            } elseif ($line -match '^regex:\s*(.+)$') {
                $AllowlistRegexes.Add([regex]::new($Matches[1].Trim(), [System.Text.RegularExpressions.RegexOptions]::IgnoreCase))
            } else {
                $AllowlistRegexes.Add([regex]::new([regex]::Escape($line), [System.Text.RegularExpressions.RegexOptions]::IgnoreCase))
            }
        }
    }
}

# Build secret / confidentiality detection rules.
# Rule strings are assembled modularly so this scanner does not false-match its own literals.
$ghPrefix = ('gh' + 'p|gh' + 'o|gh' + 'u|gh' + 's|gh' + 'r')
$ghPatPrefix = ('github' + '_pat_')
$awsAkia = ('AK' + 'IA|AS' + 'IA')
$privKeyHeader = ('-----BEGIN ' + '[A-Z0-9 ]*PRIVATE KEY-----')
$finWords = (
    ('ban' + 'co') + '|' +
    ('ba' + 'nk') + '|' +
    ('bank' + 'ing') + '|' +
    ('emplo' + 'yer') + '|' +
    ('confiden' + 'tial') + '|' +
    ('proprie' + 'tary') + '|' +
    ('internal[-_ ]' + 'only') + '|' +
    ('for[-_ ]internal[-_ ]' + 'use')
)
$corpTlds = (('co' + 'rp') + '|' + ('lo' + 'cal') + '|' + ('inter' + 'nal'))
$intraWord = ('intra' + 'net')
$corpWord = ('co' + 'rp')
$internalWord = ('inter' + 'nal')

$Rules = @(
    @{ Name = 'GitHubClassicToken';     Pattern = "\b($ghPrefix)_[A-Za-z0-9_]{20,}\b";                                 Sensitive = $true },
    @{ Name = 'GitHubFineGrainedToken'; Pattern = "\b${ghPatPrefix}[A-Za-z0-9_]{20,}\b";                              Sensitive = $true },
    @{ Name = 'AwsAccessKeyId';         Pattern = "\b($awsAkia)[0-9A-Z]{16}\b";                                       Sensitive = $true },
    @{ Name = 'AwsSecretAccessKey';     Pattern = "(?i)\baws_secret_access_key\s*[:=]\s*['""]?[A-Za-z0-9/+=]{30,}";   Sensitive = $true },
    @{ Name = 'PrivateKeyBlock';        Pattern = $privKeyHeader;                                                     Sensitive = $true },
    @{ Name = 'BearerToken';            Pattern = "(?i)\bBearer\s+[A-Za-z0-9\-._~+/]{16,}=*";                         Sensitive = $true },
    @{ Name = 'HardcodedSecretAssign';  Pattern = "(?i)\b(api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret|passwd|password)\s*[:=]\s*['""][^'""\s]{8,}['""]"; Sensitive = $true },
    @{ Name = 'ProviderToken';          Pattern = "\b(xox[baprs]-[0-9A-Za-z-]{10,}|sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z\-_]{35})\b"; Sensitive = $true },
    @{ Name = 'InternalDomainOrHost';   Pattern = "(?i)\b[a-z0-9][a-z0-9.-]*\.($corpTlds)\b";                         Sensitive = $false },
    @{ Name = 'IntranetReference';      Pattern = "(?i)\b$intraWord\b";                                               Sensitive = $false },
    @{ Name = 'VpnOrInternalHost';      Pattern = "(?i)\b((vpn|$corpWord|$intraWord)[-.][a-z0-9.-]+|$internalWord\.[a-z0-9.-]+)\b"; Sensitive = $false },
    @{ Name = 'PrivateIpv4Address';     Pattern = "\b(10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b"; Sensitive = $false },
    @{ Name = 'FinancialOrConfidTerm';  Pattern = "(?i)\b($finWords)\b";                                              Sensitive = $false }
)

# Load optional local denylist (gitignored; never logged verbatim on match)
$DenylistRules = [System.Collections.Generic.List[hashtable]]::new()
$DenylistPath = Join-Path $RepoRoot '.secrets-denylist.local'
if (Test-Path -LiteralPath $DenylistPath) {
    $idx = 0
    foreach ($rawLine in Get-Content -LiteralPath $DenylistPath -Encoding UTF8) {
        $line = $rawLine.Trim()
        if ([string]::IsNullOrWhiteSpace($line) -or $line.StartsWith('#')) { continue }
        $idx++
        if ($line -match '^regex:\s*(.+)$') {
            $DenylistRules.Add(@{ Name = "LocalDenylist#$idx"; Pattern = "(?i)" + $Matches[1].Trim(); Sensitive = $true })
        } else {
            $DenylistRules.Add(@{ Name = "LocalDenylist#$idx"; Pattern = "(?i)" + [regex]::Escape($line); Sensitive = $true })
        }
    }
}

# Collect files to scan
$FilesToScan = [System.Collections.Generic.List[string]]::new()
$SeenRelPaths = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)

# The scanner must not scan itself: its detection literals necessarily contain the
# very patterns it looks for (e.g. the word "bank" split across string concatenations,
# and the .local TLD of the denylist filename). Self-matches are pure noise and, if
# left in, force operators to ignore the scanner's output entirely.
$ScannerOwnPaths = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
foreach ($own in @(
    (Join-Path $ScriptDir 'guard-secrets.ps1'),
    (Join-Path $ScriptDir 'guard-secrets.allowlist')
)) {
    [void]$ScannerOwnPaths.Add([System.IO.Path]::GetFullPath($own))
}

# Machine-derived and vendored-content exclusions.
#
# The firewall exists to stop US from disclosing employer-confidential material in
# content WE author. It must therefore scan authored prose (docs/, lit/*.md, refs/,
# paper/, submission/, TEAM.md, scripts/) exhaustively, but scanning bundled
# third-party artefacts produces noise that trains operators to ignore the tool:
#   * vendored toolchains ship their own LICENSE files (SPDX ids look like ticket ids);
#   * fetched journal/venue HTML is third-party text;
#   * the GitHub enumeration contains public repository names such as "*-banking";
#   * npm lockfiles quote dependency licence strings.
# None of these can contain OUR employer's information, and all are reproducible
# from the committed scripts. Excluding them keeps the signal meaningful.
$ExcludedSubtrees = [string[]]@(
    'data\frame\', 'data\processed\', 'data\pilot\', 'data\raw\', 'data\repos\', 'lit\sources\',
    'tools\jvm\', '.m2repo\', '.npm-cache\', '.pylibs\', '.gradle-home\',
    'paper\template\', 'pilot\smoke-js\node_modules\', 'pilot\smoke-java\target\'
)
$ExcludedFilePatterns = [string[]]@('package-lock.json', '*.blg.stdout.txt', 'stryker.out.txt', 'pitest.out.txt')

function Test-ExcludedPath {
    param([string]$RelPath)
    $norm = ($RelPath -replace '/', '\')
    foreach ($sub in $ExcludedSubtrees) {
        if ($norm.StartsWith($sub, [System.StringComparison]::OrdinalIgnoreCase)) { return $true }
    }
    $leaf = [System.IO.Path]::GetFileName($norm)
    foreach ($pat in $ExcludedFilePatterns) {
        if ($leaf -like $pat) { return $true }
    }
    return $false
}

$InGitRepo = $false
if (Test-Path -LiteralPath (Join-Path $RepoRoot '.git')) {
    Push-Location $RepoRoot
    $prevEap = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $gitCheck = & git rev-parse --is-inside-work-tree 2>$null
        if ($LASTEXITCODE -eq 0 -and ($gitCheck -join '').Trim() -eq 'true') {
            $InGitRepo = $true
            $gitFiles = & git -c core.quotePath=false ls-files --cached --others --exclude-standard 2>&1
            if ($LASTEXITCODE -ne 0) {
                throw "git ls-files failed with exit code $LASTEXITCODE`: $($gitFiles -join ' ')"
            }
            foreach ($rel in $gitFiles) {
                $cleanRel = "$rel".Trim()
                if ([string]::IsNullOrWhiteSpace($cleanRel)) { continue }
                $normRel = $cleanRel -replace '/', '\'
                if ($normRel -eq '.secrets-denylist.local') { continue }
                $full = Join-Path $RepoRoot $normRel
                if ($ScannerOwnPaths.Contains([System.IO.Path]::GetFullPath($full))) { continue }
                if (Test-ExcludedPath -RelPath $normRel) { continue }
                if ((Test-Path -LiteralPath $full -PathType Leaf) -and $SeenRelPaths.Add($normRel)) {
                    $FilesToScan.Add($full)
                }
            }
        }
    } finally {
        $ErrorActionPreference = $prevEap
        Pop-Location
    }
}

if (-not $InGitRepo) {
    $ExcludedDirRegex = '(\\|/)(\.git|node_modules|\.venv|venv|env|__pycache__|target|build|\.gradle|scratch|tmp|logs)(\\|/)|(\\|/)data(\\|/)repos(\\|/|$)'
    $ExcludedFileNames = @('.secrets-denylist.local', '.secrets-allowlist.local', '.DS_Store', 'Thumbs.db')
    Get-ChildItem -LiteralPath $RepoRoot -Recurse -File -Force | ForEach-Object {
        $full = $_.FullName
        $rel = $full.Substring($RepoRoot.Length).TrimStart('\', '/')
        if ($full -match $ExcludedDirRegex) { return }
        if ($ExcludedFileNames -contains $_.Name) { return }
        if ($ScannerOwnPaths.Contains([System.IO.Path]::GetFullPath($full))) { return }
        if (Test-ExcludedPath -RelPath $rel) { return }
        if ($SeenRelPaths.Add($rel)) {
            $FilesToScan.Add($full)
        }
    }
}

$Findings = [System.Collections.Generic.List[string]]::new()
$EmailRegex = [regex]::new('\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
$TicketRegex = [regex]::new('\b([A-Z][A-Z0-9_]{1,9})-\d{1,6}\b')

function Test-AllowlistedLine {
    param([string]$Line)
    foreach ($rx in $AllowlistRegexes) {
        if ($rx.IsMatch($Line)) { return $true }
    }
    return $false
}

function Scan-TextLines {
    param(
        [string]$Label,
        [string[]]$Lines
    )
    for ($lineIdx = 0; $lineIdx -lt $Lines.Count; $lineIdx++) {
        $lineNum = $lineIdx + 1
        $line = $Lines[$lineIdx]
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        $isAllowlisted = Test-AllowlistedLine -Line $line

        foreach ($rule in $Rules) {
            if ($isAllowlisted -and -not $rule.Sensitive) { continue }
            $m = [regex]::Match($line, $rule.Pattern)
            if ($m.Success) {
                $snippet = if ($rule.Sensitive) { Get-MaskedSnippet $m.Value } else { $m.Value }
                $Findings.Add("${Label}:${lineNum} [$($rule.Name)] matched '$snippet'")
            }
        }

        foreach ($dRule in $DenylistRules) {
            $m = [regex]::Match($line, $dRule.Pattern)
            if ($m.Success) {
                $Findings.Add("${Label}:${lineNum} [$($dRule.Name)] matched local denylist pattern [REDACTED]")
            }
        }

        # Email check
        foreach ($emMatch in $EmailRegex.Matches($line)) {
            $email = $emMatch.Value
            if ($AllowedEmails.Contains($email)) { continue }
            $domain = ($email -split '@', 2)[1].ToLowerInvariant()
            $isAllowedDomain = $false
            foreach ($ad in $AllowedEmailDomains) {
                if ($domain -eq $ad -or $domain.EndsWith(".$ad")) {
                    $isAllowedDomain = $true
                    break
                }
            }
            if (-not $isAllowedDomain -and -not $isAllowlisted) {
                $Findings.Add("${Label}:${lineNum} [UnknownEmail] matched '$(Get-MaskedSnippet $email)' (domain '$domain')")
            }
        }

        # Jira-like internal ticket ID check
        foreach ($tkMatch in $TicketRegex.Matches($line)) {
            $prefix = $tkMatch.Groups[1].Value
            if ($AllowedTicketPrefixes.Contains($prefix)) { continue }
            if (-not $isAllowlisted) {
                $Findings.Add("${Label}:${lineNum} [InternalTicketLikeId] matched '$($tkMatch.Value)'")
            }
        }
    }
}

$ScannedCount = 0
foreach ($file in $FilesToScan) {
    if (Test-IsBinaryFile -FilePath $file) { continue }
    $relPath = $file.Substring($RepoRoot.Length).TrimStart('\', '/') -replace '\\', '/'
    if ($VerboseScan) {
        Write-Host "Scanning: $relPath"
    }
    $lines = [System.IO.File]::ReadAllLines($file, [System.Text.Encoding]::UTF8)
    if ($lines.Length -gt 0) {
        Scan-TextLines -Label $relPath -Lines $lines
    }
    $ScannedCount++
}

# Also scan staged additions in git index (catches secrets staged even if modified/deleted in working tree)
if ($InGitRepo) {
    Push-Location $RepoRoot
    $prevEap = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $diffLines = & git diff --cached --unified=0 --no-color 2>$null
        if ($LASTEXITCODE -eq 0 -and $diffLines) {
            $currentFile = '<staged>'
            $addedLines = [System.Collections.Generic.List[string]]::new()
            foreach ($dl in $diffLines) {
                $dlStr = "$dl"
                if ($dlStr -match '^\+\+\+ b/(.+)$') {
                    if ($addedLines.Count -gt 0) {
                        Scan-TextLines -Label "STAGED:$currentFile" -Lines $addedLines.ToArray()
                        $addedLines.Clear()
                    }
                    $currentFile = $Matches[1]
                } elseif ($dlStr.StartsWith('+') -and -not $dlStr.StartsWith('+++')) {
                    $addedLines.Add($dlStr.Substring(1))
                }
            }
            if ($addedLines.Count -gt 0) {
                Scan-TextLines -Label "STAGED:$currentFile" -Lines $addedLines.ToArray()
            }
        }
    } finally {
        $ErrorActionPreference = $prevEap
        Pop-Location
    }
}

Write-Host "guard-secrets: scanned $ScannedCount file(s) (git=$InGitRepo, localDenylistRules=$($DenylistRules.Count))."
if ($Findings.Count -gt 0) {
    Write-Host "GUARD-SECRETS FAILED: $($Findings.Count) potential leak(s) detected:" -ForegroundColor Red
    foreach ($f in $Findings) {
        Write-Host "  - $f" -ForegroundColor Red
    }
    exit 1
}

Write-Host "GUARD-SECRETS PASSED: 0 findings." -ForegroundColor Green
exit 0

