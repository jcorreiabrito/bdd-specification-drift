$ErrorActionPreference = 'Continue'
Push-Location "C:\Users\jvtri\OneDrive\Documentos\Projetos\bdd-specification-drift\paper"
$installerFlag = @('--disable-installer')
$log = & pdflatex @installerFlag -interaction=batchmode -halt-on-error -file-line-error main.tex 2>&1
$code = $LASTEXITCODE
Pop-Location
Write-Output "captured exit=$code"
Write-Output ($log | Select-Object -First 3)
