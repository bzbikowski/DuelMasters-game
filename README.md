# Duel Masters - the game

My attempt to create game based on Duel Masters series. Game is written with Python3 and Qt Framework.

## Project still under development

Debug mode (you don't need any internet connection to test application) is disabled by default.
To turn it on, pass an argument "--debug=True" when launching the "main.py" file:

```python main.py --debug=True```

You also need to have installed PySide6 on your Python interpreter.
Run ```pip install -r requirements.txt``` to install all required libraries in your python interpeter.

### Todo things:
* add information about the game
* ~~complete graveyard feature~~
* complete logs system
* ~~refactor all views~~
* refactor tcp error system
* complete whole documentation for project
* ~~make all effects for all cards~~

* General
  * popup help messages when hovering over elements
* Main Menu
  * add loading database menu during first start
* Game
  * implement for debug mode separate tool window, which could run commands without restrictions
* Manager
  * highlight when hovering over nameplates of added cards
  * enable clicks to add, preview or delete cards
  * add high resolution and size cards
* In far future
  * change architecture to client <-> external server <-> client from client <-> local server
  * creating your own avatar and cardback

### Spreedsheets:

Effects implemented: https://1drv.ms/x/s!AodrLtV7i89ggaI72uj1eJ-JBaoMRg?e=8ADWqT

Message system: https://1drv.ms/x/s!AodrLtV7i89ggaIIfuUt6f0RaV8HGg?e=zqtAZV

### Information

Card images were taken from:
* https://duelmasters.fandom.com/wiki/Duel_Masters_Wiki
* http://www.ccgdb.com/duelmasters/

### Usefull commands

#### Find on Windows PySide Ui Converter 
path_to_file=$(find /c/Users/${USERNAME}/AppData/Local/Packages/ -name pyside6-uic.exe)
export PATH="$PATH:$(dirname $path_to_file)"
pyside6-uic -o src/ui/ui_manager.py ui/manager.ui