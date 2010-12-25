Requirements:
* pygame
* PyYAML
* ipython

views/hex_view.py is the working demo, run it with:
$ ipython views/hex_view.py

squad1.yaml contains the squad used by Player1 (p1)
squad2.yaml contains the squad used by Player2 (p2)
Edit them to your liking... there is no validation on the files,
if there is nosense in the files, any number of borked things 
could happen.

Use the up and down arrows to highlight an item in a pane.
Use the return key to select an item in a pane.
Red tiles are tiles the unit can attack
Blue tiles are tiles the unit can move to
Purple tiles are tiles that the unit can move to or attack

tests/ provides some simple examples... 
