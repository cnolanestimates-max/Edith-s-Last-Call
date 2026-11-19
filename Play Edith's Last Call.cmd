@echo off
rem Plays the current build of Edith's Last Call straight from the project (no packaging needed).
rem Close any test run first: only one copy of Unreal fits in this laptop's memory at a time.
set "UE=C:\GameDev\Unreal\Engines\UE_5.9\Engine\Binaries\Win64\UnrealEditor.exe"
if not exist "%UE%" (
  echo Could not find Unreal at %UE%
  pause
  exit /b 1
)
tasklist /FI "IMAGENAME eq UnrealEditor.exe" 2>nul | find /I "UnrealEditor.exe" >nul
if not errorlevel 1 (
  echo Unreal is already running ^(probably a test run^). Wait for it to finish, or close it, then start this again.
  pause
  exit /b 1
)
start "" "%UE%" "C:\GameDev\Unreal\WellnessCheck\WellnessCheck.uproject" /Game/WC/Maps/House -game -fullscreen -nosplash -log
