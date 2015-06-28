#!/usr/bin/env python27

import PIL.Image
import random
import string
import os.path
import os
import json

imgW=300
imgH=419

def make_filename(image_name,game=None):
  if game:
    return os.path.join("cards",game,image_name)
  return os.path.join("cards",image_name)

def make_cache_dir(game=None):
  if not os.path.isdir("cards"):
    os.mkdir("cards")
  if game:
    gameDir=os.path.join("cards",game)
    if not os.path.isdir(gameDir):
      os.mkdir(gameDir)

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

def get_image(card_name,game=None):
  for image_format in ['.png','.jpg','.bmp']:
    card_filename=make_filename(card_name+image_format,game)
    if os.path.isfile(card_filename):
      return load_image_at_size(card_filename)
  print("Unable to find image for %s (in %s)" % (card_name,game))


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
            "rotY": 180,
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

def build_deck_image(deck,back_image,game=None):
    # first build the output file
    im = PIL.Image.new('RGBA',(10*imgW,7*imgH),(0,0,0,0))

    curImg = 0
    for card,qty in deck['cards']:
        image = get_image(card,game)
        for _ in range(qty):
            offX = (curImg%10)*imgW
            offY = (curImg/10)*imgH
            im.paste(image,(offX,offY))
            curImg+=1

    im.paste(back_image,(2700,2514))

    return im

def write_files(deck,chest,base_url,write_local,local_target,install,back_image,game=None):
  deck_image=build_deck_image(deck,back_image,game)

  base_filename=deck['filename']
  deck_filename=os.path.join(local_target,base_filename+'.jpg')
  back_filename=os.path.join(local_target,base_filename+'-back.jpg')
  chest_filename=os.path.join(local_target,base_filename+'.json')

  if write_local:
    print("Writing %s" % chest_filename)
    with open(chest_filename,'w') as chest_file:
      json.dump(chest,chest_file)

    print("Writing %s" % deck_filename)
    deck_image.save(deck_filename,'JPEG')
    print("Writing %s" % back_filename)
    back_image.save(back_filename,'JPEG')

  if install:
    tts_dir=os.path.join(os.path.expanduser("~"),"Documents","My Games","Tabletop Simulator")
    tts_chest_dir=os.path.join(tts_dir,"Saves","Chest")
    tts_image_dir=os.path.join(tts_dir,"Mods","Images")

    tts_chest_name=os.path.join(tts_chest_dir,base_filename+'.json')
    print("Writing %s" % tts_chest_name)
    with open(tts_chest_name,'w') as chest_file:
      json.dump(chest,chest_file)

    tts_deck_filename=os.path.join(tts_image_dir,tts_filename(base_url+deck_filename)+'.jpg')
    tts_back_filename=os.path.join(tts_image_dir,tts_filename(base_url+back_filename)+'.jpg')
    print("Writing %s" % tts_deck_filename)
    deck_image.save(tts_deck_filename,'JPEG')
    print("Writing %s" % tts_back_filename)
    back_image.save(tts_back_filename,'JPEG')
