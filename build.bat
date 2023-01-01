pyinstaller --onefile --console --distpath . --workpath ./temp/build --icon ./assets/images/icons/PythonsAndBoxes.ico --name PythonsAndBoxes.exe PythonsAndBoxes.py
rd /S /Q temp
del PythonsAndBoxes.exe.spec
pause