pip install pyinstaller
pyinstaller --onefile --console --distpath . --workpath ./temp/build --icon main.ico --name main.exe main.py
rd /S /Q temp
del main.exe.spec
pause