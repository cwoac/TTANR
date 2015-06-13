#!/usr/bin/env python27

import urllib
import json
import PIL.Image
import os.path
import os
import untangle
import random
import string
import argparse
import shutil

cards={}
imgW=300
imgH=419

def sanitise_filename(filename):
    # remove unprintable characters from a filename
    valid_chars = "-_.()%s%s" % (string.ascii_letters, string.digits)
    return ''.join(c for c in filename if c in valid_chars)

def tts_filename(filename):
    # Convert a filename to TTS format.
    valid_chars = "%s%s" % (string.ascii_letters, string.digits)
    return ''.join(c for c in filename if c in valid_chars)
    

def gen_guid():
    # generate a random 6 char hex string
    return ''.join([random.choice('0123456789abcdef') for x in range(6)])


def count_deck(deck):
    return sum([qty for _,qty in deck['cards']])

def build_chest_file(deck,base_url):
    # much of this is fixed.
    chest={
      "SaveName": "",
      "GameMode": "",
      "Date": "",
      "Table": "",
      "Sky": "",
      "Note": "",
      "Rules": "",
      "PlayerTurn": "",
      "ObjectStates": [
        {
          "Name": "DeckCustom",
          "Nickname": deck['name'],
          "Transform": {
            "posX": 0,
            "posY": 0,
            "posZ": 0,
            "rotX": 0,
            "rotY": 90 if deck['side']=='Corp' else 0,
            "rotZ": 180,
            "scaleX": 1.75,
            "scaleY": 1.75,
            "scaleZ": 1.75
          },
          "Description": "",
          "ColorDiffuse": {
            "r": 1,
            "g": 1,
            "b": 1
          },
          "Grid": True,
          "Locked": False,
          "SidewaysCard": False,
          "DeckIDs": range(100,100+count_deck(deck)),
          "CustomDeck":{ "1": {
            "FaceURL":base_url+deck['filename']+'.jpg',
            "BackURL":base_url+deck['filename']+'-back.jpg'
          } },
          "Guid": gen_guid()
         }]
    }

    return chest

def make_cache_dir():
    if not os.path.isdir("cards"):
        os.mkdir("cards")

def get_runner_back():
    filename = os.path.join("cards","runner-back.png")
    if os.path.isfile(filename):
        return PIL.Image.open(filename)
    print "No image back found, generating one"
    print "Create cards/runner-back.png to avoid this message."
    return PIL.Image.new('RGBA',(imgW,imgH),(255,0,0,255))

def get_corp_back():
    filename = os.path.join("cards","corp-back.png")
    if os.path.isfile(filename):
        return PIL.Image.open(filename)
    print "No image back found, generating one"
    print "Create cards/corp-back.png to avoid this message."
    return PIL.Image.new('RGBA',(imgW,imgH),(0,0,255,255))

def get_card(id):
    if not cards.has_key(id):
        filename = os.path.join("cards",id+".json")
        if not os.path.isfile(filename):
            make_cache_dir()
            print "downloading card id: %s" % id
            data=urllib.urlopen("http://netrunnerdb.com/api/card/%s" % id).read()
            fh=open(filename,'w')
            fh.write(data)
            fh.close()
        data=open(filename).read()
        j_data=json.loads(data)
        cards[id]=j_data[0]
    return cards[id]

def get_image(id):
    filename = os.path.join("cards",id+".png")
    if not os.path.isfile(filename):
        make_cache_dir()
        print "Downloading %s" % filename
        card=get_card(id)
        data=urllib.urlopen("http://netrunnerdb.com/%s" % card['imagesrc']).read()
        fh=open(filename,'wb')
        fh.write(data)
        fh.close()
    return PIL.Image.open(filename)

def load_netrunnerdb_deck(id):
    data=urllib.urlopen("http://netrunnerdb.com/api/decklist/%s" % id).read()
    j_data=json.loads(data)

    deck={
        'name':j_data['name'],
        'cards':[],
        'filename':sanitise_filename(j_data['name'])
    }

    for id in j_data['cards'].keys():
        card=get_card(id)
        if card['type_code']=='identity':
            deck['cards'].insert(0,(id,1))
            deck['side']=card['side']
        else:
            deck['cards'].append((id,j_data['cards'][id]))

    return deck


def load_octgn_deck(filename):
    deckXML = untangle.parse(filename)
    deck={
        'cards':[],
        'name':os.path.splitext(os.path.basename(filename))[0]
    }
    # add id
    id=deckXML.deck.section[0].card['id'][-5:]
    idcard=get_card(id)
    deck['side']=idcard['side']
    deck['cards'].append((id,1))
    deck['filename']=sanitise_filename(deck['name'])
    # add the rest
    for card in deckXML.deck.section[1].card:
        deck['cards'].append((card['id'][-5:],int(card['qty'])))
    return deck

def build_deck_image(deck):
    # first build the output file
    im = PIL.Image.new('RGBA',(10*imgW,7*imgH),(0,0,0,0))

    curImg = 0
    for card,qty in deck['cards']:
        image = get_image(card)
        for _ in range(qty):
            offX = (curImg%10)*imgW
            offY = (curImg/10)*imgH
            im.paste(image,(offX,offY))
            curImg+=1

    # what side is this?
    back=None
    if deck['side']=='Corp':
        back=get_corp_back()
    else:
        back=get_runner_back()

    im.paste(back,(2700,2514))

    return im

def write_files(deck,base_url,install=False):    
    chest=build_chest_file(deck,base_url)
    deckImage=build_deck_image(deck)
    backImage=None
    if deck['side']=='Corp':
        backImage=get_corp_back()
    else:
        backImage=get_runner_back()

    basefilename=deck['filename']
    with open(basefilename+'.json','w') as chestFile:
        json.dump(chest,chestFile)

    deckFilename=basefilename+'.jpg'
    backFilename=basefilename+'-back.jpg'
    deckImage.save(deckFilename,'JPEG')
    backImage.save(backFilename,'JPEG')

    if install:
        tts_dir=os.path.join(os.path.expanduser("~"),"Documents","My Games","Tabletop Simulator")
        tts_chest_dir=os.path.join(tts_dir,"Saves","Chest")
        tts_image_dir=os.path.join(tts_dir,"Mods","Images")

        with open(os.path.join(tts_chest_dir,basefilename+'.json'),'w') as chestFile:
            json.dump(chest,chestFile)

        ttsDeckFilename=os.path.join(tts_image_dir,tts_filename(base_url+deckFilename)+'.jpg')
        ttsBackFilename=os.path.join(tts_image_dir,tts_filename(base_url+backFilename)+'.jpg')
        print ttsDeckFilename        
        deckImage.save(ttsDeckFilename,'JPEG')
        print ttsBackFilename
        backImage.save(ttsBackFilename,'JPEG')
        

    

def main():
    parser = argparse.ArgumentParser(description="Create a set of files for loading ANR decks into TableTop Simulator")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-n","--netrunnerdb",metavar="ID",help="Load deck from netrunnerdb using given ID.")
    group.add_argument("-o","--octgn",metavar="file",help="Load the given o8n file (in octgn format).")
    group2 = parser.add_mutually_exclusive_group(required=True)
    group2.add_argument("-i","--install",action="store_true",help="Install files into local TTS install.")
    group2.add_argument("-u","--url",help="Base url for where the images will be made availiable")
    args = parser.parse_args()

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

    print baseurl
    write_files(deck,baseurl,args.install)

if __name__ == "__main__":
    main()
