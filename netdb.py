#!/usr/bin/env python27

import urllib
import json
import PIL.Image
import os.path
import os
import untangle

cards={}
imgW=300
imgH=419

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
        print "downloading card id: %s" % id
        data=urllib.urlopen("http://netrunnerdb.com/api/card/%s" % id).read()
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

def get_decklist(id):
    data=urllib.urlopen("http://netrunnerdb.com/api/decklist/%s" % id).read()
    j_data=json.loads(data)
    return j_data['cards']

def parse_deck(cards):
    deck=[]
    for id in cards.keys():
        card=get_card(id)
        if card['type_code']=='identity':
            deck.insert(0,(id,cards[id]))
        else:
            deck.append((id,cards[id]))
    return deck

def load_netrunnerdb_deck(id):
    return parse_deck(get_decklist(id))

def load_octgn_deck(filename):
    deckXML = untangle.parse(filename)
    deck=[]
    # add id
    id=deckXML.deck.section[0].card['id'][-5:]
    deck.append((id,1))
    # add the rest
    for card in deckXML.deck.section[1].card:
        deck.append((card['id'][-5:],int(card['qty'])))
    return deck



def build_deck_image(deck):
    # first build the output file
    im = PIL.Image.new('RGBA',(10*imgW,7*imgH),(0,0,0,0))

    curImg = 0
    for card,qty in deck:
        image = get_image(card)
        for _ in range(qty):
            offX = (curImg%10)*imgW
            offY = (curImg/10)*imgH
            im.paste(image,(offX,offY))
            curImg+=1

    # what side is this?
    id,_ = deck[0]
    back=None
    identity=get_card(id)
    if identity['side']=='Corp':
        back=get_corp_back()
    else:
        back=get_runner_back()

    im.paste(back,(2700,2514))

    return im


