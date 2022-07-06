# Duel Masters - the game

My attempt to create game based on Duel Masters series. Game is written with Python3 and Qt Framework.

## Project still under development

To run the game:

```python main.py```

You also need to have installed PySide6 on your Python interpreter.
Run ```pip install -r requirements.txt``` to install all required libraries in your python interpeter.

You can use Vagrantfile in tools/ folder to create two VM instances to test the game.

## How to play

First, create a deck with 40 cards or load it from pre-created decks/ folder.
Second, one player must host the game by being the server, second player must join the game as the client.
As the client, enter IP address of the server over a reachable interface and correct port.

### Todo things:

* General
  * add information about the game
  * popup help messages when hovering over elements
  * complete logs system
  * refactor tcp error system
  * complete whole documentation for project
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
* In even further future
  * add AI for playing with computer

### Information

Card images were taken from:
* https://duelmasters.fandom.com/wiki/Duel_Masters_Wiki
* http://www.ccgdb.com/duelmasters/

### Usefull commands

#### Find on Windows PySide Ui Converter (bash)
path_to_file=$(find /c/Users/${USERNAME}/AppData/Local/Packages/ -name pyside6-uic.exe)
export PATH="$PATH:$(dirname $path_to_file)"
pyside6-uic -o src/ui/ui_manager.py ui/manager.ui