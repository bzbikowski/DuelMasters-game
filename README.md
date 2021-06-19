# Duel Masters - the game

My attempt to create game based on Duel Masters series. Game is written with Python3 and Qt Framework.

## Project still under development

Debug mode (you don't need any internet connection to test application) is disabled by default.
To turn it on, pass an argument "--debug=True" when launching the "main.py" file:

```python main.py --debug=True```

You also need to have installed PySide2 on your Python interpreter.
Run ```pip install -r requirements.txt``` to install all required libraries in your python interpeter.

### Todo things:
* add information about the game
* complete graveyard feature
* complete logs system
* ~~refactor all views~~
* refactor tcp error system
* complete whole documentation for project
* make all effects for all cards
* ~~check tcp connection with other player~~
* all minor and major changes with graphics and GUI
* creating your own avatar and cardback
* popup help messages
* add high resolution and size cards for manager
* implement debug mode as separate window with commands without restrictions
* client <-> server <-> client architecture
* add loading database menu during first start

### Spreedsheets:

Effects implemented: https://1drv.ms/x/s!AodrLtV7i89ggaI72uj1eJ-JBaoMRg?e=8ADWqT

Message system: https://1drv.ms/x/s!AodrLtV7i89ggaIIfuUt6f0RaV8HGg?e=zqtAZV

### Information

Card images were taken from:
* https://duelmasters.fandom.com/wiki/Duel_Masters_Wiki
* http://www.ccgdb.com/duelmasters/

### Message system
Message system (TODO: translate to English):
        8,x,y - ja dodaję kartę x z reki na tarczę y
        9,x,y - ja tapuje/odtapuje manę
                x - 0/1 - odtapuje/tapuje
                y - pozycja karty na manie
        10,x - ja zaglądam w swoją tarczę na pozycji x
        11,x,y - ja zaglądam w twoją tarczę/kartę z reki na pozycji y
                x - 0/1 - ręka/tarcza
        12,x,y - (info) ja atakuje swoją kartą x twoją kartę y na polu bitwy
        13,x - ja niszcze ci tarczę na pozycji x