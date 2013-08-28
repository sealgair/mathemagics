class Menu(object):
    """..."""
    def __init__(self, title):
        """..."""
        self.choices = {}
        self.choice = None
        self.description = title
    
    def __str__(self):
        return self.title
        
    def open(self):
        """..."""
    
    def notify(self, event):
        """..."""