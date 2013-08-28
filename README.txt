MATHEMAGICS

Mathemagics is a proof-of-concept for an educational RPG dueling engine.  The general idea behind the engine being
that casting a spell requires solving a simple multiplication problem (which, in practice, can be substituted
with any number of simple questions with defined or multiple-choice responses.)

Current Features:
* The faster the problem is solved, the more powerful the spell will be.
* If the hero fails to solve the problem in the alloted time, or submits an incorrect solution, the 
	spell backfires and deals damage to the hero.
* The enemy will attack asynchronously at (somewhat) random intervals (e.g. 5-10 seconds between attacks)
* At current, when a game is over the program must be closed and repoened to start a new duel

Future features to be implemented:
* Respawn of hero and enemy
* Weighting of difficulty of problem (0 X 5 is easier than 3 X 4 is easier than 6 X 7)
* Defense system to allow hero to defend attacks from enemies
* Multiple enemies (including targeting system)
* Multiple types of 'spells" (e.g. addition, fractions, conjugation, etc.)
* Configurable control scheme
* Multiplayer action to allow duels between human opponents
* Network play to allow players to duel online
* Friendly Actors to allow players to cooperate (or to allow for friendly NPC's)

Dependencies:
Mathemagics requires Python 2.5 or better and Pygame 1.8 or better to be installed.
You can download Python here: http://www.python.org/download/
You can download Pygame here: http://www.pygame.org/download.shtml

To Run:
From the mathemagics directory (which contains the file main.py) run the following command:
python main.py

To Play:
* Press the space bar to start a spell
* Type the solution to the spell using the number keys (you can use the delete key for typos)
* Press Enter to attempt to cast the spell
* Press ESC to quit

To Run Test Cases:
From the mathemagics directory (which contains the file main.py) run the following command:
python test.py

Code created based on tutorial by sjbrown:
http://ezide.com/games/writing-games.html

Notes to OpenSourcery:
I have included this application as an example of a straightforward solution to a unique problem, 
incorporating elements of graphically-minded programming and a dynamic user interface. 