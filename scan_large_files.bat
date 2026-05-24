@echo off
echo ================================================
echo       C: Drive Large Files Scanner
echo ================================================
echo.

echo [Step 1] Checking Windows Update Cache...
IF EXIST "C:\Windows\SoftwareDistribution\Download" (
    for /f "tokens=3" %%a in ('dir /s /-c "C:\Windows\SoftwareDistribution\Download" 2^>nul ^| findstr /c:"bytes free"') do echo   Windows Update: %%a
)

echo.
echo [Step 2] Checking Downloads folder...
IF EXIST "%USERPROFILE%\Downloads" (
    for /f "tokens=3" %%a in ('dir /s /-c "%USERPROFILE%\Downloads" 2^>nul ^| findstr /c:"bytes free"') do echo   Downloads: %%a
)

echo.
echo [Step 3] Checking Desktop...
for /f "tokens=3" %%a in ('dir /s /-c "%USERPROFILE%\Desktop" 2^>nul ^| findstr /c:"bytes free"') do echo   Desktop: %%a

echo.
echo [Step 4] Checking Documents...
IF EXIST "%USERPROFILE%\Documents" (
    for /f "tokens=3" %%a in ('dir /s /-c "%USERPROFILE%\Documents" 2^>nul ^| findstr /c:"bytes free"') do echo   Documents: %%a
)

echo.
echo [Step 5] Checking WeChat Files (if installed)...
IF EXIST "%USERPROFILE%\Documents\WeChat Files" (
    for /f "tokens=3" %%a in ('dir /s /-c "%USERPROFILE%\Documents\WeChat Files" 2^>nul ^| findstr /c:"bytes free"') do echo   WeChat Files: %%a
)

echo.
echo ================================================
echo Scan complete!
echo ================================================
pause
