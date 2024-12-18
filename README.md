# Ani47
CLI app to browse and watch on Anime47
# Installation
```bash
$ git clone https://github.com/CleveTok3125/Ani47/
$ cd Ani47
$ pip install -r requirements.txt
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