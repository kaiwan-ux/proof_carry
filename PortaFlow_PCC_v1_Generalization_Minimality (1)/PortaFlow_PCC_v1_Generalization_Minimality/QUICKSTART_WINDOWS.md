# Windows quick start

## Recommended

1. Extract the ZIP.
2. Open the extracted folder.
3. Click the address bar, type `powershell`, press Enter.
4. Run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\run_pcc_v1.ps1
```

The script creates `.venv`, installs pinned dependencies, runs tests, native probes, the 432-row experiment, analysis, verification, checksums, and exports the result ZIP.

## Output to send back

`PortaFlow_PCC_v1_results.zip`

Do not send only screenshots; send the ZIP so raw evidence can be audited.
