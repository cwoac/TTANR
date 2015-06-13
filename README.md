# TTANR
ANR deck image creator for TableTop Simulator, working from either octgn format files (`.o8n`) or netrunnerdb decks (public decks only).

## Usage

The easiest way is via netrunnerdb. Both players create *public* decks then give the id to the other. Each then uses `-i` to automatically install the files into their TTS saved directory.
Alternatively, don't use `-i` and put the created files up on a webserver using the `-u` parameter
Example:
````
python ttanr.py -n 12345 -i
python ttanr.py -o my_awesome_deck.o8n -u http://myserver/decks/
python ttanr.py -n 5438 -u http://myserver/decks/
````

## Notes

This program comes supplied with *no* assets. Card fronts are pulled from netrunnerdb and cached in a 'cards' directory.

This code is to be considered alpha - there is is little/no error handling at the moment.

It will create a .json file for TableTop Simulator. If not installing locally then you need to provide an url for where the images will be stored. This *can* be a local path (e.g. `file:///c:/mydecks/`), but in that case you need to get the file to the other players and they must put it in the same location. 

It will use a fixed block of red or blue for the the backs of cards. If you want to use other images, create `cards/corp-back.png` and `cards/runner-back.png`, they *must* be 300x419 in size.

It will only use the original card art - if you want to use alt art, figure out the netrunner card id for the card and replace cards/id.png with your file (again, *must* be 300x419)

## Requirements
- python2.7
- untangle
- PIL



## TODO
Not committing to anything, mind. Pull reqs are welcome though.
- GUI
- private netrunnerdb support
- alternate art
- alternate card image source support
- support for flip ids
- image resizing
- compiled version
