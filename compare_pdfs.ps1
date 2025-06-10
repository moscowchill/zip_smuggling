# Compare original and extracted PDFs byte by byte

param(
    [string]$OriginalPdf = "test.pdf",
    [string]$ExtractedPdf = "$env:TEMP\test.pdf"
)

Write-Host "=== PDF Comparison ===" -ForegroundColor Cyan

$original = [System.IO.File]::ReadAllBytes($OriginalPdf)
$extracted = [System.IO.File]::ReadAllBytes($ExtractedPdf)

Write-Host "Original size: $($original.Length) bytes" -ForegroundColor Yellow
Write-Host "Extracted size: $($extracted.Length) bytes" -ForegroundColor Yellow

if ($original.Length -ne $extracted.Length) {
    Write-Host "Files have different sizes!" -ForegroundColor Red
    return
}

# Find first difference
$firstDiff = -1
$diffCount = 0
for ($i = 0; $i -lt $original.Length; $i++) {
    if ($original[$i] -ne $extracted[$i]) {
        if ($firstDiff -eq -1) {
            $firstDiff = $i
            Write-Host "`nFirst difference at byte: $i" -ForegroundColor Red
            
            # Show context around first difference
            Write-Host "`nContext (10 bytes before and after):" -ForegroundColor Yellow
            $start = [Math]::Max(0, $i - 10)
            $end = [Math]::Min($original.Length - 1, $i + 10)
            
            Write-Host "Original:" -ForegroundColor Green
            $hex = ""
            $ascii = ""
            for ($j = $start; $j -le $end; $j++) {
                if ($j -eq $i) { $hex += "[" }
                $hex += "{0:X2}" -f $original[$j]
                if ($j -eq $i) { $hex += "]" }
                $hex += " "
                
                if ($original[$j] -ge 32 -and $original[$j] -le 126) {
                    $ascii += [char]$original[$j]
                } else {
                    $ascii += "."
                }
            }
            Write-Host $hex -ForegroundColor DarkGreen
            Write-Host $ascii -ForegroundColor DarkGreen
            
            Write-Host "`nExtracted:" -ForegroundColor Red
            $hex = ""
            $ascii = ""
            for ($j = $start; $j -le $end; $j++) {
                if ($j -eq $i) { $hex += "[" }
                $hex += "{0:X2}" -f $extracted[$j]
                if ($j -eq $i) { $hex += "]" }
                $hex += " "
                
                if ($extracted[$j] -ge 32 -and $extracted[$j] -le 126) {
                    $ascii += [char]$extracted[$j]
                } else {
                    $ascii += "."
                }
            }
            Write-Host $hex -ForegroundColor DarkRed
            Write-Host $ascii -ForegroundColor DarkRed
        }
        $diffCount++
    }
}

if ($diffCount -eq 0) {
    Write-Host "`nFiles are identical!" -ForegroundColor Green
} else {
    Write-Host "`nTotal differences: $diffCount bytes" -ForegroundColor Red
    $percent = [Math]::Round(($diffCount / $original.Length) * 100, 2)
    Write-Host "Difference percentage: $percent%" -ForegroundColor Red
}

# Check if it's a line ending issue
Write-Host "`nChecking for line ending patterns..." -ForegroundColor Yellow
$originalCRLF = 0
$originalLF = 0
$extractedCRLF = 0
$extractedLF = 0

for ($i = 0; $i -lt $original.Length - 1; $i++) {
    if ($original[$i] -eq 13 -and $original[$i+1] -eq 10) { $originalCRLF++ }
    elseif ($original[$i] -eq 10) { $originalLF++ }
    
    if ($extracted[$i] -eq 13 -and $extracted[$i+1] -eq 10) { $extractedCRLF++ }
    elseif ($extracted[$i] -eq 10) { $extractedLF++ }
}

Write-Host "Original - CRLF: $originalCRLF, LF: $originalLF" -ForegroundColor Gray
Write-Host "Extracted - CRLF: $extractedCRLF, LF: $extractedLF" -ForegroundColor Gray
