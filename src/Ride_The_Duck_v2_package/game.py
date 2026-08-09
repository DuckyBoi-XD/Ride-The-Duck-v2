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