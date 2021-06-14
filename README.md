# DuelMaster-game

#### Project under development

My attempt to create game based on Duel Masters series. Game is written with Python3 and Qt Framework.

Debug mode (you don't need any internet connection to test application) is disabled by default.
To turn it on, pass an argument "--debug=True" when launching the "main.py" file:

```python main.py --debug=True```

You also need to have installed PySide2 on your Python interpreter.
Run ```pip install -r requirements.txt``` to install all required libraries in your python interpeter.

#### Todo things:
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

Effects implemented:
* teleport cards from bf to hand (test mana teleport and your cards teleport)
* draw cards (test if working)
* power attacker (test if working)


Card images were taken from:
* https://duelmasters.fandom.com/wiki/Duel_Masters_Wiki
* http://www.ccgdb.com/duelmasters/

Message system (TODO: translate to English):
        0 - you start the game
        1 - przeciwnik zaczyna grę
        2 - koniec mojej tury
        3 - ja dobieram kartę
        4,x,y - ja zagrywam kartę o id x na miejscu y na pole bitwy
        5,v,x,y - gracz v podnosi kartę z pól x z miejsca y do ręki
                  v - 0/1 - przeciwnik/ty
                  x - 0/1 - mana/pole bitwy
        6,v,x,y - gracz v podnosi kartę z pól x z miejsca y na cmentarz
                  v - 0/1 - przeciwnik/ty
                  x - 0/1 - mana/pole bitwy
        7,x - ja dodaję kartę x z ręki na mane
        8,x,y - ja dodaję kartę x z reki na tarczę y
        9,x,y - ja tapuje/odtapuje manę
                x - 0/1 - odtapuje/tapuje
                y - pozycja karty na manie
        10,x - ja zaglądam w swoją tarczę na pozycji x
        11,x,y - ja zaglądam w twoją tarczę/kartę z reki na pozycji y
                x - 0/1 - ręka/tarcza
        12,x,y - (info) ja atakuje swoją kartą x twoją kartę y na polu bitwy
        13,x - ja niszcze ci tarczę na pozycji x