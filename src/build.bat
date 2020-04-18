@echo off
set ZIP=C:\PROGRA~1\7-Zip\7z.exe a -tzip -y -r
set REPO=rfb9000
set PACKID=rfb9000
set VERSION=0.2.0


quick_manifest.exe "RFB9000: A Google Translator" "%PACKID%" >%REPO%\manifest.json
echo %VERSION% >%REPO%\VERSION

fsum -r -jm -md5 -d%REPO% * > checksum.md5
move checksum.md5 %REPO%\checksum.md5

REM %ZIP% %REPO%_v%VERSION%_Anki20.zip *.py %REPO%\*
cd %REPO%
%ZIP% ../%REPO%_v%VERSION%_Anki21.ankiaddon *
%ZIP% ../%REPO%_v%VERSION%_CCBC.adze *
