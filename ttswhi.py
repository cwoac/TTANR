#!/usr/bin/env python27

import ttsutil
import urllib
import BeautifulSoup

cards={}
debug=True
game="WHI"

# TTS util overrides

def make_filename(image):
  return ttsutil.make_filename(image,game)

def make_cache_dir():
  ttsutil.make_cache_dir(game)

def load_deckbox_deck(id):
  print("Attempting to load deck %s from deckbox" % id)
  # TODO: read name better
  name = "Deck id %s" % id
  deck={
    'name':name,
    'cards':[],
    'filename':ttsutil.sanitise_filename(name)
  }

  data=urllib.urlopen("http://deckbox.org/sets/%s/export" % id).read()
  soup=BeautifulSoup.BeautifulSoup(data)
  for line in soup.body.childGenerator():
    if not isinstance(line,BeautifulSoup.NavigableString):
      continue
    line=line.strip()
    if len(line)==0:
      continue
    count=int(line[0])
    name=line[1:]
    print( "%s (x%s)" % (name,count) )
    deck['cards'].append((name,count))
  return deck

x=load_deckbox_deck(1007109)

print x
