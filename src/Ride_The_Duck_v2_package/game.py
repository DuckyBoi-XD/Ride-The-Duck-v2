import pygame
import random
import json
import base64
import os
import codecs
import math
from pathlib import Path
from pygame.locals import *

ASSETS_DIR = Path(__file__).resolve().parent / "assets"


def asset_path(relative_path):
    """Return the installed package path for an asset."""
    return str(ASSETS_DIR / relative_path)

def to_binary_str(s):
    '''binary encoder'''
    return ''.join(format(ord(c), '08b') for c in s)

def from_binary_str(b):
    '''binary decoder'''
    if len(b) % 8 != 0:
        raise ValueError("Binary string length must be divisible by 8")
    if not all(c in '01' for c in b):
        raise ValueError("Binary string must only contain 0s and 1s")
    
    chars = [chr(int(b[i:i+8], 2)) for i in range(0, len(b), 8)]
    return ''.join(chars)

def encode_save(json_str):
    '''encodes using method under'''
    # Base64 encode
    b64 = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
    # Reverse
    rev = b64[::-1]
    # ROT13 encode CHIP
    rot = codecs.encode(rev, 'rot_13')
    # Binary encode
    binary = to_binary_str(rot)
    return binary.encode('utf-8')

def decode_save(encoded_bytes):
    '''decodes using method under'''
    # grabs code
    binary_str = encoded_bytes.decode('utf-8')
    # Binary decode
    rot = from_binary_str(binary_str)
    # ROT13 decode
    rev = codecs.decode(rot, 'rot_13')
    # Reverse
    b64 = rev[::-1]
    # Base64 decode
    json_str = base64.b64decode(b64).decode('utf-8')
    return json_str


def get_config_dir():
    '''Return platform-appropriate config directory'''
    return os.path.expanduser("~/.config/Ride-The-Duck-v2")

def load_game(): # access save file -JSON
    '''loading save file - returns pat game data'''
    global savefile_value
    config_dir = get_config_dir()
    save_path = os.path.join(config_dir, "Ride-The-Duck-v2.bin")
    try:
        with open(save_path, "rb") as f:
            encoded_bytes = f.read()
            json_str = decode_save(encoded_bytes)
            data = json.loads(json_str)
            savefile_value = 1
            return (data.get("Chips", [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
                    data.get("Stats", {"rounds played" : 0, "2x wins" : 0, "3x wins" : 0, "4x wins" : 0, "20x wins" : 0, "wins" : 0, "loses" : 0, "push back" : 0, "money earnt" : 0}))
                    
    except FileNotFoundError:
        savefile_value = 2
        return [5, 2, 1, 0, 0, 0, 0, 0, 0, 0], {"rounds played" : 0, "2x wins" : 0, "3x wins" : 0, "4x wins" : 0, "20x wins" : 0, "wins" : 0, "loses" : 0, "push back" : 0, "money earnt" : 0}
    except (ValueError, json.JSONDecodeError) as error:
        print(f"Corrupted save file - using defaults. Error: {error}")
        savefile_value = 3  
        return [5, 2, 1, 0, 0, 0, 0, 0, 0, 0], {"rounds played" : 0, "2x wins" : 0, "3x wins" : 0, "4x wins" : 0, "20x wins" : 0, "wins" : 0, "loses" : 0, "push back" : 0, "money earnt" : 0}

def save_game(chip_info = None, stats = None):
    '''saving game data'''
    if chip_info is None:
        chip_info = CHIPS
    if stats is None:
        stats = STATS

    data = {
        "Chips": chip_info,
        "Stats": stats
    }
    json_str = json.dumps(data)
    encoded_bytes = encode_save(json_str)
    config_dir = get_config_dir()
    os.makedirs(config_dir, exist_ok=True)
    save_path = os.path.join(config_dir, "Ride-The-Duck-v2.bin")
    with open(save_path, "wb") as f:
        f.write(encoded_bytes)

CHIPS, STATS = load_game()

def cosd(x):
    return math.cos(math.radians(x))
def sind(x):
    return math.sin(math.radians(x))


class game_variable: # Game variables
    def __init__(self):
        pygame.init()
        self.displayWidth, self.displayHeight = 1200, 700
        self.display = pygame.display.set_mode((self.displayWidth, self.displayHeight), pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.table_colour = (20, 86, 62)
        self.table_colour_accent = (37, 64, 64)
        global CHIPS, STATS

        self.white_colour = (255, 255, 255)
        self.red_colour = (159, 27, 39)
        self.blue_colour = (21, 38, 110)
        self.green_colour = (27, 120, 75)
        self.black_colour = (9, 14, 18)
        self.bright_purple_colour = (127, 101, 227)
        self.yellow_colour = (241, 208, 93)
        self.orange_colour = (255, 176, 60)
        self.dark_blue = (62, 72, 161)
        self.light_blue = (110, 177, 255)
        self.bright_green = (109, 255, 108)
        self.yellow_green = (183, 255, 0)
        self.bright_red = (255, 49, 49)
        self.highlight_yellow = (249, 203, 26)
        self.bright_blue = (14, 142, 255)
        self.bright_orange = (255, 127, 14)

        self.darkgreen_colour = (18, 78, 49)
        self.darkred_colour = (115, 20, 28)
        self.darkblue_colour = (13, 23, 67)
        self.darkorange_colour = (239, 142, 0)

        self.button_blue = (34, 87, 122)
        self.button_blue2 = (56, 163, 165)
        self.button_green = (87, 204, 153)
        self.button_green2 = (128, 237, 153)

        self.button_blue_dark = (17, 43, 61)
        self.button_blue2_dark = (28, 81, 82)
        self.button_green_dark = (34, 112, 78)
        self.button_green2_dark = (23, 160, 54)

        self._running = True

        self.chipRadius = 40
        self.smallChipRadius = 20
        self.chipPos = [600, 350]
        self.chipCurrentPos = [600, 350]
        self.chipArcAngles = (270, 330, 30, 90, 150, 210)
        self.chipValues = ("1", "5", "10", "25", "100", "500", "1000", "5000", "25000", "100000")
        self.chipValuePositions = ((0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (8, 0), (9, 0))

        chipPositions1 = []
        chipPositions5 = []
        chipPositions10 = []
        chipPositions25 = []
        chipPositions100 = []
        chipPositions500 = []
        chipPositions1000 = []
        chipPositions5000 = []
        chipPositions25000 = []
        chipPositions100000 = []

        self.chipPositions = (chipPositions1, chipPositions5, chipPositions10, chipPositions25, chipPositions100, chipPositions500,
                            chipPositions1000, chipPositions5000, chipPositions25000, chipPositions100000)
        self.chipValueColours = (self.white_colour, self.red_colour, self.blue_colour, self.green_colour, self.black_colour, 
                                 self.bright_purple_colour, self.yellow_colour, self.orange_colour, self.dark_blue, self.light_blue)
        self.chipDisplayPriority = []

        self.mouseStartPos = None
        self.mousePosChange = False

        self.threeCharFont = pygame.font.Font(asset_path("fonts/chipText.ttf"), 40)
        self.fourCharFont = pygame.font.Font(asset_path("fonts/chipText.ttf"), 30)
        self.fiveCharFont = pygame.font.Font(asset_path("fonts/chipText.ttf"), 25)
        self.sixCharFont = pygame.font.Font(asset_path("fonts/chipText.ttf"), 23)

        self.tableFont = pygame.font.Font(asset_path("fonts/tableFont.ttf"), 40)

        self.threeCharFontSmall = pygame.font.Font(asset_path("fonts/chipText.ttf"), 16)
        self.fourCharFontSmall = pygame.font.Font(asset_path("fonts/chipText.ttf"), 13)
        self.fiveCharFontSmall = pygame.font.Font(asset_path("fonts/chipText.ttf"), 10)
        self.sixCharFontSmall = pygame.font.Font(asset_path("fonts/chipText.ttf"), 8)

        self.exchangeFontFull = pygame.font.Font(asset_path("fonts/tableFont.ttf"), 30)

        self.exchangeChipAmmount = pygame.font.Font(asset_path("fonts/tableFont.ttf"), 20)
        self.betFunctionBetFont = pygame.font.Font(asset_path("fonts/tableFont.ttf"), 30)
        self.betFunctionStandFont = pygame.font.Font(asset_path("fonts/tableFont.ttf"), 20)
        self.betFunctionDoubleDownFont = pygame.font.Font(asset_path("fonts/tableFont.ttf"), 15)
        self.betFunctionSplitFont = pygame.font.Font(asset_path("fonts/tableFont.ttf"), 25)

        self.tableTextFontFull = pygame.font.Font(asset_path("fonts/tableFont.ttf"), 40)
        self.tableTextFontSemi = pygame.font.Font(asset_path("fonts/tableFont.ttf"), 25)

        self.endgamefont = pygame.font.Font(asset_path("fonts/endgameFont.ttf"), 20)
        self.endgamefontSemi = pygame.font.Font(asset_path("fonts/endgameFont.ttf"), 17)

        self.chipFontList = (self.threeCharFont, self.fourCharFont, self.fiveCharFont, self.sixCharFont)
        self.chipFontListSmall = (self.threeCharFontSmall, self.fourCharFontSmall, self.fiveCharFontSmall, self.sixCharFontSmall)
        

        self.tempcardDeck = []

        card_ranks = ("2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A")
        self.spadesCards = tuple(asset_path(f"Carddeck/Spades/{rank}.png") for rank in card_ranks)
        self.heartsCards = tuple(asset_path(f"Carddeck/Hearts/{rank}.png") for rank in card_ranks)
        self.diamondsCards = tuple(asset_path(f"Carddeck/Diamonds/{rank}.png") for rank in card_ranks)
        self.clubsCards = tuple(asset_path(f"Carddeck/Clubs/{rank}.png") for rank in card_ranks)
        
        self.CardFiles = (self.spadesCards, self.heartsCards, self.diamondsCards, self.clubsCards)
        
        self.CardSuits = ("Spades0", "Hearts1", "Diamonds2", "Clubs3")
        for suit in self.CardSuits:
            for value in range(2, 11):
                self.tempcardDeck.append(f"{suit[-1]}{value}")
            self.tempcardDeck.append(f"{suit[-1]}11")
            self.tempcardDeck.append(f"{suit[-1]}12")
            self.tempcardDeck.append(f"{suit[-1]}13")
            self.tempcardDeck.append(f"{suit[-1]}14")

        self.cardDeck = self.tempcardDeck * 6
        random.shuffle(self.cardDeck)
        random.shuffle(self.cardDeck)

        self.Values = (2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11)

GV = game_variable()

class game_objects:
    def game_space(self):
        pygame.draw.rect(GV.display, (0, 0, 0), (100, 100, 100, 100))

GO = game_objects()




class pygame_function:
    def __init__(self):
        self.fps = 60
        self.FPS = pygame.time.Clock()
        self.display = None
        GV._running = True

    def on_init(self):
        pygame.init()
        pygame.display.set_caption("Ride The Duck v2")
        GV._running = True

    def on_event(self, event):
        if event.type == pygame.QUIT:
            GV._running = False

    def on_render(self):
        GV.display.fill(GV.table_colour)
        GO.game_space()
    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        if self.on_init() == False:
            GV._running = False 
        while(GV._running):
            self.FPS.tick(self.fps)
            for event in pygame.event.get():
                self.on_event(event)
            self.on_render()

            pygame.display.flip()
        self.on_cleanup()

def main():
    Game = pygame_function()
    Game.on_execute()

if __name__ == "__main__":
    main()
