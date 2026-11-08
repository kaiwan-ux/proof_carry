# Monitor smoke8 test progress
$resultDir = "results/native_full_20260829-225319"
$interval = 30 # seconds

Write-Host "Monitoring $resultDir ..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop monitoring`n"

while ($true) {
    $timestamp = Get-Date -Format "HH:mm:ss"
    $workDirs = (Get-ChildItem -Path "$resultDir/native_work" -Directory -ErrorAction SilentlyContinue).Count
    $csvFiles = (Get-ChildItem -Path "$resultDir" -Filter "*.csv" -ErrorAction SilentlyContinue).Count
    
    Write-Host "[$timestamp] Work dirs: $workDirs | CSV files: $csvFiles"
    
    # Check if run is complete
    if (Test-Path "$resultDir/NATIVE_RUN_META.json") {
        Write-Host "`n=== RUN COMPLETE! ===" -ForegroundColor Green
        Get-Content "$resultDir/NATIVE_RUN_META.json"
        break
    }
    
    Start-Sleep -Seconds $interval
}
