# Ani47
CLI app to browse and watch on Anime47
# Installation
```bash
$ git clone https://github.com/CleveTok3125/Ani47/
$ cd Ani47
$ pip install -r requirements.txt
```
# Build
- Linux:
```bash
$ pip install pyinstaller
$ bash build.sh
```
- Windows:
```cmd
$ pip install pyinstaller
$ build.cmd
```
# Usage
Default:
```bash
$ python main.py
```
Quick Search:
```bash
$ python main.py <anime_name>
```
View last watched anime:
- Windows
```cmd
$ python main.py !last
```
- Linux
```bash
$ python main.py '!last'
```
## Query commands
- `!last`: View last watched anime
- `!ask`: Enter raw search mode (treat query commands such as `!ask` and `!last` as search content)
- `!history`: Show viewing history
- `!clearhistory`: Clear viewing history
- `!clearcache`: Clears all generated caches, including session cache, subtitle files, viewing history, and debug files.
- `!exit`: Exit
- `!which` or `!where`: Returns the current working directory and absolute path
- `!clear` or `!cls`: Clear screen