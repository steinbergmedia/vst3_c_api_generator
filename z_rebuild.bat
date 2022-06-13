taskkill /F /IM pycharm64.exe /T
taskkill /F /IM devenv.exe /T
::taskkill /F /IM devenv.exe /T
timeout/t 3
if exist test_header.h del /F test_header.h
rmdir /Q /S build
mkdir build
cd build
cmake ..
cd C:\Program Files\JetBrains\PyCharm Community Edition 2022.1\bin
start pycharm64.exe
cd %~dp0
cd build
GeneratorTest.sln
::pause

