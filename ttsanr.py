#!/usr/bin/env python27

import ttsutil
import os.path

import urllib
import json

import untangle

import argparse
import shutil

import PIL.Image


cards={}

debug=True

# TTS util overrides
def make_filename(image):
  return ttsutil.make_cache_filename(image,"ANR")

def make_cache_dir():
  ttsutil.make_cache_dir("ANR")

def build_chest_file(deck,base_url):
  chest=ttsutil.build_chest_file(deck,base_url)
  if deck['side']=='Corp':
    chest['ObjectStates'][0]['Transform']['rotY']=90

  # check for special exceptions
  if deck['jinteki-biotech']:
    chest['ObjectStates'][0]['CustomDeck']['2']= {
      "FaceURL":base_url+'08012-id.jpg',
      "BackURL":base_url+'08012-id-back.jpg'
    }
    chest['ObjectStates'][0]['DeckIDs']=[200,201,202]+chest['ObjectStates'][0]['DeckIDs']

  return chest

def get_runner_back():
    filename = os.path.join("cards","ANR","runner-back.png")
    if not os.path.isfile(filename):
	print("No runner back found. Downloading")
        data=urllib.urlopen("http://vignette1.wikia.nocookie.net/ancur/images/a/a0/Runner_back.png/revision/latest").read()
        fh=open(filename,'wb')
        fh.write(data)
        fh.close()
    return ttsutil.load_image_at_size(filename)

def get_corp_back():
    filename = os.path.join("cards","ANR","corp-back.png")
    if not os.path.isfile(filename):
	print("No corp back found. Downloading")
        data=urllib.urlopen("http://vignette3.wikia.nocookie.net/ancur/images/c/c3/Corp_back.png/revision/latest").read()
        fh=open(filename,'wb')
        fh.write(data)
        fh.close()
    return ttsutil.load_image_at_size(filename)

def get_card(id):
    if not cards.has_key(id):
        filename = make_filename(id+".json")
        if not os.path.isfile(filename):
            make_cache_dir()
            print "Downloading card id: %s" % id
            data=urllib.urlopen("http://netrunnerdb.com/api/card/%s" % id).read()
            fh=open(filename,'w')
            fh.write(data)
            fh.close()
        data=open(filename).read()
        j_data=json.loads(data)
        cards[id]=j_data[0]
        image_filename = make_filename(id+".png")
        if not os.path.isfile(image_filename):
          make_cache_dir()
          print "Downloading card image to: %s" % image_filename
          data=urllib.urlopen("http://netrunnerdb.com/%s" % j_data[0]['imagesrc']).read()
          fh=open(image_filename,'wb')
          fh.write(data)
          fh.close()
    return cards[id]

def get_flip_image(id,idx):
    if id!='08012':
        print("Unknown flip id %s" % id )
        return
    if idx!='A' and idx!='B' and idx!='C':
        print("Unknown flip index %s for %s" % (idx,id) )
        return
    filename = make_filename(id+idx+".png")
    if not os.path.isfile(filename):
        make_cache_dir()
        print "Downloading card image to: %s" % filename
        # TODO: figure out a better way of doing this.
        data=None
        if idx=='A':
            data=urllib.urlopen("http://vignette2.wikia.nocookie.net/ancur/images/9/96/08012A.png").read()
        if idx=='B':
            data=urllib.urlopen("http://vignette3.wikia.nocookie.net/ancur/images/6/6a/08012B.png").read()
        if idx=='C':
            data=urllib.urlopen("http://vignette3.wikia.nocookie.net/ancur/images/a/a1/08012C.png").read()
        fh=open(filename,'wb')
        fh.write(data)
        fh.close()
    return ttsutil.load_image_at_size(filename)

def print_deck(deck):
    print('''
    Deck: %s
    Filename: %s
    Side: %s
    Size: %s
    ''' % ( deck['name'],deck['filename'],deck['side'],ttsutil.count_deck(deck)))

def load_netrunnerdb_deck(id):
    print("Attempting to load deck %s from netrunnerdb" % id )
    data=urllib.urlopen("http://netrunnerdb.com/api/decklist/%s" % id).read()
    j_data=json.loads(data)

    deck={
        'name':j_data['name'],
        'cards':[],
        'filename':ttsutil.sanitise_filename(j_data['name']),
        'jinteki-biotech':False
    }

    for id in j_data['cards'].keys():
        card=get_card(id)
        if card['type_code']=='identity':
            if id=='08012':
                deck['jinteki-biotech']=True
            else:
                deck['cards'].insert(0,(id,1))
            deck['side']=card['side']
        else:
            deck['cards'].append((id,j_data['cards'][id]))

    if debug:
        print_deck(deck)
    return deck


def load_octgn_deck(filename):
    print("Attempting to load octgn deck from %s" % filename )
    deckXML = untangle.parse(filename)
    deck={
        'cards':[],
        'name':os.path.splitext(os.path.basename(filename))[0],
        'jinteki-biotech':False
    }
    # add id
    id=deckXML.deck.section[0].card['id'][-5:]
    if id=='08012':
        deck['jinteki-biotech']=True
    else:
        deck['cards'].append((id,1))
    idcard=get_card(id)
    deck['side']=idcard['side']
    deck['filename']=ttsutil.sanitise_filename(deck['name'])
    # add the rest
    for card in deckXML.deck.section[1].card:
        deck['cards'].append((card['id'][-5:],int(card['qty'])))

    if debug:
        print_deck(deck)
    return deck

def build_08012_image():
    # build mini-deck for flip ID Jinteki Biotech
    im = PIL.Image.new('RGBA',(10*ttsutil.imgW,7*ttsutil.imgH),(0,0,0,0))
    offX=0
    image=get_flip_image('08012','A')
    im.paste(image,(offX,0))
    offX+=ttsutil.imgW
    image=get_flip_image('08012','B')
    im.paste(image,(offX,0))
    offX+=ttsutil.imgW
    image=get_flip_image('08012','C')
    im.paste(image,(offX,0))
    back=ttsutil.get_cache_image('08012','ANR')
    im.paste(back,(2700,2514))
    return im

def load_anr_back(deck):
    back=None
    if deck['back_filename']:
        print "loading custom back %s" % deck['back_filename']
        back=ttsutil.load_image_at_size(deck['back_filename'])
    else:
        if deck['side']=='Corp':
            back=get_corp_back()
        else:
            back=get_runner_back()
    return back

def write_files(deck,base_url,write_local,local_target,install):
  chest=build_chest_file(deck,base_url)
  back_image=load_anr_back(deck)

  ttsutil.write_files(deck,chest,base_url,write_local,local_target,install,back_image,"ANR")

  if not deck['jinteki-biotech']:
    return

  jbDeckImage=build_08012_image()
  jbBackImage=ttsutil.get_cache_image('08012','ANR')

  basefilename=deck['filename']
  jbDeckFilename=os.path.join(local_target,"08012-id.jpg")
  jbBackFilename=os.path.join(local_target,"08012-id-back.jpg")

  if write_local:
    print("Writing %s" % jbDeckFilename)
    print("Writing %s" % jbBackFilename)
    jbDeckImage.save(jbDeckFilename,'JPEG')
    jbBackImage.save(jbBackFilename,'JPEG')

  if install:
    ttsJbDeckFilename=ttsutil.make_tts_image_filename(base_url+jbDeckFilename)
    ttsJbBackFilename=ttsutil.make_tts_image_filename(base_url+jbBackFilename)
    print("Writing %s" % ttsJbDeckFilename)
    jbDeckImage.save(ttsJbDeckFilename,'JPEG')
    print("Writing %s" % ttsJbBackFilename)
    jbBackImage.save(ttsJbBackFilename,'JPEG')



def main():
    parser = argparse.ArgumentParser(description="Create a set of files for loading ANR decks into TableTop Simulator")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-n","--netrunnerdb",metavar="ID",help="Load deck from netrunnerdb using given ID.")
    group.add_argument("-o","--octgn",metavar="file",help="Load the given o8n file (in octgn format).")
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

    deck=None
    if args.netrunnerdb != None:
        deck=load_netrunnerdb_deck(args.netrunnerdb)
    if args.octgn != None:
        deck=load_octgn_deck(args.octgn)

    deck['back_filename']=args.back
    write_files(deck,baseurl,args.writelocal,"",args.install)

if __name__ == "__main__":
    main()
