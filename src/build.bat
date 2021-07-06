@echo off
set ZIP=C:\PROGRA~1\7-Zip\7z.exe a -tzip -y -r
set REPO=rfb9000
set PACKID=rfb9000
set VERSION=0.4.0


quick_manifest.exe "RFB9000: A Google Translator" "%PACKID%" >%REPO%\manifest.json
echo %VERSION% >%REPO%\VERSION

fsum -r -jm -md5 -d%REPO% * > checksum.md5
move checksum.md5 %REPO%\checksum.md5

cd %REPO%
%ZIP% ../%REPO%_v%VERSION%_Anki21.ankiaddon *
%ZIP% ../%REPO%_v%VERSION%_CCBC.adze *




REM  Support for 2.0 in no longer possible due to changes made to the API which is PY3 specific.
