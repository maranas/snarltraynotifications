rd /S /Q dist
python setup.py py2exe
ren dist\snarl_notifications.exe "Snarl Tray Notifications.exe"
copy icon.ico dist\icon.ico
copy LICENSE dist\LICENSE
mkdir dist\Licenses
mkdir dist\Licenses\PySnarl
copy Licenses dist\Licenses
copy Licenses\PySnarl\License.txt dist\Licenses\PySnarl\License.txt