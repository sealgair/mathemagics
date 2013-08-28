from EventManager import *
from controller import *
from view import *
from model import *

def main():
    """Put everthing into motion -- with as few lines of code as possible."""
    keybd = KeyboardController()
    spinner = CPUSpinnerController()
    pygameView = PygameView()
    game = Game()
    
    spinner.Run()

if __name__ == "__main__":
        main()
