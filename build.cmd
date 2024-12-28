@ echo off
pyinstaller main.spec
copy config.ini ".\dist\Ani47\"
copy README.md ".\dist\Ani47\"
copy LICENSE ".\dist\Ani47\"