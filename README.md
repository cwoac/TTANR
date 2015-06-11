# TTANR
ANR deck image creator for TableTop Simulator

Currently just a library, but wrapping a gui around it soon.

## Notes
This program comes supplied with *no* assets. Card fronts are pulled from netrunnerdb and cached in a 'cards' directory.

This code is to be considered *very* alpha - there is is little/no error handling at the moment.

## Usage
Example
```
import netdb
deck=netdb.load_octgn_deck('my_deckfile.o8n')
deck2=netdb.load_netrunnerdb_deck(20386)
deck_image=netdb.build_deck_image(deck)
deck_image.save('my_deck.jpg')
deck2_image=netdb.build_deck_image(deck2)
deck2_image.save('my_other_deck.jpg)
```
