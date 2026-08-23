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

CHIPS = [0, 0, 1, 0, 0, 0, 0, 0, 0, 0]

def cosd(x):
    return math.cos(math.radians(x))
def sind(x):
    return math.sin(math.radians(x))

def RICD(midx, midy):# random int card display
    return random.randint(midx-10, midx+10), random.randint(midy-10, midy+10)

class game_variable: # Game variables
    def __init__(self):
        pygame.init()
        self.displayWidth, self.displayHeight = 1200, 700
        self.display = pygame.display.set_mode((self.displayWidth, self.displayHeight), pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.table_colour = (20, 86, 62)
        self.table_colour_accent = (37, 64, 64)
        self.dark_table_colour_accent = (15, 35, 35)
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
        self.highlight_yellow = (255, 230, 100)
        self.bright_blue = (14, 142, 255)
        self.bright_orange = (255, 127, 14)
        self.semi_black_colour = (60, 60, 60)
        self.semi_red_colour = (215, 49, 64)
        self.semi_bright_green = (30, 180, 30)

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
        self.betFunctionSuitFont = pygame.font.Font(asset_path("fonts/tableFont.ttf"), 90)
        self.betFunctionSuitFont2 = pygame.font.Font(asset_path("fonts/tableFont.ttf"), 80)

        self.tableTextFontFull = pygame.font.Font(asset_path("fonts/tableFont.ttf"), 40)
        self.tableTextFontSemi = pygame.font.Font(asset_path("fonts/tableFont.ttf"), 25)

        self.endgamefont = pygame.font.Font(asset_path("fonts/endgameFont.ttf"), 20)
        self.endgamefontSemi = pygame.font.Font(asset_path("fonts/endgameFont.ttf"), 17)
        self.endgamefontQuat = pygame.font.Font(asset_path("fonts/endgameFont.ttf"), 15)

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

        self.round = 0
        self.chipBet = []
        self.hoverButtonSquare = [False, False, False, False]
        self.hoverButtonCashOut = False

        self.gameButtonResult = [False, False, False, False]
        self.shuffle_count = 0

        self.gameHand = []
        self.gameCardPositon = []

        self.game = False
        self.gamefail = False
        self.gamepayout = False 
        self.gamepushback = False

        self.cardlengths = [0, 0, 0, 0]
        self.gamemultiplier = 0
        self.chipBetValues = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.chipBetPhyiscalValue = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.cardHandValue = []

        self.roundState = [0, 0, 0, 0]
        self.gameend = False
        self.gameendHover = [20, 20, 20]
        self.gameRestart = False

        self.cardSFX = pygame.mixer.Sound(asset_path("SFX/cardSFX.mp3"))
        self.chipdownSFX = pygame.mixer.Sound(asset_path("SFX/chipdownSFX.mp3"))
        self.chipupSFX = pygame.mixer.Sound(asset_path("SFX/chipupSFX.mp3"))
        self.clickupSFX = pygame.mixer.Sound(asset_path("SFX/clickupSFX.mp3"))
        self.clickdownSFX = pygame.mixer.Sound(asset_path("SFX/clickdownSFX.mp3"))
        self.chipsSFX = pygame.mixer.Sound(asset_path("SFX/chipsSFX.mp3"))
        self.loseSFX = pygame.mixer.Sound(asset_path("SFX/loseSFX.mp3"))
        self.winSFX = pygame.mixer.Sound(asset_path("SFX/winSFX.mp3"))

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

        self.cardDeck = self.tempcardDeck
        random.shuffle(self.cardDeck)
        random.shuffle(self.cardDeck)
        print(self.cardDeck)

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
                                                 "override": False,
                                                 "outline": False,
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
                if value in GV.chipExchange or value in GV.chipBet:
                    chipOutlineColour = GV.yellow_green
                    chipOutlineWidth = 2
                elif GV.chipValueColours[value[0]] == GV.yellow_colour:
                    chipOutlineColour = GV.orange_colour
                    chipOutlineWidth = 2
                else:
                    chipOutlineColour = GV.yellow_colour
                    chipOutlineWidth = 2

            elif value in GV.chipExchange or value in GV.chipBet:
                if ((GV.chipData[value[0]])[value[1]])["outline"] and not ((GV.chipData[value[0]])[value[1]])["override"]:
                    chipOutlineColour = GV.yellow_green
                    chipOutlineWidth = 1
                else:
                    chipOutlineColour = GV.bright_green
                    chipOutlineWidth = 2

            elif ((GV.chipData[value[0]])[value[1]])["outline"] and not ((GV.chipData[value[0]])[value[1]])["override"]:
                chipOutlineColour = GV.highlight_yellow
                chipOutlineWidth = 1
                
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

        for index, value in enumerate(GV.roundState):
            if index == 0:

                if value == 1:
                    textcolour = GV.bright_green
                elif value == 2:
                    textcolour = GV.orange_colour
                elif value == 3:
                    textcolour = GV.bright_red
                else:
                    if GV.round == 0:
                        textcolour = GV.highlight_yellow
                    else:
                        textcolour = GV.white_colour

                tabelText = GV.tableTextFontFull.render(("2x"), True, textcolour)
                tableTextRotated = pygame.transform.rotate(tabelText, 335)
                tableTextRect = tabelText.get_rect(center=(90, 134))
                GV.display.blit(tableTextRotated, tableTextRect)

            elif index == 1:

                if value == 1:
                    textcolour = GV.bright_green
                elif value == 2:
                    textcolour = GV.orange_colour
                elif value == 3:
                    textcolour = GV.bright_red
                else:
                    if GV.round == 1:
                        textcolour = GV.highlight_yellow
                    else:
                        textcolour = GV.white_colour

                tabelText = GV.tableTextFontFull.render(("3x"), True, textcolour)
                tableTextRotated = pygame.transform.rotate(tabelText, 344)
                tableTextRect = tabelText.get_rect(center=(260, 198))
                GV.display.blit(tableTextRotated, tableTextRect)

            elif index == 2:

                if value == 1:
                    textcolour = GV.bright_green
                elif value == 2:
                    textcolour = GV.orange_colour
                elif value == 3:
                    textcolour = GV.bright_red
                else:
                    if GV.round == 2:
                        textcolour = GV.highlight_yellow
                    else:
                        textcolour = GV.white_colour

                tabelText = GV.tableTextFontFull.render(("4x"), True, textcolour)
                tableTextRotated = pygame.transform.rotate(tabelText, 15)
                tableTextRect = tabelText.get_rect(center=(925, 198))
                GV.display.blit(tableTextRotated, tableTextRect)

            elif index == 3:

                if value == 1:
                    textcolour = GV.bright_green
                elif value == 2:
                    textcolour = GV.orange_colour
                elif value == 3:
                    textcolour = GV.bright_red
                else:
                    if GV.round == 3:
                        textcolour = GV.highlight_yellow
                    else:
                        textcolour = GV.white_colour

                tabelText = GV.tableTextFontFull.render(("20x"), True, textcolour)
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

        if GV.round == 0:
            if GV.gamepushback or GV.gamepayout or GV.gamefail:
                    box_colour1 = GV.black_colour
                    box_colour2 = GV.red_colour
            else:
                if GV.hoverButtonSquare[0] or GV.hoverButtonSquare[1]:
                    box_colour1 = GV.semi_black_colour
                else:
                    box_colour1 = GV.black_colour

                if GV.hoverButtonSquare[2] or GV.hoverButtonSquare[3]:
                    box_colour2 = GV.semi_red_colour
                else:
                    box_colour2 = GV.red_colour

            pygame.draw.rect(GV.display, box_colour1, (303, 350, 75, 150))
            pygame.draw.rect(GV.display, box_colour2, (822, 350, 75, 150))

            if GV.gamepushback or GV.gamepayout or GV.gamefail:
                pass
            else:
                buttontext1 = GV.betFunctionColourFont.render(f"BLACK", True, GV.white_colour)
                buttontext2 = GV.betFunctionColourFont.render(f"RED", True, GV.white_colour)
                buttontext1_rotated = pygame.transform.rotate(buttontext1, 90)
                buttontext2_rotated = pygame.transform.rotate(buttontext2, 270)
                buttontext1rect1 = buttontext1_rotated.get_rect(center=(340, 425))
                buttontext2rect2 = buttontext2_rotated.get_rect(center=(860, 425))
                GV.display.blit(buttontext1_rotated, buttontext1rect1)
                GV.display.blit(buttontext2_rotated, buttontext2rect2)
        elif GV.round == 1:
            if GV.hoverButtonSquare[0] or GV.hoverButtonSquare[1]:
                box_colour1 = GV.semi_black_colour
            else:
                box_colour1 = GV.black_colour

            if GV.hoverButtonSquare[2] or GV.hoverButtonSquare[3]:
                box_colour2 = GV.semi_red_colour
            else:
                box_colour2 = GV.red_colour

            pygame.draw.rect(GV.display, box_colour1, (303, 350, 75, 150))
            pygame.draw.rect(GV.display, box_colour2, (822, 350, 75, 150))
            buttontext1 = GV.betFunctionColourFont.render(f"ABOVE", True, GV.white_colour)
            buttontext2 = GV.betFunctionColourFont.render(f"BELOW", True, GV.white_colour)
            buttontext1_rotated = pygame.transform.rotate(buttontext1, 90)
            buttontext2_rotated = pygame.transform.rotate(buttontext2, 270)
            buttontext1rect1 = buttontext1_rotated.get_rect(center=(340, 425))
            buttontext2rect2 = buttontext2_rotated.get_rect(center=(860, 425))
            GV.display.blit(buttontext1_rotated, buttontext1rect1)
            GV.display.blit(buttontext2_rotated, buttontext2rect2)
        elif GV.round == 2:
            if GV.hoverButtonSquare[0] or GV.hoverButtonSquare[1]:
                box_colour1 = GV.semi_black_colour
            else:
                box_colour1 = GV.black_colour

            if GV.hoverButtonSquare[2] or GV.hoverButtonSquare[3]:
                box_colour2 = GV.semi_red_colour
            else:
                box_colour2 = GV.red_colour

            pygame.draw.rect(GV.display, box_colour1, (303, 350, 75, 150))
            pygame.draw.rect(GV.display, box_colour2, (822, 350, 75, 150))
            buttontext1 = GV.betFunctionInOutFont.render(f"INSIDE", True, GV.white_colour)
            buttontext2 = GV.betFunctionInOutFont.render(f"OUTSIDE", True, GV.white_colour)
            buttontext1_rotated = pygame.transform.rotate(buttontext1, 90)
            buttontext2_rotated = pygame.transform.rotate(buttontext2, 270)
            buttontext1rect1 = buttontext1_rotated.get_rect(center=(340, 425))
            buttontext2rect2 = buttontext2_rotated.get_rect(center=(860, 425))
            GV.display.blit(buttontext1_rotated, buttontext1rect1)
            GV.display.blit(buttontext2_rotated, buttontext2rect2)
        elif GV.round == 3:
            if GV.hoverButtonSquare[0]:
                box_colour1 = GV.dark_table_colour_accent
            else:
                box_colour1 = GV.table_colour_accent

            if GV.hoverButtonSquare[1]:
                box_colour2 = GV.dark_table_colour_accent
            else:
                box_colour2 = GV.table_colour_accent

            if GV.hoverButtonSquare[2]:
                box_colour3 = GV.dark_table_colour_accent
            else:
                box_colour3 = GV.table_colour_accent

            if GV.hoverButtonSquare[3]:
                box_colour4 = GV.dark_table_colour_accent
            else:
                box_colour4 = GV.table_colour_accent

            pygame.draw.rect(GV.display, box_colour1, (303, 350, 75, 75))
            pygame.draw.rect(GV.display, box_colour2, (303, 425, 75, 75))

            pygame.draw.line(GV.display, GV.white_colour, (303, 425), (375, 425), 3)

            pygame.draw.rect(GV.display, box_colour3, (822, 350, 75, 75))
            pygame.draw.rect(GV.display, box_colour4, (822, 425, 75, 75))

            pygame.draw.line(GV.display, GV.white_colour, (822, 425), (894, 425), 3)

            text = GV.betFunctionSuitFont.render("♠", True, GV.black_colour)
            textrect = text.get_rect(center=(340, 383))
            GV.display.blit(text, textrect)

            text = GV.betFunctionSuitFont2.render("♥", True, GV.red_colour)
            textrect = text.get_rect(center=(339, 458))
            GV.display.blit(text, textrect)

            text = GV.betFunctionSuitFont.render("♦", True, GV.red_colour)
            textrect = text.get_rect(center=(859, 383))
            GV.display.blit(text, textrect)

            text = GV.betFunctionSuitFont.render("♣", True, GV.black_colour)
            textrect = text.get_rect(center=(859, 458))
            GV.display.blit(text, textrect)

        if GV.hoverButtonCashOut and GV.chipBet and GV.round != 0:
            box_colour = GV.bright_green
        elif GV.chipBet:
            box_colour = GV.semi_bright_green
        else:
            box_colour = GV.semi_red_colour
        pygame.draw.rect(GV.display, box_colour, (500, 497, 200, 50))
        if GV.round != 0:
            buttontext1 = GV.betFunctionInOutFont.render(f"CASH OUT", True, GV.white_colour)
            buttontextrect1 = buttontext1.get_rect(center=(600, 522))
            GV.display.blit(buttontext1, buttontextrect1)
            
        pygame.draw.rect(GV.display, (255, 255, 255), (303, 350, 75, 150), 3)
        pygame.draw.rect(GV.display, (255, 255, 255), (822, 350, 75, 150), 3)
        pygame.draw.rect(GV.display, GV.highlight_yellow, (500, 497, 200, 50), 3)
        pygame.draw.rect(GV.display, GV.highlight_yellow, (375, 350, 450, 150), 3)
    def card_object(self):
        for index, card in enumerate(GV.gameHand):

            suit_var = int(card[0])
            if len(card) == 3:
                value_var = int(card[1:3])
            else:
                value_var = int(card[1])

            value_var -= 2

            if GV.roundState[index] == 1:
                cardoutline = GV.bright_green
            elif GV.roundState[index] == 3:
                cardoutline = GV.bright_red

            cardpos = GV.gameCardPositon[index]
            card = pygame.transform.smoothscale(pygame.image.load((GV.CardFiles[suit_var][value_var])), (105, 140)).convert_alpha()
            rect = card.get_rect(center=(cardpos))
            GV.display.blit(card, rect)
            pygame.draw.rect(GV.display, cardoutline, (rect[0]-1, rect[1]-1, 107, 142), 2, 5)

    def gameEnd(self):
            if GV.gameend:
                rect_surface = pygame.Surface((600, 400), pygame.SRCALPHA)
                rect_surface.set_alpha(200)
        
                pygame.draw.rect(rect_surface, (0, 0, 0), (0, 0, 300, 400))
                pygame.draw.rect(rect_surface, (255, 255, 255), (0, 0, 300, 400), width=3)
        
                GV.display.blit(rect_surface, (450, 150))
        
                endgameText = GV.endgamefont.render(f"ROUNDS PLAYED:", True, GV.white_colour)
                endgameRect = endgameText.get_rect(center=(600, 170))
                GV.display.blit(endgameText, endgameRect)
        
                endgameValue = GV.endgamefont.render(f"{STATS["rounds played"]}", True, GV.white_colour)
                endgameRect = endgameValue.get_rect(center=(600, 190))
                GV.display.blit(endgameValue, endgameRect)
        
                
                endgameText = GV.endgamefont.render(f"ROUNDS WON:", True, GV.white_colour)
                endgameRect = endgameText.get_rect(center=(600, 220))
                GV.display.blit(endgameText, endgameRect)
                endgameValue = GV.endgamefont.render(f"{STATS["wins"]}", True, GV.white_colour)
                endgameRect = endgameValue.get_rect(center=(600, 240))
                GV.display.blit(endgameValue, endgameRect)

                endgameText = GV.endgamefontSemi.render(f"2x: {STATS["2x wins"]}", True, GV.white_colour)
                endgameRect = endgameText.get_rect(center=(600, 265))
                GV.display.blit(endgameText, endgameRect)

                endgameText = GV.endgamefontSemi.render(f"3x: {STATS["3x wins"]}", True, GV.white_colour)
                endgameRect = endgameText.get_rect(center=(600, 285))
                GV.display.blit(endgameText, endgameRect)

                endgameText = GV.endgamefontSemi.render(f"4x: {STATS["4x wins"]}", True, GV.white_colour)
                endgameRect = endgameText.get_rect(center=(600, 305))
                GV.display.blit(endgameText, endgameRect)

                endgameText = GV.endgamefontSemi.render(f"20x: {STATS["20x wins"]}", True, GV.white_colour)
                endgameRect = endgameText.get_rect(center=(600, 325))
                GV.display.blit(endgameText, endgameRect)                
        
                endgameText = GV.endgamefont.render(f"ROUNDS LOST:", True, GV.white_colour)
                endgameRect = endgameText.get_rect(center=(600, 355))
                GV.display.blit(endgameText, endgameRect)
                endgameValue = GV.endgamefont.render(f"{STATS["loses"]}", True, GV.white_colour)
                endgameRect = endgameValue.get_rect(center=(600, 375))
                GV.display.blit(endgameValue, endgameRect)
        
                endgameText = GV.endgamefont.render(f"ROUNDS PUSHED BACK:", True, GV.white_colour)
                endgameRect = endgameText.get_rect(center=(600, 405))
                GV.display.blit(endgameText, endgameRect)
                endgameValue = GV.endgamefont.render(f"{STATS["push back"]}", True, GV.white_colour)
                endgameRect = endgameValue.get_rect(center=(600, 425))
                GV.display.blit(endgameValue, endgameRect)
        
                endgameText = GV.endgamefont.render(f"MONEY EARNT:", True, GV.white_colour)
                endgameRect = endgameText.get_rect(center=(600, 455))
                GV.display.blit(endgameText, endgameRect)
                endgameValue = GV.endgamefont.render(f"{STATS["money earnt"]}", True, GV.white_colour)
                endgameRect = endgameValue.get_rect(center=(600, 475))
                GV.display.blit(endgameValue, endgameRect)

                pygame.draw.rect(GV.display, GV.gameendHover, (500, 495, 200, 40))
                endgameText = GV.endgamefont.render("RESTART", True, GV.highlight_yellow)
                endgameRect = endgameText.get_rect(center=(600, 515))
                GV.display.blit(endgameText, endgameRect)

                pygame.draw.rect(GV.display, (255, 255, 255), (500, 495, 200, 40), width=1)

GO = game_objects()

class game_functions():
    def player_function(self):

        global CHIPS, STATS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GV._running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if int(list(reversed(GV.chipValues))[GV.exchangeChipSelection]) < GV.chipExchangeValue2 or (int(list(reversed(GV.chipValues))[GV.exchangeChipSelection]) == GV.chipExchangeValue2 and len(GV.chipExchange)!= 1):
                    if int(list(reversed(GV.chipValues))[GV.exchangeChipSelection]) <= GV.chipExchangeValue2-GV.chipExchangeValue1:
                        if event.button == 1:
                            if GV.chipExchangehighlightOn:

                                GV.clickupSFX.play(0)

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

                            GV.clickdownSFX.play(0)

                            GV.chipSmallExchangeListtemp[GV.exchangeChipSelection] -= 1
                            GV.chipExchangeValue1 = 0

                            for indexexclist, value in enumerate(GV.chipSmallExchangeListtemp):
                                if value > 0:
                                    GV.chipExchangeValue1 += value * int(list(reversed(GV.chipValues))[indexexclist])
                            GV.chipExchangeStr1 = (f"{GV.chipExchangeValue1:,}")
                        GV.chipSmallExchangeListtemp.reverse()
                if event.button == 1:

                    cursorPosx, cursorPosy = pygame.mouse.get_pos()

                    if GV.chipBet and not GV.game and GV.round == 0 and any(GV.hoverButtonSquare):
                        GV.game = True
                        for self.index_var in GV.chipBet:
                            ((GV.chipData[self.index_var[0]])[self.index_var[1]])["override"] = True
                        for index, value in enumerate(GV.hoverButtonSquare):
                            if value:
                                if index == 0 or index == 1:
                                    GV.gameButtonResult[0] = True
                                    GV.round = 1

                                    GV.chipBetValues = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                                    for chip in GV.chipBet:
                                        GV.chipBetValues[chip[0]] += 1

                                elif index == 2 or index == 3:
                                    GV.gameButtonResult[2] = True
                                    GV.round = 1

                                    GV.chipBetValues = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                                    for chip in GV.chipBet:
                                        GV.chipBetValues[chip[0]] += 1

                    elif GV.round != 0 and GV.hoverButtonCashOut:
                        GV.gamepayout = True

                    elif GV.round == 1:
                        for index, value in enumerate(GV.hoverButtonSquare):
                            if value:
                                if index == 0 or index == 1:
                                    GV.gameButtonResult[0] = True
                                    GV.round = 2
                                elif index == 2 or index == 3:
                                    GV.gameButtonResult[2] = True
                                    GV.round = 2

                    elif GV.round == 2:
                        for index, value in enumerate(GV.hoverButtonSquare):
                            if value:
                                if index == 0 or index == 1:
                                    GV.gameButtonResult[0] = True
                                    GV.round = 3
                                elif index == 2 or index == 3:
                                    GV.gameButtonResult[2] = True
                                    GV.round = 3

                    elif GV.round == 3:
                        for index, value in enumerate(GV.hoverButtonSquare):
                            if value:
                                if index == 0:
                                    GV.gameButtonResult[0] = True
                                    GV.round = 4
                                elif index == 1:
                                    GV.gameButtonResult[1] = True
                                    GV.round = 4
                                elif index == 2:
                                    GV.gameButtonResult[2] = True
                                    GV.round = 4
                                elif index == 3:
                                    GV.gameButtonResult[3] = True
                                    GV.round = 4

                    for self.index_var in reversed(GV.chipDisplayPriority):
                        CursorPos_CirclePosx = cursorPosx - (((GV.chipData[self.index_var[0]])[self.index_var[1]])["position"])[0]
                        CursorPos_CirclePosy = cursorPosy - (((GV.chipData[self.index_var[0]])[self.index_var[1]])["position"])[1]

                        CursorPos_CirclePos = CursorPos_CirclePosx**2 + CursorPos_CirclePosy**2

                        if CursorPos_CirclePos <= GV.chipRadius**2 and ((GV.chipData[self.index_var[0]])[self.index_var[1]])["override"] is False:

                            GV.chipupSFX.play(0)

                            if GV.gamefail or GV.gamepayout or GV.gamepushback:
                                if GV.gamefail:
                                    GV.gamefail = False
                                if GV.gamepayout:
                                    GV.gamepayout = False
                                if GV.gamepushback:
                                    GV.gamepushback = False
                                GV.game = False
                                GV.gameHand.clear()
                                GV.gameCardPositon.clear()
                                GV.roundState = [0, 0, 0, 0]

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

                        GV.chipsSFX.play(0)
                        
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
                                                                    "override": False,
                                                                    "outline": False,
                                                                })
                                    GV.offset += 10
                                    GV.offsetreal += 10 

                        GV.chipExchangeValue1 = 0
                        
                        GV.chipSmallExchangeListtemp = list(GV.chipSmallExchangeList)
                        GV.chipExchangeStr1 = (f"{GV.chipExchangeValue1:,}")

                        GV.chipDisplayPriority.clear()

                        for indexa, lista in enumerate(GV.chipData):
                                    for indexb, value in enumerate(lista):
                                        GV.chipDisplayPriority.append((indexa, indexb))

                        save_game()
                if GV.gameRestart and GV.gameend:

                    CHIPS = [5, 2, 1, 0, 0, 0, 0, 0, 0, 0]
                    STATS = {"rounds played" : 0, "2x wins" : 0, "3x wins" : 0, "4x wins" : 0, "20x wins" : 0, "wins" : 0, "loses" : 0, "push back" : 0, "money earnt" : 0}

                    if GV.gamefail:
                        GV.gamefail = False
                    if GV.gamepayout:
                        GV.gamepayout = False
                    if GV.gamepushback:
                        GV.gamepushback = False
                    GV.game = False
                    GV.gameHand.clear()
                    GV.gameCardPositon.clear()
                    GV.round = 0
                    GV.roundState = [0, 0, 0, 0]

                    GV.gameRestart = False
                    GV.gameend = False

                    for index, _ in enumerate(GV.chipData):
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
                                                                "override": False,
                                                                "outline": False,
                                                            })
                                GV.offset += 10
                                GV.offsetreal += 10
                    GV.chipDisplayPriority.clear()
                    for indexa, lista in enumerate(GV.chipData):
                        for indexb, _ in enumerate(lista):
                            GV.chipDisplayPriority.append((indexa, indexb))

            if event.type == pygame.MOUSEBUTTONUP and GV.mousePosChange == True:

                GV.chipdownSFX.play(0)

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
            if not ((GV.chipData[self.index_var[0]])[self.index_var[1]])["override"]:
                GV.hoverButtonSquare = [False, False, False, False]
                GV.hoverButtonCashOut = False
                (((GV.chipData[self.index_var[0]])[self.index_var[1]])["position"])[0] = pygame.mouse.get_pos()[0] - GV.mouseStartPos[0] + GV.chipCurrentPos[0]
                (((GV.chipData[self.index_var[0]])[self.index_var[1]])["position"])[1] = pygame.mouse.get_pos()[1] - GV.mouseStartPos[1] + GV.chipCurrentPos[1]
        else:
            cursorPosx, cursorPosy = pygame.mouse.get_pos()
            GV.hoverButtonCashOut = False
            GV.hoverButtonSquare = [False, False, False, False]

            if GV.gameend and GV.round == 0:
                cursorPosx, cursorPosy = pygame.mouse.get_pos()
                (500, 495, 200, 40)
                if 500 <= cursorPosx <= 700 and 495 <= cursorPosy <= 535:
                    GV.gameendHover = [80, 80, 80]
                    GV.gameRestart = True
                else:
                    GV.gameendHover = [20, 20, 20]
                    GV.gameRestart = False

            elif 303 <= cursorPosx <= 372 and 350 <= cursorPosy <= 425:
                GV.hoverButtonSquare = [True, False, False, False]
            elif 303 <= cursorPosx <= 372 and 425 <= cursorPosy <= 500:
                GV.hoverButtonSquare = [False, True, False, False]
            elif 822 <= cursorPosx <= 897 and 350 <= cursorPosy <= 425:
                GV.hoverButtonSquare = [False, False, True, False]
            elif 822 <= cursorPosx <= 897 and 425 <= cursorPosy <= 500:
                GV.hoverButtonSquare = [False, False, False, True]
            elif 500 <= cursorPosx <= 700 and 500 <= cursorPosy <= 550:
                GV.hoverButtonCashOut = True
            else:
                for chipindex in reversed(GV.chipDisplayPriority):
                    CursorPos_CirclePosx = cursorPosx - (((GV.chipData[chipindex[0]]))[chipindex[1]]["position"])[0]
                    CursorPos_CirclePosy = cursorPosy - (((GV.chipData[chipindex[0]]))[chipindex[1]]["position"])[1]
                    CursorPos_CirclePos = CursorPos_CirclePosx**2 + CursorPos_CirclePosy**2

                    if CursorPos_CirclePos <= GV.chipRadius**2:
                        if not (((GV.chipData[chipindex[0]]))[chipindex[1]])["outline"]:
                            for indexa, chiplist in enumerate(GV.chipData):
                                for indexb, chip in enumerate(chiplist):
                                    ((GV.chipData[indexa])[indexb])["outline"] = False
                            (((GV.chipData[chipindex[0]]))[chipindex[1]])["outline"] = True
                        break

                    else:
                        if (((GV.chipData[chipindex[0]]))[chipindex[1]])["outline"]:
                            (((GV.chipData[chipindex[0]]))[chipindex[1]])["outline"] = False
                            

    def betting_areas(self):
        for chip_index in reversed(GV.chipDisplayPriority):
            chipPositionx = ((GV.chipData[chip_index[0]])[chip_index[1]])["position"][0]
            chipPositiony = ((GV.chipData[chip_index[0]])[chip_index[1]])["position"][1]

            if 375 <= chipPositionx <= 825 and 350 <= chipPositiony <= 500 and GV.round == 0:
                if chip_index not in GV.chipBet:
                    GV.chipBet.append(chip_index)
            else:
                if chip_index in GV.chipBet and GV.round == 0:
                    GV.chipBet.remove(chip_index)

    def ride_the_duck_function(self):
        global CHIPS, STATS
        if any(GV.gameButtonResult):
            GV.gameHand.append(GV.cardDeck[0])
            GV.cardDeck.append(GV.cardDeck[0])

            GV.cardSFX.play(0)

            if len(GV.gameHand[-1]) == 3:
                GV.cardlengths[(GV.round) - 1] = slice(1, 3)
            else:
                GV.cardlengths[(GV.round) - 1] = 1

            GV.gamefail = False

            if GV.round == 1: # BLACK AND RED
                GV.gameCardPositon.append(RICD(350, 260))

                if int(GV.gameHand[0][0]) in (0,3) and GV.gameButtonResult[0]:
                    GV.gamemultiplier = 2
                    GV.roundState[0] = 1

                elif int(GV.gameHand[0][0]) in (1,2) and GV.gameButtonResult[2]:
                    GV.gamemultiplier = 2
                    GV.roundState[0] = 1

                else:
                    GV.gamefail = True
                    GV.roundState[0] = 3

            elif GV.round == 2: # ABOVE AND BELOW
                GV.gameCardPositon.append(RICD(517, 260))
                if int(GV.gameHand[1][GV.cardlengths[1]]) > int(GV.gameHand[0][GV.cardlengths[0]]) and GV.gameButtonResult[0]:
                    GV.gamemultiplier = 3
                    GV.roundState[1] = 1

                elif int(GV.gameHand[1][GV.cardlengths[1]]) < int(GV.gameHand[0][GV.cardlengths[0]]) and GV.gameButtonResult[2]:
                    GV.gamemultiplier = 3
                    GV.roundState[1] = 1

                elif int(GV.gameHand[1][GV.cardlengths[1]]) == int(GV.gameHand[0][GV.cardlengths[0]]) and (GV.gameButtonResult[0] or GV.gameButtonResult[2]):
                    GV.gamepushback = True
                    GV.roundState[1] = 2

                else:
                    GV.gamefail = True
                    GV.roundState[1] = 3

            elif GV.round == 3: # INSIDE AND OUTSIDE
                GV.gameCardPositon.append(RICD(683, 260))
                GV.cardHandValue.append(int(GV.gameHand[0][GV.cardlengths[0]]))
                GV.cardHandValue.append(int(GV.gameHand[1][GV.cardlengths[1]]))

                if max(GV.cardHandValue) > int(GV.gameHand[2][GV.cardlengths[2]]) > min(GV.cardHandValue) and GV.gameButtonResult[0]:
                    GV.gamemultiplier = 4
                    GV.roundState[2] = 1

                elif (int(GV.gameHand[2][GV.cardlengths[2]]) > max(GV.cardHandValue) or min(GV.cardHandValue) > int(GV.gameHand[2][GV.cardlengths[2]])) and GV.gameButtonResult[2]:
                    GV.gamemultiplier = 4
                    GV.roundState[2] = 1

                elif int(GV.gameHand[2][GV.cardlengths[2]]) in GV.cardHandValue:
                    GV.gamepushback = True
                    GV.roundState[2] = 2

                else:
                    GV.gamefail = True
                    GV.roundState[2] = 3

            elif GV.round == 4: # SPADE HEART DIAMIOND CLUB
                GV.gameCardPositon.append(RICD(850, 260))
                if int(GV.gameHand[-1][0]) == 0 and GV.gameButtonResult[0]:
                    GV.gamemultiplier = 20
                    GV.gamepayout = True
                    GV.roundState[3] = 1

                elif int(GV.gameHand[-1][0]) == 1 and GV.gameButtonResult[1]:
                    GV.gamemultiplier = 20
                    GV.gamepayout = True
                    GV.roundState[3] = 1

                elif int(GV.gameHand[-1][0]) == 2 and GV.gameButtonResult[2]:
                    GV.gamemultiplier = 20
                    GV.gamepayout = True
                    GV.roundState[3] = 1

                elif int(GV.gameHand[-1][0]) == 3 and GV.gameButtonResult[3]:
                    GV.gamemultiplier = 20
                    GV.gamepayout = True
                    GV.roundState[3] = 1

                else:
                    GV.gamefail = True
                    GV.roundState[3] = 3
            
            if GV.gamefail:

                STATS["loses"] += 1
                GV.loseSFX.play(0)
                for chip in GV.chipBet:
                    CHIPS[chip[0]] -= 1

                    for index, _ in enumerate(GV.chipData):
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
                                                                "override": False,
                                                                "outline": False,
                                                            })
                                GV.offset += 10
                                GV.offsetreal += 10

                    GV.chipDisplayPriority.clear()
                    for indexa, lista in enumerate(GV.chipData):
                        for indexb, _ in enumerate(lista):
                            GV.chipDisplayPriority.append((indexa, indexb))

                GV.round = 0
                GV.chipBet.clear()
                GV.gamemultiplier = 0

            GV.gameButtonResult = [False, False, False, False]
            GV.cardDeck.remove(GV.cardDeck[0])
            GV.cardHandValue.clear()

        elif (GV.gamepayout or GV.gamepushback) and GV.round != 0:
            if GV.gamepushback:
                STATS["push back"] += 1

            if GV.gamepayout:
                STATS["wins"] += 1
                STATS[f"{str(GV.gamemultiplier)}x wins"] += 1

                GV.winSFX.play(0)
                GV.chipsSFX.play(0)

                GV.chipBetPhyiscalValue = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

                for chip in GV.chipBet:
                    CHIPS[chip[0]] -= 1
                for index, value in enumerate(GV.chipBetValues): # updates chip payout with winning multiplier
                    if value != 0:
                        GV.chipBetValues[index] = value * GV.gamemultiplier
                        GV.chipBetPhyiscalValue[index] = (int(GV.chipValues[index])) * value * GV.gamemultiplier

                chipbettedvalue = 0
                for chip in GV.chipBet:
                    chipbettedvalue += int(GV.chipValues[chip[0]])

                for index, chip in enumerate(GV.chipBetValues):
                    STATS["money earnt"] += (int(GV.chipValues[index]) * chip)
                STATS["money earnt"] -= chipbettedvalue


                for index, value in enumerate(GV.chipBetPhyiscalValue): # tries to simplify the payout

                    bit20 = False
                    bit4 = False

                    if value != 0 and index != 7 and (GV.gamemultiplier == 20 or value >= 2):
                        if value % int(GV.chipValues[index+3]) == 0:
                            bit20 = True
                            GV.chipBetValues[index] = 0
                            GV.chipBetValues[index+3] = int(value/int(GV.chipValues[index+3]))
                        else:
                            bit20 = False

                    if not bit20:
                        if value != 0 and index != 8 and (GV.gamemultiplier >= 4 or value >= 2):
                            if value % int(GV.chipValues[index+2]) == 0:
                                bit20 = True
                                GV.chipBetValues[index] = 0
                                GV.chipBetValues[index+2] = int(value/int(GV.chipValues[index+2]))
                            else:
                                bit4 = False
                    if not bit4 and not bit20:
                        if value != 0 and index != 9 and (GV.gamemultiplier >= 3 or value >= 2):
                            if value % int(GV.chipValues[index+1]) == 0:
                                GV.chipBetValues[index] = 0
                                GV.chipBetValues[index+1] = int(value/int(GV.chipValues[index+1]))

            for parent_index, chips in enumerate(GV.chipBetValues):
                if GV.gamepayout:
                    CHIPS[parent_index] += chips

                for index, _ in enumerate(GV.chipData):
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
                                                            "override": False,
                                                            "outline": False,
                                                        })
                            GV.offset += 10
                            GV.offsetreal += 10
                GV.chipDisplayPriority.clear()
                for indexa, lista in enumerate(GV.chipData):
                    for indexb, _ in enumerate(lista):
                        GV.chipDisplayPriority.append((indexa, indexb))

            GV.chipBet.clear()
            GV.gamemultiplier = 0
            GV.round = 0
            GV.cardHandValue.clear()

            
        

            

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
        if GV.gameHand:
            GO.card_object()
        GO.gameEnd()
    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        if self.on_init() == False:
            GV._running = False 
        while(GV._running):
            self.FPS.tick(self.fps)
            GF.player_function()
            GF.betting_areas()
            if GV.game:
                GF.ride_the_duck_function()
            if sum(CHIPS) == 0 and GV.round == 0:
                GV.gameend = True
            else:
                GV.gameend = False
            self.on_render()
            pygame.display.flip()
        self.on_cleanup()

def main():
    Game = pygame_function()
    Game.on_execute()

if __name__ == "__main__":
    main()
