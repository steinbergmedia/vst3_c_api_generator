cd build
py -m venv venv
call .\venv\Scripts\activate
py -m pip install libclang
py -m pip install clang
py -m pip install wheel