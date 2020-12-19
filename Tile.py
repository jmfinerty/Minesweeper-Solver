
class Tile:
    
    def __init__(self):
        self.is_mined = False
        self.is_flagged = False
        self.is_opened = False
        self.number = None
        self.xy = [None, None]

    def print_summary(self):
        print("BOMB:", self.is_mined)
        print("FLAG:", self.is_flagged)
        print("OPEN:", self.is_opened)
        print("XY X:", self.xy[0])
        print("XY Y:", self.xy[1])
