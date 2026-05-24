@echo off
echo ============================================
echo        C: Drive Usage Scanner
echo ============================================
echo.

echo Scanning C: drive... Please wait...
echo.

:: Get total and free space
forfreespace
echo.

:: Check main folders
echo [1] Windows folder: %SystemRoot%
for /f "tokens=3" %%a in ('dir /s /-c "%SystemRoot%" 2^>nul ^| findstr /c:"bytes free"') do echo    Size: %%a

echo.
echo [2] Users folder: %USERPROFILE%
for /f "tokens=3" %%a in ('dir /s /-c "%USERPROFILE%" 2^>nul ^| findstr /c:"bytes free"') do echo    Size: %%a

echo.
echo [3] Program Files: %ProgramFiles%
for /f "tokens=3" %%a in ('dir /s /-c "%ProgramFiles%" 2^>nul ^| findstr /c:"bytes free"') do echo    Size: %%a

echo.
echo [4] Windows Update Cache: %SystemRoot%\SoftwareDistribution\Download
if exist "%SystemRoot%\SoftwareDistribution\Download" (
    for /f "tokens=3" %%a in ('dir /s /-c "%SystemRoot%\SoftwareDistribution\Download" 2^>nul ^| findstr /c:"bytes free"') do echo    Size: %%a
) else (
    echo    Not found
)

echo.
echo [5] Temp folders
for /f "tokens=3" %%a in ('dir /s /-c "%TEMP%" 2^>nul ^| findstr /c:"bytes free"') do echo    User Temp: %%a

echo.
echo ============================================
echo Scan complete!
echo.
echo NOTE: These are disk usage values.
echo       Use TreeSize Free for detailed analysis.
echo ============================================
pause
