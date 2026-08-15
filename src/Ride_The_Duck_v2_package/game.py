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

        chipData1 = []
        chipData5 = []
        chipData10 = []
        chipData25 = []
        chipData100 = []
        chipData500 = []
        chipData1000 = []
        chipData5000 = []
        chipData25000 = []
        chipData100000 = []

        self.chipData = (chipData1, chipData5, chipData10, chipData25, chipData100, chipData500,
                            chipData1000, chipData5000, chipData25000, chipData100000)
        
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
        self.betFunctionBetFont = pygame.font.Font(asset_path("fonts/tableFont.ttf"), 50)
        self.betFunctionColourFont = pygame.font.Font(asset_path("fonts/tableFont.ttf"), 30)
        self.betFunctionInOutFont = pygame.font.Font(asset_path("fonts/tableFont.ttf"), 25)
        self.betFunctionSplitFont = pygame.font.Font(asset_path("fonts/tableFont.ttf"), 25)

        self.tableTextFontFull = pygame.font.Font(asset_path("fonts/tableFont.ttf"), 40)
        self.tableTextFontSemi = pygame.font.Font(asset_path("fonts/tableFont.ttf"), 25)

        self.endgamefont = pygame.font.Font(asset_path("fonts/endgameFont.ttf"), 20)
        self.endgamefontSemi = pygame.font.Font(asset_path("fonts/endgameFont.ttf"), 17)

        self.chipFontList = (self.threeCharFont, self.fourCharFont, self.fiveCharFont, self.sixCharFont)
        self.chipFontListSmall = (self.threeCharFontSmall, self.fourCharFontSmall, self.fiveCharFontSmall, self.sixCharFontSmall)

        self.chipExchangePosChords1 = []
        self.chipExchangePosChords2 = []
        self.chipExchangePosChordsOutline1 = []
        self.chipExchangePosChordsOutline2 = []

        self.chipExchange = []
        self.chipExchangeOn = False
        self.chipExchangehighlightOn = False
        self.chipExchangeHighlight = []

        self.chipExchangeValue1 = 0
        self.chipExchangeValue2 = 0
        self.chipExchangeStr1 = "0"
        self.chipExchangeStr2 = "0"
        self.exchangeChipSelection = 0

        self.chipSmallExchangeList = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        self.chipSmallExchangeListtemp = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        self.exchangeChipPos = []
        self.tempcardDeck = []

        self.round = 0 # 0: none, 1: br, 2: hl, 3: io:, 4: suit

        self.spadesImage = asset_path(f"suits/spades.png")
        self.heartsImage = asset_path(f"suits/hearts.png")
        self.clubsImage = asset_path(f"suits/clubs.png")
        self.diamondsImage = asset_path(f"suits/diamonds.png")
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

        self.chipStartPositions = {}
        for index, i in enumerate(self.chipValues): # Starting value of chips
            startingx = index * 100 + (index+1)*(200/11) + 50
            self.chipStartPositions[i] = (startingx, 650)

        for index, i in enumerate(CHIPS):
            if i != 0:
                self.offset = 5
                self.offsetreal = 0
                self.sideOffset = 0
                for _ in range(0, i):
                    self.sideOffset = int(str(self.offset/350)[0]) * 5
                    self.offset = self.offset - int(str(self.offset/350)[0]) * 350
                    self.chipData[index].append({"value": self.chipValues[index],
                                                 "colour": self.chipValueColours[index],
                                                 "position": [((self.chipStartPositions)[self.chipValues[index]])[0] - self.sideOffset, ((self.chipStartPositions[self.chipValues[index]])[1] - self.offset)],
                                                 "override": False
                                                })
                    self.offset += 10
                    self.offsetreal += 10

        for indexa, lista in enumerate(self.chipData):
            for indexb, value in enumerate(lista):
                self.chipDisplayPriority.append((indexa, indexb))


GV = game_variable()

class game_objects:
    def __init__(self):
        self.chipCirclePoints1 = []
        self.chipCirclePoints2 = []
        self.chipCirclePoints3 = []
        self.chipCirclePoints4 = []
        self.chipCirclePoints5 = []
        self.chipCirclePoints6 = []
        self.chipCirclePointsList = (self.chipCirclePoints1, self.chipCirclePoints2, self.chipCirclePoints3, 
                                     self.chipCirclePoints4, self.chipCirclePoints5, self.chipCirclePoints6)
        self.chipCirclePointsReverse = []

        self.chipCirclePointsSmall1 = []
        self.chipCirclePointsSmall2 = []
        self.chipCirclePointsSmall3 = []
        self.chipCirclePointsSmall4 = []
        self.chipCirclePointsSmall5 = []
        self.chipCirclePointsSmall6 = []
        self.chipCirclePointsListSmall = (self.chipCirclePoints1, self.chipCirclePoints2, self.chipCirclePoints3, 
                                     self.chipCirclePoints4, self.chipCirclePoints5, self.chipCirclePoints6)
        self.chipCirclePointsReverseSmall = []

        GV.chipExchangePosChords2.append((613.1174117891126, 0))
        GV.chipExchangePosChordsOutline2.append((613.1174117891126, 0))
        for delta in range(271, 302, 1):
            GV.chipExchangePosChords2.append(((cosd(delta) * 1210) + 592, 
                                              -1010 - (sind(delta) * 1210)))
            GV.chipExchangePosChordsOutline2.append(((cosd(delta) * 1210) + 592, -1010 - (sind(delta) * 1210)))
        GV.chipExchangePosChords2.append((1200, 0))


        GV.chipExchangePosChords1.append((0, 0))
        for delta in range(240, 270, 1):
            GV.chipExchangePosChords1.append(((cosd(delta) * 1210) + 608, -1010 - (sind(delta) * 1210)))
            GV.chipExchangePosChordsOutline1.append(((cosd(delta) * 1210) + 608, -1010 - (sind(delta) * 1210)))
        GV.chipExchangePosChords1.append((586.882588210887, 0))
        GV.chipExchangePosChordsOutline1.append((586.882588210887, 0))

    def on_init(self):
        self.chipCirclePoints1 = []
        self.chipCirclePoints2 = []
        self.chipCirclePoints3 = []
        self.chipCirclePoints4 = []
        self.chipCirclePoints5 = []
        self.chipCirclePoints6 = []
        self.chipCirclePointsList = (self.chipCirclePoints1, self.chipCirclePoints2, self.chipCirclePoints3, 
                                     self.chipCirclePoints4, self.chipCirclePoints5, self.chipCirclePoints6)
        self.chipCirclePointsReverse = []

        self.chipCirclePointsSmall1 = []
        self.chipCirclePointsSmall2 = []
        self.chipCirclePointsSmall3 = []
        self.chipCirclePointsSmall4 = []
        self.chipCirclePointsSmall5 = []
        self.chipCirclePointsSmall6 = []
        self.chipCirclePointsListSmall = (self.chipCirclePoints1, self.chipCirclePoints2, self.chipCirclePoints3, 
                                     self.chipCirclePoints4, self.chipCirclePoints5, self.chipCirclePoints6)
        self.chipCirclePointsReverseSmall = []
    def chip_objects(self):
        for value in GV.chipDisplayPriority:
            for listpostions in self.chipCirclePointsList:
                listpostions.clear()
            pos = ((GV.chipData[value[0]])[value[1]])["position"]

            # Base chip
            pygame.draw.circle(GV.display, ((GV.chipData[value[0]])[value[1]])["colour"], pos, GV.chipRadius)

            # Chip Arc Accent Positioning
            for b, valueb in enumerate(GV.chipArcAngles):
                self.chipCirclePointsReverse = []
                for delta in range (valueb-10, valueb+11, 2):
                    self.chipCirclePointsList[b].append([
                        (cosd(delta) * (GV.chipRadius)) + (pos)[0], 
                        (sind(delta) * (GV.chipRadius)) + (pos)[1]
                    ])
                    self.chipCirclePointsReverse.append([
                        (cosd(delta) * (GV.chipRadius - 7)) + (pos)[0], 
                        (sind(delta) * (GV.chipRadius - 7)) + (pos)[1]
                    ])
                self.chipCirclePointsReverse.reverse()
                for c in self.chipCirclePointsReverse:
                    self.chipCirclePointsList[b].append(c)

            # Chip Accent Creation
            for i in self.chipCirclePointsList:
                if GV.chipValueColours[value[0]] == GV.white_colour:
                    pygame.draw.polygon(GV.display, GV.blue_colour, i)
                else:
                    pygame.draw.polygon(GV.display, GV.white_colour, i)

            # Font Creation
            chip = GV.chipValues[value[0]]
            if len(chip) <= 3: # Grabs the font depending on value
                chipFontFont = GV.chipFontList[0]
            elif len(chip) >= 4:
                chipFontFont = GV.chipFontList[len(chip) - 3]

            if GV.chipValueColours[value[0]] == GV.white_colour:
                chipText = chipFontFont.render(GV.chipValues[value[0]], True, GV.blue_colour)
            else:
                chipText = chipFontFont.render(GV.chipValues[value[0]], True, GV.white_colour)
            chipTextRect = chipText.get_rect(center=(pos))
            GV.display.blit(chipText, chipTextRect)

            chipOutlineColour = None
            chipOutlineWidth = None

            chipPositionx = (((GV.chipData[value[0]])[value[1]])["position"])[0]
            chipPositiony = (((GV.chipData[value[0]])[value[1]])["position"])[1]
            exchange_remove = True

            for position in GV.chipExchangePosChords2:
                if 613.1174117891126 <= chipPositionx <= position[0] and -100 <= chipPositiony <= position[1]:
                    exchange_remove = False
                    if value not in GV.chipExchange:
                        GV.chipExchange.append(value)
                        GV.chipExchangeOn = True
                    break

            if exchange_remove:
                if value in GV.chipExchange: 
                        GV.chipExchange.remove(value)
                if not GV.chipExchange:
                    GV.chipExchangeOn = False
                    GV.chipExchangeValue1 = 0
                    GV.chipExchangeValue2 = 0
                    GV.chipSmallExchangeListtemp = list(GV.chipSmallExchangeList)
                    GV.chipExchangeStr1 = None

            if GV.mousePosChange and value == GV.chipDisplayPriority[-1]:
                # Chip outline
                if value in GV.chipExchange:
                    chipOutlineColour = GV.yellow_green
                    chipOutlineWidth = 2
                elif GV.chipValueColours[value[0]] == GV.yellow_colour:
                    chipOutlineColour = GV.orange_colour
                    chipOutlineWidth = 2
                else:
                    chipOutlineColour = GV.yellow_colour
                    chipOutlineWidth = 2

            elif value in GV.chipExchange:
                chipOutlineColour = GV.bright_green
                chipOutlineWidth = 2
                
            elif GV.chipValueColours[value[0]] == GV.black_colour or GV.chipValueColours[value[0]] == GV.blue_colour:
                chipOutlineColour = GV.white_colour
                chipOutlineWidth = 1
            else:
                chipOutlineColour = GV.black_colour
                chipOutlineWidth = 1

            if chipOutlineWidth == 2:
                pygame.draw.circle(GV.display, chipOutlineColour, (pos[0], pos[1]), 42, width=3)
            else:
                pygame.draw.circle(GV.display, chipOutlineColour, (pos[0], pos[1]), 42, width=2)
    
    def game_space(self):
        pygame.draw.arc(GV.display, GV.white_colour, (-600, -2180, 2400, 2400), 0, 360, 3)
        pygame.draw.arc(GV.display, GV.white_colour, (-660, -2240, 2520, 2520), 0, 360, 3)

        pygame.draw.polygon(GV.display, GV.table_colour_accent, GV.chipExchangePosChords2)
        pygame.draw.lines(GV.display, GV.white_colour, False, GV.chipExchangePosChordsOutline2, 5)

        pygame.draw.polygon(GV.display, GV.table_colour_accent, GV.chipExchangePosChords1)
        pygame.draw.lines(GV.display, GV.white_colour, False, GV.chipExchangePosChordsOutline1, 5)

        tabelText = GV.tableTextFontFull.render(("RIDE"), True, GV.white_colour)
        tableTextRotated = pygame.transform.rotate(tabelText, 355)
        tableTextRect = tabelText.get_rect(center=(490, 240))
        GV.display.blit(tableTextRotated, tableTextRect)

        tabelText = GV.tableTextFontFull.render(("THE"), True, GV.white_colour)
        tableTextRotated = pygame.transform.rotate(tabelText, 0)
        tableTextRect = tabelText.get_rect(center=(600, 248))
        GV.display.blit(tableTextRotated, tableTextRect)

        tabelText = GV.tableTextFontFull.render(("DUCK"), True, GV.white_colour)
        tableTextRotated = pygame.transform.rotate(tabelText, 4.5)
        tableTextRect = tabelText.get_rect(center=(715, 238))
        GV.display.blit(tableTextRotated, tableTextRect)

        tabelText = GV.tableTextFontFull.render(("2x"), True, GV.white_colour)
        tableTextRotated = pygame.transform.rotate(tabelText, 335)
        tableTextRect = tabelText.get_rect(center=(90, 134))
        GV.display.blit(tableTextRotated, tableTextRect)

        tabelText = GV.tableTextFontFull.render(("3x"), True, GV.white_colour)
        tableTextRotated = pygame.transform.rotate(tabelText, 344)
        tableTextRect = tabelText.get_rect(center=(260, 198))
        GV.display.blit(tableTextRotated, tableTextRect)

        tabelText = GV.tableTextFontFull.render(("4x"), True, GV.white_colour)
        tableTextRotated = pygame.transform.rotate(tabelText, 15)
        tableTextRect = tabelText.get_rect(center=(925, 198))
        GV.display.blit(tableTextRotated, tableTextRect)

        tabelText = GV.tableTextFontFull.render(("20x"), True, GV.white_colour)
        tableTextRotated = pygame.transform.rotate(tabelText, 25)
        tableTextRect = tabelText.get_rect(center=(1095, 130))
        GV.display.blit(tableTextRotated, tableTextRect)

        if GV.chipExchangeOn:
            widthSpacing = 150/11
            GV.chipExchangeValue2 = 0
            for item in GV.chipDisplayPriority:
                if item in GV.chipExchange:
                    GV.chipExchangeValue2 += int(GV.chipValues[item[0]])
            GV.chipExchangeStr2 = (f"{GV.chipExchangeValue2:,}")

            GV.exchangeChipPos = []
            for chipIndexSelection in GV.chipValuePositions:
                for listpostions in self.chipCirclePointsListSmall:
                    listpostions.clear()

                # Circle Positions
                widthSpacing = (chipIndexSelection[0] * 40) + ((100/10) * (chipIndexSelection[0] + 2)) + 70
                smallChipPos = (widthSpacing, 20)

                GV.exchangeChipPos.append(smallChipPos)

                # Base circle
                pygame.draw.circle(GV.display, GV.chipValueColours[chipIndexSelection[0]], smallChipPos, GV.smallChipRadius)

                # Chip font
                chip = GV.chipValues[chipIndexSelection[0]]
                if len(chip) <= 3:
                    chipFontSmall = GV.chipFontListSmall[0]
                elif len(chip) >= 4:
                    chipFontSmall = GV.chipFontListSmall[len(chip) - 3]

                if GV.chipValueColours[chipIndexSelection[0]] == GV.white_colour:
                    chipText = chipFontSmall.render(GV.chipValues[chipIndexSelection[0]], True, GV.blue_colour)
                else:
                    chipText = chipFontSmall.render(GV.chipValues[chipIndexSelection[0]], True, GV.white_colour)
                chipTextRect = chipText.get_rect(center=(smallChipPos))
                GV.display.blit(chipText, chipTextRect)

                # Calculating small chip accent
                for b, value in enumerate(GV.chipArcAngles):
                    self.chipCirclePointsReverseSmall = []
                    for delta in range (value-10, value+11, 2):
                        self.chipCirclePointsListSmall[b].append([
                            (cosd(delta) * (GV.smallChipRadius)) + (smallChipPos)[0], 
                            (sind(delta) * (GV.smallChipRadius)) + (smallChipPos)[1]
                        ])
                        self.chipCirclePointsReverseSmall.append([
                            (cosd(delta) * (GV.smallChipRadius - 4)) + (smallChipPos)[0], 
                            (sind(delta) * (GV.smallChipRadius - 4)) + (smallChipPos)[1]
                        ])
                    self.chipCirclePointsReverseSmall.reverse()
                    for c in self.chipCirclePointsReverseSmall:
                        self.chipCirclePointsListSmall[b].append(c)

                # prints accent
                for i in self.chipCirclePointsList:
                    if GV.chipValueColours[chipIndexSelection[0]] == GV.white_colour:
                        pygame.draw.polygon(GV.display, GV.blue_colour, i)
                    else:
                        pygame.draw.polygon(GV.display, GV.white_colour, i)

                # sets outline colour
                if int(GV.chipValues[chipIndexSelection[0]]) > GV.chipExchangeValue2 or int(GV.chipValues[chipIndexSelection[0]]) > GV.chipExchangeValue2-GV.chipExchangeValue1 or int(GV.chipValues[chipIndexSelection[0]]) == int(GV.chipValues[GV.chipExchange[0][0]]):
                    chipOutlineColour = GV.bright_red
                elif GV.exchangeChipPos[chipIndexSelection[0]] == GV.chipExchangeHighlight:
                    chipOutlineColour = GV.bright_green
                elif GV.chipValueColours[chipIndexSelection[0]] == GV.black_colour or GV.chipValueColours[chipIndexSelection[0]] == GV.blue_colour:
                    chipOutlineColour = GV.white_colour
                else:
                    chipOutlineColour = GV.black_colour

                pygame.draw.circle(GV.display, chipOutlineColour, (smallChipPos[0], smallChipPos[1]), 21, width=1)   

                # Chip ammount indicator

                chipAmmountIndicator = GV.exchangeChipAmmount.render(str(GV.chipSmallExchangeListtemp[chipIndexSelection[0]]), True, GV.white_colour)
                CAIrect = chipAmmountIndicator.get_rect(center=(smallChipPos[0], 50))
                GV.display.blit(chipAmmountIndicator, CAIrect)

            # Exchange values box
            pygame.draw.rect(GV.display, GV.table_colour, (350, 65, 180, 40))
            pygame.draw.rect(GV.display, GV.white_colour, (350, 65, 180, 40), width=2)

            pygame.draw.rect(GV.display, GV.table_colour, (350, 115, 180, 40))
            pygame.draw.rect(GV.display, GV.white_colour, (350, 115, 180, 40), width=2)

            exchangeValueText = GV.exchangeFontFull.render(GV.chipExchangeStr2, True, GV.white_colour)
            exchangeValueTextRect = exchangeValueText.get_rect(center=(440, 135))
            GV.display.blit(exchangeValueText, exchangeValueTextRect)

            exchangeValueText = GV.exchangeFontFull.render(GV.chipExchangeStr1, True, GV.white_colour)
            exchangeValueTextRect = exchangeValueText.get_rect(center=(440, 85))
            GV.display.blit(exchangeValueText, exchangeValueTextRect)

            if GV.chipExchangeValue1 == GV.chipExchangeValue2:
                pygame.draw.circle(GV.display, GV.bright_green, (280, 105), 30)
            else:
                pygame.draw.circle(GV.display, GV.red_colour, (280, 105), 30)
            pygame.draw.circle(GV.display, GV.white_colour, (280, 105), 30, width=2)

        GV.round = 4
        if GV.round == 0:
            pygame.draw.rect(GV.display, GV.table_colour_accent, (303, 350, 75, 150))
            pygame.draw.rect(GV.display, GV.table_colour_accent, (822, 350, 75, 150))
            buttontext1 = GV.betFunctionBetFont.render(f"BET", True, GV.white_colour)
            buttontext2 = GV.betFunctionBetFont.render(f"BET", True, GV.white_colour)
            buttontext1_rotated = pygame.transform.rotate(buttontext1, 90)
            buttontext2_rotated = pygame.transform.rotate(buttontext2, 270)
            buttontext1rect1 = buttontext1_rotated.get_rect(center=(340, 425))
            buttontext2rect2 = buttontext2_rotated.get_rect(center=(860, 425))
            GV.display.blit(buttontext1_rotated, buttontext1rect1)
            GV.display.blit(buttontext2_rotated, buttontext2rect2)
        elif GV.round == 1:
            pygame.draw.rect(GV.display, GV.black_colour, (303, 350, 75, 150))
            pygame.draw.rect(GV.display, GV.red_colour, (822, 350, 75, 150))
            buttontext1 = GV.betFunctionColourFont.render(f"BLACK", True, GV.white_colour)
            buttontext2 = GV.betFunctionColourFont.render(f"RED", True, GV.white_colour)
            buttontext1_rotated = pygame.transform.rotate(buttontext1, 90)
            buttontext2_rotated = pygame.transform.rotate(buttontext2, 270)
            buttontext1rect1 = buttontext1_rotated.get_rect(center=(340, 425))
            buttontext2rect2 = buttontext2_rotated.get_rect(center=(860, 425))
            GV.display.blit(buttontext1_rotated, buttontext1rect1)
            GV.display.blit(buttontext2_rotated, buttontext2rect2)
        elif GV.round == 2:
            pygame.draw.rect(GV.display, GV.black_colour, (303, 350, 75, 150))
            pygame.draw.rect(GV.display, GV.red_colour, (822, 350, 75, 150))
            buttontext1 = GV.betFunctionColourFont.render(f"ABOVE", True, GV.white_colour)
            buttontext2 = GV.betFunctionColourFont.render(f"BELOW", True, GV.white_colour)
            buttontext1_rotated = pygame.transform.rotate(buttontext1, 90)
            buttontext2_rotated = pygame.transform.rotate(buttontext2, 270)
            buttontext1rect1 = buttontext1_rotated.get_rect(center=(340, 425))
            buttontext2rect2 = buttontext2_rotated.get_rect(center=(860, 425))
            GV.display.blit(buttontext1_rotated, buttontext1rect1)
            GV.display.blit(buttontext2_rotated, buttontext2rect2)
        elif GV.round == 3:
            pygame.draw.rect(GV.display, GV.black_colour, (303, 350, 75, 150))
            pygame.draw.rect(GV.display, GV.red_colour, (822, 350, 75, 150))
            buttontext1 = GV.betFunctionInOutFont.render(f"INSIDE", True, GV.white_colour)
            buttontext2 = GV.betFunctionInOutFont.render(f"OUTSIDE", True, GV.white_colour)
            buttontext1_rotated = pygame.transform.rotate(buttontext1, 90)
            buttontext2_rotated = pygame.transform.rotate(buttontext2, 270)
            buttontext1rect1 = buttontext1_rotated.get_rect(center=(340, 425))
            buttontext2rect2 = buttontext2_rotated.get_rect(center=(860, 425))
            GV.display.blit(buttontext1_rotated, buttontext1rect1)
            GV.display.blit(buttontext2_rotated, buttontext2rect2)
        elif GV.round == 4:
            pygame.draw.rect(GV.display, GV.table_colour_accent, (303, 350, 75, 75))
            pygame.draw.rect(GV.display, GV.table_colour_accent, (303, 425, 75, 75))

            pygame.draw.line(GV.display, GV.white_colour, (303, 425), (375, 425), 3)

            pygame.draw.rect(GV.display, GV.table_colour_accent, (822, 350, 75, 75))
            pygame.draw.rect(GV.display, GV.table_colour_accent, (822, 425, 75, 75))

            pygame.draw.line(GV.display, GV.white_colour, (822, 425), (894, 425), 3)


            spadesuit = pygame.transform.smoothscale(pygame.image.load((GV.spadesImage)), (75, 75)).convert_alpha()
            rect = spadesuit.get_rect(center=(340.5, 387.5))
            GV.display.blit(spadesuit, rect)

            heartsuit = pygame.transform.smoothscale(pygame.image.load((GV.heartsImage)), (75, 75)).convert_alpha()
            rect = heartsuit.get_rect(center=(340.5, 462.5))
            GV.display.blit(heartsuit, rect)

            diamondsuit = pygame.transform.smoothscale(pygame.image.load((GV.diamondsImage)), (75, 75)).convert_alpha()
            rect = diamondsuit.get_rect(center=(859.5, 387.5))
            GV.display.blit(diamondsuit, rect)

            clubsuit = pygame.transform.smoothscale(pygame.image.load((GV.clubsImage)), (75, 75)).convert_alpha()
            rect = clubsuit.get_rect(center=(858, 462.5))
            GV.display.blit(clubsuit, rect)

        pygame.draw.rect(GV.display, (255, 255, 255), (303, 350, 75, 150), 3)
        pygame.draw.rect(GV.display, (255, 255, 255), (822, 350, 75, 150), 3)
        pygame.draw.rect(GV.display, GV.highlight_yellow, (375, 350, 450, 150), 3)

GO = game_objects()

class game_functions():
    def player_function(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GV._running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if int(list(reversed(GV.chipValues))[GV.exchangeChipSelection]) < GV.chipExchangeValue2 or (int(list(reversed(GV.chipValues))[GV.exchangeChipSelection]) == GV.chipExchangeValue2 and len(GV.chipExchange)!= 1):
                    if int(list(reversed(GV.chipValues))[GV.exchangeChipSelection]) <= GV.chipExchangeValue2-GV.chipExchangeValue1:
                        if event.button == 1:
                            if GV.chipExchangehighlightOn:
                                GV.chipSmallExchangeListtemp.reverse()
                                GV.chipSmallExchangeListtemp[GV.exchangeChipSelection] += 1
                                GV.chipSmallExchangeListtemp.reverse()
                                GV.chipExchangeValue1 = 0

                                for indexexclist, value in enumerate(reversed(GV.chipSmallExchangeListtemp)):
                                    if value > 0:
                                        GV.chipExchangeValue1 += value * int(list(reversed(GV.chipValues))[indexexclist])
                                GV.chipExchangeStr1 = (f"{GV.chipExchangeValue1:,}")
                if event.button == 3:
                    if GV.chipExchangehighlightOn:
                        GV.chipSmallExchangeListtemp.reverse()
                        if GV.chipSmallExchangeListtemp[GV.exchangeChipSelection] > 0:
                            GV.chipSmallExchangeListtemp[GV.exchangeChipSelection] -= 1
                            GV.chipExchangeValue1 = 0

                            for indexexclist, value in enumerate(GV.chipSmallExchangeListtemp):
                                if value > 0:
                                    GV.chipExchangeValue1 += value * int(list(reversed(GV.chipValues))[indexexclist])
                            GV.chipExchangeStr1 = (f"{GV.chipExchangeValue1:,}")
                        GV.chipSmallExchangeListtemp.reverse()
                if event.button == 1:
                    cursorPosx, cursorPosy = pygame.mouse.get_pos()
                    for self.index_var in reversed(GV.chipDisplayPriority):
                        CursorPos_CirclePosx = cursorPosx - (((GV.chipData[self.index_var[0]])[self.index_var[1]])["position"])[0]
                        CursorPos_CirclePosy = cursorPosy - (((GV.chipData[self.index_var[0]])[self.index_var[1]])["position"])[1]

                        CursorPos_CirclePos = CursorPos_CirclePosx**2 + CursorPos_CirclePosy**2
                        '''
                        if GV.bettingGame:
                            if CursorPos_CirclePos <= GV.chipRadius**2 and GV.dOutcome:
                                GV.bettingGame = False

                            elif self.index_var in GV.chipBet2 or self.index_var in GV.chipBet3:
                                GV.betChipOverride = True

                            elif self.index_var in GV.chipBet1 and GV.splitOverride1:
                                GV.betChipOverride = True

                            elif self.index_var in GV.chipBet4 and GV.splitOverride2:
                                GV.betChipOverride = True
                        '''

                        if CursorPos_CirclePos <= GV.chipRadius**2 and ((GV.chipData[self.index_var[0]])[self.index_var[1]])["override"] is False:
                            GV.mouseStartPos = pygame.mouse.get_pos()
                            GV.mousePosChange = True
                            GV.chipCurrentPos[0] = (((GV.chipData[self.index_var[0]])[self.index_var[1]])["position"])[0]
                            GV.chipCurrentPos[1] = (((GV.chipData[self.index_var[0]])[self.index_var[1]])["position"])[1]

                            GV.chipDisplayPriority.remove(self.index_var)
                            GV.chipDisplayPriority.append(self.index_var)
                            break
                    if GV.mousePosChange == True:
                        break
                    CursorPos_CirclePosx = cursorPosx - 305
                    CursorPos_CirclePosy = cursorPosy - 105

                    CursorPos_CirclePos = CursorPos_CirclePosx**2 + CursorPos_CirclePosy**2

                    if CursorPos_CirclePos <= GV.chipRadius**2 and GV.chipExchangeValue1 == GV.chipExchangeValue2:
                        
                        for chips in GV.chipExchange:
                            CHIPS[chips[0]] -= 1
                        GV.chipExchange.clear()

                        for index, i in enumerate(GV.chipSmallExchangeListtemp):
                            CHIPS[index] += i

                        for index, value in enumerate(GV.chipData):
                            GV.chipData[index].clear()

                        for index, i in enumerate(CHIPS):
                            if i != 0:
                                GV.offset = 5
                                GV.offsetreal = 0
                                GV.sideOffset = 0
                                for _ in range(0, i):
                                    GV.sideOffset = int(str(GV.offset/350)[0]) * 5
                                    GV.offset = GV.offset - int(str(GV.offset/350)[0]) * 350
                                    GV.chipData[index].append({"value": GV.chipValues[index],
                                                                    "colour": GV.chipValueColours[index],
                                                                    "position": [((GV.chipStartPositions)[GV.chipValues[index]])[0] - GV.sideOffset, ((GV.chipStartPositions[GV.chipValues[index]])[1] - GV.offset)],
                                                                    "override": False
                                                                })
                                    GV.offset += 10
                                    GV.offsetreal += 10 

                        GV.chipExchangeValue1 = 0
                        
                        GV.chipSmallExchangeListtemp = list(GV.chipSmallExchangeList)
                        GV.chipExchangeStr1 = (f"{GV.chipExchangeValue1:,}")

                        '''
                        if GV.bettingGame:
                            chipBet1_temp = []
                            chipBet2_temp = []
                            chipBet3_temp = []
                            chipBet4_temp = []

                            for index, value in enumerate(GV.chipBet1):
                                GV.chipPositions[value[0]].append(GV.gameChipPos1[index])
                                chipBet1_temp.append((value[0], len(GV.chipPositions[value[0]]) - 1))
                            for index, value in enumerate(GV.chipBet2):
                                GV.chipPositions[value[0]].append(GV.gameChipPos2[index])
                                chipBet2_temp.append((value[0], len(GV.chipPositions[value[0]]) - 1))
                            for index, value in enumerate(GV.chipBet3):
                                GV.chipPositions[value[0]].append(GV.gameChipPos3[index])
                                chipBet3_temp.append((value[0], len(GV.chipPositions[value[0]]) - 1))
                            for index, value in enumerate(GV.chipBet4):
                                GV.chipPositions[value[0]].append(GV.gameChipPos4[index])
                                chipBet4_temp.append((value[0], len(GV.chipPositions[value[0]]) - 1))

                            GV.chipBet1[:] = chipBet1_temp
                            GV.chipBet2[:] = chipBet2_temp
                            GV.chipBet3[:] = chipBet3_temp
                            GV.chipBet4[:] = chipBet4_temp
                        else:
                            for index, _ in enumerate(GV.chipBet):
                                GV.chipBet[index].clear()
                        '''

                        GV.chipDisplayPriority.clear()

                        for indexa, lista in enumerate(GV.chipData):
                                    for indexb, value in enumerate(lista):
                                        GV.chipDisplayPriority.append((indexa, indexb))

                        save_game()

            if event.type == pygame.MOUSEBUTTONUP and GV.mousePosChange == True:
                GV.mousePosChange = False
                GV.chipCurrentPos[0] = (((GV.chipData[self.index_var[0]])[self.index_var[1]])["position"])[0]
                GV.chipCurrentPos[1] = (((GV.chipData[self.index_var[0]])[self.index_var[1]])["position"])[1]

            for indexexchange, self.smallExchangeChipPos in enumerate(reversed(GV.exchangeChipPos)):

                cursorPosx, cursorPosy = pygame.mouse.get_pos()

                CursorPos_CirclePosx = cursorPosx - self.smallExchangeChipPos[0]
                CursorPos_CirclePosy = cursorPosy - self.smallExchangeChipPos[1]

                CursorPos_CirclePos = CursorPos_CirclePosx**2 + CursorPos_CirclePosy**2
                if CursorPos_CirclePos <= GV.smallChipRadius**2:
                    GV.chipExchangeHighlight = self.smallExchangeChipPos 
                    GV.chipExchangehighlightOn = True
                    GV.exchangeChipSelection = indexexchange
                    break
                else:
                    GV.chipExchangeHighlight = None
                    GV.chipExchangehighlightOn = False
        if GV.mousePosChange == True:
            (((GV.chipData[self.index_var[0]])[self.index_var[1]])["position"])[0] = pygame.mouse.get_pos()[0] - GV.mouseStartPos[0] + GV.chipCurrentPos[0]
            (((GV.chipData[self.index_var[0]])[self.index_var[1]])["position"])[1] = pygame.mouse.get_pos()[1] - GV.mouseStartPos[1] + GV.chipCurrentPos[1]

    def ride_the_duck_function(self):
        pass

GF = game_functions()


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

    def on_render(self):
        GV.display.fill(GV.table_colour)
        GO.on_init()
        GO.game_space()
        GO.chip_objects()
    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        if self.on_init() == False:
            GV._running = False 
        while(GV._running):
            self.FPS.tick(self.fps)
            GF.player_function()
            self.on_render()

            pygame.display.flip()
        self.on_cleanup()

def main():
    Game = pygame_function()
    Game.on_execute()

if __name__ == "__main__":
    main()
