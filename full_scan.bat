@echo off
echo ============================================
echo     C: Drive Full Scan
echo ============================================
echo.

echo [1] C: Total Space
wmic logicaldisk where "DeviceID='C:'" get Size,FreeSpace /value | findstr "="
echo.

echo [2] Temp Folder Size
dir /s /a C:\Users\Administrator\AppData\Local\Temp 2>nul | findstr "File(s)"
echo.

echo [3] Windows Update Cache
if exist "C:\Windows\SoftwareDistribution\Download" dir /s "C:\Windows\SoftwareDistribution\Download" 2>nul | findstr "File(s)"
echo.

echo [4] Windows.old
if exist "C:\Windows.old" dir /s "C:\Windows.old" 2>nul | findstr "File(s)"
echo.

echo [5] Hiberfil.sys and Pagefile.sys
if exist "C:\hiberfil.sys" dir C:\hiberfil.sys | findstr "hiberfil"
if exist "C:\pagefile.sys" dir C:\pagefile.sys | findstr "pagefile"
echo.

echo ============================================
echo Scan Complete!
echo ============================================
pause
