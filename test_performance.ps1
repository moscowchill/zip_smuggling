# PowerShell Performance Test Script
# This script demonstrates the performance difference between the original and optimized approaches

Write-Host "=== PowerShell Zip Smuggling Performance Test ===" -ForegroundColor Cyan
Write-Host ""

# Test file search performance
Write-Host "Testing file search performance..." -ForegroundColor Yellow

# Simulate the SLOW recursive search (original level 1)
Write-Host "1. Testing SLOW recursive search (original method):" -ForegroundColor Red
$slowSearch = {
    $name = "testarch"
    # This is the problematic line that causes 30+ second delays
    $file = Get-ChildItem -Path $Env:USERPROFILE -Filter "*$name.zip" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
    return $file.FullName
}

Write-Host "   Measuring recursive search time..." -ForegroundColor Gray
$slowTime = Measure-Command { 
    try { 
        & $slowSearch 
    } catch { 
        Write-Host "   (Search completed or timed out)" -ForegroundColor Gray
    }
}
Write-Host "   Recursive search took: $($slowTime.TotalSeconds) seconds" -ForegroundColor Red

Write-Host ""

# Test the FAST targeted search (optimized)
Write-Host "2. Testing FAST targeted search (optimized method):" -ForegroundColor Green
$fastSearch = {
    $name = "testarch"
    $commonPaths = @(
        "$Env:USERPROFILE\Downloads",
        "$Env:USERPROFILE\Desktop", 
        "$Env:USERPROFILE\Documents",
        "$Env:TEMP",
        "$PWD"
    )
    
    $file = $null
    foreach($path in $commonPaths) {
        if(Test-Path $path) {
            $found = Get-ChildItem -Path $path -Filter "*$name.zip" -ErrorAction SilentlyContinue | Select-Object -First 1
            if($found) {
                $file = $found.FullName
                break
            }
        }
    }
    return $file
}

Write-Host "   Measuring targeted search time..." -ForegroundColor Gray
$fastTime = Measure-Command { 
    $result = & $fastSearch
    if($result) {
        Write-Host "   Found file: $result" -ForegroundColor Green
    } else {
        Write-Host "   No file found (expected if testarch.zip doesn't exist)" -ForegroundColor Gray
    }
}
Write-Host "   Targeted search took: $($fastTime.TotalSeconds) seconds" -ForegroundColor Green

Write-Host ""

# Test byte pattern search performance
Write-Host "Testing byte pattern search performance..." -ForegroundColor Yellow

# Create a test byte array (simulating a large zip file)
$testBytes = New-Object byte[] 100000  # 100KB test
# Add our pattern at position 50000
$testBytes[50000] = 0x55
$testBytes[50001] = 0x55
$testBytes[50002] = 0x55
$testBytes[50003] = 0x55

Write-Host "3. Testing SLOW Where-Object pattern search (original method):" -ForegroundColor Red
$slowPattern = {
    $bytes = $testBytes
    $size = (0..($bytes.Length-4) | Where-Object {
        $bytes[$_] -eq 0x55 -and 
        $bytes[$_+1] -eq 0x55 -and 
        $bytes[$_+2] -eq 0x55 -and 
        $bytes[$_+3] -eq 0x55 
    })[0] + 4
    return $size
}

Write-Host "   Measuring Where-Object pattern search..." -ForegroundColor Gray
$slowPatternTime = Measure-Command { 
    $result = & $slowPattern
    Write-Host "   Found pattern at position: $result" -ForegroundColor Red
}
Write-Host "   Where-Object search took: $($slowPatternTime.TotalSeconds) seconds" -ForegroundColor Red

Write-Host ""

Write-Host "4. Testing FAST for-loop pattern search (optimized method):" -ForegroundColor Green
$fastPattern = {
    $bytes = $testBytes
    $size = -1
    for($i = 0; $i -lt ($bytes.Length - 3); $i++) {
        if($bytes[$i] -eq 85 -and $bytes[$i+1] -eq 85 -and $bytes[$i+2] -eq 85 -and $bytes[$i+3] -eq 85) {
            $size = $i + 4
            break
        }
    }
    return $size
}

Write-Host "   Measuring for-loop pattern search..." -ForegroundColor Gray
$fastPatternTime = Measure-Command { 
    $result = & $fastPattern
    Write-Host "   Found pattern at position: $result" -ForegroundColor Green
}
Write-Host "   For-loop search took: $($fastPatternTime.TotalSeconds) seconds" -ForegroundColor Green

Write-Host ""

# Summary
Write-Host "=== PERFORMANCE SUMMARY ===" -ForegroundColor Cyan
Write-Host "File Search Performance:" -ForegroundColor White
Write-Host "  Recursive search: $($slowTime.TotalSeconds) seconds" -ForegroundColor Red
Write-Host "  Targeted search:  $($fastTime.TotalSeconds) seconds" -ForegroundColor Green
if($slowTime.TotalSeconds -gt 0) {
    $searchSpeedup = [math]::Round($slowTime.TotalSeconds / $fastTime.TotalSeconds, 1)
    Write-Host "  Speedup: ${searchSpeedup}x faster" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Pattern Search Performance:" -ForegroundColor White
Write-Host "  Where-Object: $($slowPatternTime.TotalSeconds) seconds" -ForegroundColor Red
Write-Host "  For-loop:     $($fastPatternTime.TotalSeconds) seconds" -ForegroundColor Green
$patternSpeedup = [math]::Round($slowPatternTime.TotalSeconds / $fastPatternTime.TotalSeconds, 1)
Write-Host "  Speedup: ${patternSpeedup}x faster" -ForegroundColor Cyan

Write-Host ""
Write-Host "RECOMMENDATION:" -ForegroundColor Yellow
Write-Host "Use zip_smuggle_optimized.py with obfuscation level 4 for best performance!" -ForegroundColor Green
Write-Host "This eliminates the 30+ second delay caused by recursive file search." -ForegroundColor Green
