# TTS utils
A set of gui+cli programs for creating [Tabletop Simulator](http://berserk-games.com/) decks.

## TTSANR
ANR deck image creator, working from either octgn format files (`.o8n`) or netrunnerdb decks (public decks only).

### Quickstart

download `ttanr_gui.exe` from the [releases](https://github.com/cwoac/TTANR/releases/latest). Run it, enter a [netrunnerdb](http://netrunnerdb.com/) deck id, click go. Run Tabletop Simulator and look in the chest for the deck.
### Usage

For the cli, use either `ttanr.exe` or `python ttanr.py`; for the gui, `ttanr_gui.exe` or `python ttanr_gui.py`

The easiest way is via netrunnerdb. Both players create *public* decks then give the id to the other. Each then uses `-i` to automatically install the files into their TTS saved directory.
Alternatively, don't use `-i` and put the created files up on a webserver using the `-w` and `-u` parameters
Example:
````
ttsanr -n 12345 -i
ttsanr -o my_awesome_deck.o8n -u http://myserver/decks/ -w
ttsanr -n 5438 -u http://myserver/decks/ -w
````

## TTSWHI
WHI deck image creator, working from [cardbox](http://cardbox.org/) decks.

### Quickstart

download `ttsanr_whi.exe` from the [releases](https://github.com/cwoac/TTANR/releases/latest). Run it, enter a [cardbox](http://cardbox.org/) deck id, click go. Run Tabletop Simulator and look in the chest for the deck. Optionally provide an image for the deck back or create `cards/WHI/whi-back.png` (ideally at 300x419) *before* importing your deck to get fancy card backs; otherwise you will have plain green backs.

### Usage

For the cli, use either `ttswhi.exe` or `python ttswhi.py`; for the gui, `ttswhi_gui.exe` or `python ttswhi_gui.py`

Both players should create decks on cardbox.org then give the id to the other. Each then uses `-i` to automatically install the files into their TTS saved directory.
Alternatively, don't use `-i` and put the created files up on a webserver using the `-w` and `-u` parameters
Example:
````
ttswhi -d 12345 -i
ttswhi -d 5438 -u http://myserver/decks/ -w
````

# Notes

These programs come supplied with *no* assets. Card fronts are pulled from online sources and cached in a 'cards' directory.

This code is to be considered alpha - there is is little/no error handling at the moment.

It will create a .json file for Tabletop Simulator. If not installing locally then you need to provide an url for where the images will be stored. This *can* be a local path (e.g. `file:///c:/mydecks/`), but in that case you need to get the file to the other players and they must put it in the same location.

Unless you override the card backs, it will use a fixed block of green for WHI.

It will only use the original card art - if you want to use alt art, figure out either the netrunnerdb card id for the card or WHI card name and replace cards/ANR/id.png or cards/WHI/name.jpg with your file (again, *should* be 300x419 to maximise quality).

## Requirements
Either download a compiled exe, or run using python. In the latter case, you will need:
- python2.7
- untangle
- PIL
- BeautifulSoup

## TODO
Not committing to anything, mind. Pull reqs are welcome though.
- private netrunnerdb support
- alternate art
- alternate card image source support
