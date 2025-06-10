# Diagnostic script to check PDF extraction issue

param(
    [string]$ZipPath = "report.zip",
    [string]$ExtractedPdf = "$env:TEMP\test.pdf"
)

Write-Host "=== PDF Extraction Diagnostic ===" -ForegroundColor Cyan

# Read the ZIP file
$bytes = [System.IO.File]::ReadAllBytes($ZipPath)
Write-Host "ZIP file size: $($bytes.Length) bytes" -ForegroundColor Yellow

# Search for PDF header
Write-Host "`nSearching for PDF headers (PDF-)..." -ForegroundColor Yellow
$pdfPositions = @()
for($i = 0; $i -lt ($bytes.Length - 3); $i++) {
    if($bytes[$i] -eq 80 -and $bytes[$i+1] -eq 68 -and $bytes[$i+2] -eq 70 -and $bytes[$i+3] -eq 45) {
        $pdfPositions += $i
        Write-Host "Found PDF- at position: $i" -ForegroundColor Green
        # Show next 20 bytes
        $preview = ""
        for($j = 0; $j -lt 20 -and ($i+$j) -lt $bytes.Length; $j++) {
            $preview += [char]$bytes[$i+$j]
        }
        Write-Host "  Preview: $preview" -ForegroundColor Gray
    }
}

# Search for EXE marker
Write-Host "`nSearching for EXE marker (0x55555555)..." -ForegroundColor Yellow
$exePosition = -1
for($i = 0; $i -lt ($bytes.Length - 3); $i++) {
    if($bytes[$i] -eq 0x55 -and $bytes[$i+1] -eq 0x55 -and $bytes[$i+2] -eq 0x55 -and $bytes[$i+3] -eq 0x55) {
        $exePosition = $i
        Write-Host "Found EXE marker at position: $i" -ForegroundColor Green
        break
    }
}

# Find EOCD
Write-Host "`nSearching for End of Central Directory (PK0506)..." -ForegroundColor Yellow
$eocdPosition = -1
for($i = $bytes.Length - 22; $i -ge 0; $i--) {
    if($bytes[$i] -eq 0x50 -and $bytes[$i+1] -eq 0x4B -and $bytes[$i+2] -eq 0x05 -and $bytes[$i+3] -eq 0x06) {
        $eocdPosition = $i
        Write-Host "Found EOCD at position: $i" -ForegroundColor Green
        # Read central directory offset
        $cdOffset = [BitConverter]::ToUInt32($bytes, $i + 16)
        Write-Host "Central Directory offset from EOCD: $cdOffset" -ForegroundColor Gray
        break
    }
}

# Check extracted PDF
if (Test-Path $ExtractedPdf) {
    Write-Host "`nChecking extracted PDF..." -ForegroundColor Yellow
    $extractedBytes = [System.IO.File]::ReadAllBytes($ExtractedPdf)
    Write-Host "Extracted PDF size: $($extractedBytes.Length) bytes" -ForegroundColor Green
    
    # Show first 50 bytes
    Write-Host "First 50 bytes of extracted PDF:" -ForegroundColor Gray
    $hex = ""
    $ascii = ""
    for($i = 0; $i -lt 50 -and $i -lt $extractedBytes.Length; $i++) {
        $hex += "{0:X2} " -f $extractedBytes[$i]
        if($extractedBytes[$i] -ge 32 -and $extractedBytes[$i] -le 126) {
            $ascii += [char]$extractedBytes[$i]
        } else {
            $ascii += "."
        }
    }
    Write-Host $hex -ForegroundColor DarkGray
    Write-Host $ascii -ForegroundColor DarkGray
}

Write-Host "`n=== Summary ===" -ForegroundColor Cyan
Write-Host "PDF positions found: $($pdfPositions.Count)" -ForegroundColor White
Write-Host "EXE marker position: $exePosition" -ForegroundColor White
Write-Host "EOCD position: $eocdPosition" -ForegroundColor White

if ($pdfPositions.Count -gt 1) {
    Write-Host "`nWARNING: Multiple PDF headers found!" -ForegroundColor Red
    Write-Host "The script might be extracting from the wrong position." -ForegroundColor Red
}
