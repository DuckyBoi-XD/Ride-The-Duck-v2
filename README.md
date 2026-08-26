# Ride The Duck v2

The second version of my recreation of the drinking game and Schedule 1 gambling game, 'Ride the Bus', recreated in Python using pygame for the user interface

## Features

- Save File System: Uses JSON to automatically save game data to the disk, saving stats and the amount of chips there are
- Pygame: Uses Pygame to track user inputs and display information about the game
- Pypi: Published to pypi for easy installation and access
- Chip Based Betting System: Instead of using plain money or 'points', physical chips are used to indicate the value of a bet.
- Chip Exchange: Includes the ability to exchange chips with other chips of equal value
- Sound/SFX: Includes sound effects in game for different functions
- Chip Shortcuts: Features a hold down key to quickly move the chip to the exchange or betting area
- Chip Redos: Features a function/key that will redo any changes in the position of the chip (history resets upon exchanging or winning/lose a game)
- Statistics: Statistics relevant to the game is tracked and displayed when booting up the game and running out of chips (resetting game)
- Table Writing: Feature mathematically symmetrical table text and lines

## Videos

## Images

## How To Install

Requirements:

- MacOS or Linux device (MacOS is confirmed working with terminal)
- Python 3.9 or later (the latest to be safe)
- Pip 22 or later (the latest to be safe)
- Pygame 2.6.0 or later (should be installed when installing the package from Pypi)

1. You'll need to have Python and pip installed.
    - You can follow [this](https://www.python.org/downloads/) to install Python
    - You can follow [this](https://pypi.org/project/pip/) to install pip

2. In Terminal or Command Prompt, enter the command:

    ```sh
    pip install ride-the-duck-v2
    ```

    This will install the game. This is from the Pypi package [blackduck-v2](https://pypi.org/project/blackduck-v2/)

3. Once installed, you can use the commands:

    - `rtd2`
    - `ridetheduck-v2`
    - `play-rtd2`
    - `play-ridetheduck-v2`
    (Capitalization doesn't matter)

4. Enjoy and good luck gambling

## How To Play

After running the entry command (seen above), you'll be presented with the title screen. This simply shows the stats of the current run and the title of the game. To pass this you can just press start and this will get into the main game.

When in the main part of the game, you can do 3 things: exchange your chips for different denominations (shortcut - 'x' + left click the chip), use your chips to bet (shortcut - 'z' + left click the chip), move the chip (for fun).

When exchanging, this is done by moving the chip into the top right section of the table or holding down 'x' and selecting the chip (chips are indicated that they are in the space if they have a green outline). Once moving all desired chips to the exchange area, a space on the top left will appear, showing all the chip denominations, the selected value, the value of all the chips you placed and a circular button. You'll need to press on the chips you want to exchange your chips for which has to be equal to each other. Once equal, the circular button will turn green and pressing it will exchange your chips and save the game's data.

When betting, this is done by moving all the chips you want to bet into the center box between the 2 buttons labeled and coloured black and red. Once all desired chips are in the the betting space (chips are indicated that they are in the space if they have a green outline), pressing either the 'black' or 'red' will start the game, the button you press indicating/is your guess on whether the next card drawn would 'black' or 'red'. There are 4 stages of the game, indicated by the text on the table labeled as: 2x, 3x, 4x, 20x which also represents the multiplier you get for beating the stage. Once you beat at least once stage, you are given the ability to 'cash out' and your original bet will be multiplied by the stage's multiplier that you're on.

The following stages are ordered by the following: 2x - Black or White, 3x - Higher or Lower the first card, 4x - Inside or Outside the cards before, 20x - Spade, Heart, Diamond or Clubs, the suit of the next card.

The rules of the game can be seen [here](https://www.wikihow.com/Play-Ride-the-Bus) (note that it's only the first part and that the multiplier and outcome are different)

There are 7 stats: Rounds Played, Rounds Won, Specific Multiplier Wins, Rounds Lost, Rounds Pushed Back, Money Earnt, Peak Money. 