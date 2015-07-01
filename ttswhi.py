#!/usr/bin/env python27

import ttsutil
import urllib
import BeautifulSoup
import os.path
import PIL.Image
import argparse

cards={}
debug=True
game="WHI"

# TTS util overrides

def make_filename(image):
  return ttsutil.make_cache_filename(image,game)

def make_cache_dir():
  ttsutil.make_cache_dir(game)

def get_card(id):
  filename=make_filename(id+".jpg")
  if not os.path.isfile(filename):
    make_cache_dir()
    print("Downloading card to: %s" % id)
    data=urllib.urlopen("https://deckbox.org/whi/%s" % id).read()
    soup=BeautifulSoup.BeautifulSoup(data)
    url="http://deckbox.org/%s" % soup.findAll('img',{'id':'card_image'})[0]['src']
    image=urllib.urlopen(url).read()
    fh=open(filename,'wb')
    fh.write(image)
    fh.close()

def load_deckbox_deck(id):
  print("Attempting to load deck %s from deckbox" % id)
  html=urllib.urlopen("https://deckbox.org/sets/%s" % id).read()
  soup=BeautifulSoup.BeautifulSoup(html)
  name = soup.head.title.contents[0].replace("&#x27;","'").split(" - ")[0]
  print("Found deck '%s'" % name )
  deck={
    'name':name,
    'cards':[],
    'filename':ttsutil.sanitise_filename(name),
    'back_filename':None
  }
  print("Loading deck contents")
  data=urllib.urlopen("https://deckbox.org/sets/%s/export" % id).read()
  soup=BeautifulSoup.BeautifulSoup(data)
  for line in soup.body.childGenerator():
    if not isinstance(line,BeautifulSoup.NavigableString):
      continue
    line=line.strip()
    if len(line)==0:
      continue
    count=int(line[0])
    name=line[1:].strip()
    get_card(name)
    deck['cards'].append((name,count))
  return deck

def get_back():
  image=ttsutil.get_cache_image('whi-back',game) or PIL.Image.new('RGBA',(ttsutil.imgW,ttsutil.imgH),(0,255,0,255))
  return image

def write_files(deck,base_url,write_local,local_target,install):
  chest=ttsutil.build_chest_file(deck,base_url)
  back_image=None
  if deck['back_filename']:
    print "loading custom back %s" % deck['back_filename']
    back_image=ttsutil.load_image_at_size(deck['back_filename'])
  else:
    back_image=get_back()
  ttsutil.write_files(deck,chest,base_url,write_local,local_target,install,back_image,game)

def main():
  parser = argparse.ArgumentParser(description="Create a set of files for loading WHI decks into TableTop Simulator")
  parser.add_argument("-d","--deckbox",metavar="ID",help="Load deck from deckbox.org using given ID.")
  parser.add_argument("-b","--back",metavar="backgroundFile",help="Override default back with given file.")
  parser.add_argument("-i","--install",action="store_true",help="Install files into local TTS install.")
  parser.add_argument("-w","--writelocal",action="store_true",help="Write files into the current directory.")
  parser.add_argument("-u","--url",help="Base url for where the images will be made availiable")
  args = parser.parse_args()

  if not (args.install or args.url):
    print("Warning: Neither install (-i) or url (-u) has been specified. You probably don't want to do this.")

  if not (args.install or args.writelocal):
    parser.error("At least one of -i or -w is required.")

  baseurl=args.url or "null://"

  if baseurl.startswith('file') and not baseurl.endswith(os.sep):
    baseurl+=os.sep
  if baseurl.startswith('http') and not baseurl.endswith('/'):
    baseurl+='/'

  deck=load_deckbox_deck(args.deckbox)
  deck['back_filename']=args.back
  write_files(deck,baseurl,args.writelocal,"",args.install)

if __name__ == "__main__":
    main()
