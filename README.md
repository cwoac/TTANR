# TTANR
ANR deck image creator for TableTop Simulator

Currently just a library, but wrapping a gui around it soon.

## Notes
This program comes supplied with *no* assets. Card fronts are pulled from netrunnerdb and cached in a 'cards' directory.

This code is to be considered *very* alpha - there is is little/no error handling at the moment.

It will create a .json file for TableTop Simulator. To use, first create a deck using `load_octgn_deck` or `load_netrunnerdb_deck`, then write the files using `write_files` - you need to provide an url for where the images will be stored. This *can* be a local path (e.g. 'file:///c:/mydecks/'), but in that case you need to get the file to the other players and they must put it in the same location. Upload the two .jpg files to that url, then copy the .json file to you TableTop Simulator save directory (typically `c:\Users\myusername\Documents\My Games\TableTop Simulator\Saves\Chest`)

It will use a fixed block of red or blue for the the backs of cards. If you want to use other images, create `cards/corp-back.png` and `cards/runner-back.png`, they *must* be 300x419 in size.

## Usage
Example
```
import netdb
deck=netdb.load_octgn_deck('my_deckfile.o8n')
deck2=netdb.load_netrunnerdb_deck(20386)

netdb.write_files(deck,'http://mywebserver.com/files/')
```
