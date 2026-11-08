# InfraFixA compatibility entrypoint. The original in-process native gate is intentionally disabled.
& "$PSScriptRoot\run_mccv3_holdout_infrafixA.ps1"
exit $LASTEXITCODE
