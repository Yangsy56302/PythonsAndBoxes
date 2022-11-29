pyinstaller --onefile --console --distpath . --workpath ./temp/build --icon ./assets/images/icons/main.ico --name main.exe main.py
rd /S /Q temp
del main.exe.spec
pause