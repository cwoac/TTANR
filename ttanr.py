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
debug=True

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

def load_image_at_size(filename):
    # load an image, forcing the colourspace and resizing if required.
    img=PIL.Image.open(filename).convert("RGB")
    w,h=img.size
    if w==imgW and h==imgH:
      # already the right size
      return img
    w_scale=(1.0*imgW)/w
    h_scale=(1.0*imgH)/h
    scale=min(h_scale,w_scale)
    newW=int(w*scale)
    newH=int(h*scale)
    img=img.resize((newW,newH),PIL.Image.ANTIALIAS)
    if newW==imgW and newH==imgH:
      # was the correct aspect ratio
      return img
    # create a new black image of the correct size.
    out=PIL.Image.new('RGBA',(imgW,imgH),(0,0,0,255))
    # TODO: center image
    out.paste(img,(0,0))
    return out

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
            "rotY": 90 if deck['side']=='Corp' else 180,
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

    # check for special exceptions
    if deck['jinteki-biotech']:
        chest['ObjectStates'][0]['CustomDeck']['2']= {
                "FaceURL":base_url+'08012-id.jpg',
                "BackURL":base_url+'08012-id-back.jpg'
            }
        chest['ObjectStates'][0]['DeckIDs']=[200,201,202]+chest['ObjectStates'][0]['DeckIDs']
    print chest

    return chest

def make_cache_dir():
    if not os.path.isdir("cards"):
        os.mkdir("cards")

def get_runner_back():
    filename = os.path.join("cards","runner-back.png")
    if os.path.isfile(filename):
        return load_image_at_size(filename)
    print "No image back found, generating one"
    print "Create cards/runner-back.png to avoid this message."
    return PIL.Image.new('RGBA',(imgW,imgH),(255,0,0,255))

def get_corp_back():
    filename = os.path.join("cards","corp-back.png")
    if os.path.isfile(filename):
        return load_image_at_size(filename)
    print "No image back found, generating one"
    print "Create cards/corp-back.png to avoid this message."
    return PIL.Image.new('RGBA',(imgW,imgH),(0,0,255,255))

def get_card(id):
    if not cards.has_key(id):
        filename = os.path.join("cards",id+".json")
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
    return cards[id]

def get_flip_image(id,idx):
    if id!='08012':
        print("Unknown flip id %s" % id )
        return
    if idx!='A' and idx!='B' and idx!='C':
        print("Unknown flip index %s for %s" % (idx,id) )
        return
    filename = os.path.join("cards",id+idx+".png")
    if not os.path.isfile(filename):
        make_cache_dir()
        print "Downloading card image: %s" % filename
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
    return load_image_at_size(filename)


def get_image(id):
    filename = os.path.join("cards",id+".png")
    if not os.path.isfile(filename):
        make_cache_dir()
        print "Downloading card image: %s" % filename
        card=get_card(id)
        data=urllib.urlopen("http://netrunnerdb.com/%s" % card['imagesrc']).read()
        fh=open(filename,'wb')
        fh.write(data)
        fh.close()
    return load_image_at_size(filename)

def print_deck(deck):
    print('''
    Deck: %s
    Filename: %s
    Side: %s
    Size: %s
    ''' % ( deck['name'],deck['filename'],deck['side'],count_deck(deck)))

def load_netrunnerdb_deck(id):
    print("Attempting to load deck %s from netrunnerdb" % id )
    data=urllib.urlopen("http://netrunnerdb.com/api/decklist/%s" % id).read()
    j_data=json.loads(data)

    deck={
        'name':j_data['name'],
        'cards':[],
        'filename':sanitise_filename(j_data['name']),
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
    deck['filename']=sanitise_filename(deck['name'])
    # add the rest
    for card in deckXML.deck.section[1].card:
        deck['cards'].append((card['id'][-5:],int(card['qty'])))

    if debug:
        print_deck(deck)
    return deck

def build_08012_image():
    # build mini-deck for flip ID Jinteki Biotech
    im = PIL.Image.new('RGBA',(10*imgW,7*imgH),(0,0,0,0))
    offX=0
    image=get_flip_image('08012','A')
    im.paste(image,(offX,0))
    offX+=imgW
    image=get_flip_image('08012','B')
    im.paste(image,(offX,0))
    offX+=imgW
    image=get_flip_image('08012','C')
    im.paste(image,(offX,0))
    back=get_image('08012')
    im.paste(back,(2700,2514))
    return im

def load_anr_back(deck):
    back=None
    if deck['back_filename']:
        print "loading custom back %s" % deck['back_filename']
        back=load_image_at_size(deck['back_filename'])
    else:
        if deck['side']=='Corp':
            back=get_corp_back()
        else:
            back=get_runner_back()
    return back

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
    back=load_anr_back(deck)

    im.paste(back,(2700,2514))

    return im

def write_files(deck,base_url,write_local,local_target,install):
    chest=build_chest_file(deck,base_url)
    deckImage=build_deck_image(deck)
    deck2Image=None


    if deck['jinteki-biotech']:
        jbDeckImage=build_08012_image()
        jbBackImage=get_image('08012')

    backImage=load_anr_back(deck)

    basefilename=deck['filename']
    jbDeckFilename=os.path.join(local_target,"08012-id.jpg")
    jbBackFilename=os.path.join(local_target,"08012-id-back.jpg")
    deckFilename=os.path.join(local_target,basefilename+'.jpg')
    backFilename=os.path.join(local_target,basefilename+'-back.jpg')
    chestFilename=os.path.join(local_target,basefilename+'.json')

    if write_local:
        print("Writing %s" % chestFilename)
        with open(chestFilename,'w') as chestFile:
            json.dump(chest,chestFile)
        print("Writing %s" % deckFilename)
        print("Writing %s" % backFilename)
        deckImage.save(deckFilename,'JPEG')
        backImage.save(backFilename,'JPEG')
        if deck['jinteki-biotech']:
            print("Writing %s" % jbDeckFilename)
            print("Writing %s" % jbBackFilename)
            jbDeckImage.save(jbDeckFilename,'JPEG')
            jbBackImage.save(jbBackFilename,'JPEG')

    if install:
        tts_dir=os.path.join(os.path.expanduser("~"),"Documents","My Games","Tabletop Simulator")
        tts_chest_dir=os.path.join(tts_dir,"Saves","Chest")
        tts_image_dir=os.path.join(tts_dir,"Mods","Images")

        tts_chest_name=os.path.join(tts_chest_dir,basefilename+'.json')
        print("Writing %s" % tts_chest_name)
        with open(tts_chest_name,'w') as chestFile:
            json.dump(chest,chestFile)

        ttsDeckFilename=os.path.join(tts_image_dir,tts_filename(base_url+deckFilename)+'.jpg')
        ttsBackFilename=os.path.join(tts_image_dir,tts_filename(base_url+backFilename)+'.jpg')
        print("Writing %s" % ttsDeckFilename)
        deckImage.save(ttsDeckFilename,'JPEG')
        print("Writing %s" % ttsBackFilename)
        backImage.save(ttsBackFilename,'JPEG')
        if deck['jinteki-biotech']:
            ttsJbDeckFilename=os.path.join(tts_image_dir,tts_filename(base_url+jbDeckFilename)+'.jpg')
            ttsJbBackFilename=os.path.join(tts_image_dir,tts_filename(base_url+jbBackFilename)+'.jpg')
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
