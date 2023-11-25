import epd4in2
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from enum import Enum
import os
import RPi.GPIO as GPIO
from picamera import PiCamera
from datetime import datetime

#CAMERA

def camera_take():
  camera = PiCamera()

  now = datetime.now()
  name = now.strftime("P_%Y_%m_%d_%H_%M_%S")
  camera.color_effects = (128,128)
  camera.capture(f"{gallery_normal_path}/{name}.jpg")

  print(f"Saved {name}.jpg")

  gallery_black(f"{name}.jpg")

  print(f"Converted {name}.jpg")
  camera.close()

#CAMERA

#GALLERY
gallery_path = "GALLERY/black"
gallery_normal_path = "GALLERY/norm"
index = 0
count = 0
gallery = []

def gallery_init():
  global gallery, count
  gallery = os.listdir(gallery_path)

  count = len(gallery)
  print(f"{count} images loaded")
  print(gallery)

def gallery_black(name):
  image = Image.open(gallery_normal_path+"/"+name).convert('L')
  image = image.resize((400, 300))
  image.save(gallery_path+"/"+name, "BMP")

def get_next_image():
  global index

  #reset
  if index >= count: index = 0

  if count == 0: return None
  print("Loading "+str(index)+": "+gallery[index])

  image = Image.open(gallery_path + "/" + gallery[index])
  index += 1

  if index >= count: index = 0

  return image

def get_prev_image():
  global index

  #reset
  if index >= count: index = 0

  if count == 0: return None
  print("Loading "+str(index)+": "+gallery[index])

  image = Image.open(gallery_path + "/" + gallery[index])
  index -= 1

  if index < 0: index = count - 1

  return image

#GALLERY

#DRAWING

base_font = '/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf'

epd = None
frame = None
draw = None

def screen_init():
  global epd
  epd = epd4in2.EPD()
  epd.init()
  screen_clear()

def screen_clear():
  global frame, draw
  frame = Image.new('1', (epd.width, epd.height), 255)
  draw = ImageDraw.Draw(frame)
  epd.Clear()

def screen_sleep(t):
  time.sleep(t)

def screen_display():
  epd.display(epd.getbuffer(frame))

def screen_draw_text(font_path, text, x, y, font_size):
  font = ImageFont.truetype(font_path, font_size)

  draw.text((x, y), text, font = font, fill = 0)

def screen_draw_image(image):
  screen_clear()
  img = Image.open(image)
  frame.paste(img, (50,10))

def screen_draw_ui(dir):
  global count
  global KEY1, KEY2, KEY3, KEY4, HKEY
  global redraw

  #avoid useless refreshing
  redraw = False

  if ui == Screen.MAIN:
    screen_draw_text(base_font, "TAKE A PHOTO", 35, 70, 46)
    screen_draw_text(base_font, "AND WAIT :)", 50, 200, 46)

    screen_display()
  elif ui == Screen.GALLERY:
    gallery_init()
    screen_clear()
    if count == 0:
      screen_draw_text(base_font, "EMPTY GALLERY", 35, 70, 44)
    else:
      if dir == 1:
        screen_draw_image(get_next_image())
      elif dir == -1:
        screen_draw_image(get_prev_image())
    screen_display()

#DRAWING

#KEYS

HKEY = 0

KEY1 = 26
KEY2 = 19
KEY3 = 6
KEY4 = 13

def keys_interrupt(channel):
  global HKEY
  if HKEY == 0:
    HKEY = channel

def keys_init():
  global KEY1, KEY2, KEY3, KEY4

  GPIO.setmode(GPIO.BCM)

  GPIO.setup(KEY1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
  GPIO.setup(KEY2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
  GPIO.setup(KEY3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
  GPIO.setup(KEY4, GPIO.IN, pull_up_down=GPIO.PUD_UP)

  GPIO.add_event_detect(KEY1, GPIO.FALLING, callback=keys_interrupt, bouncetime=200)
  GPIO.add_event_detect(KEY2, GPIO.FALLING, callback=keys_interrupt, bouncetime=200)
  GPIO.add_event_detect(KEY3, GPIO.FALLING, callback=keys_interrupt, bouncetime=200)
  GPIO.add_event_detect(KEY4, GPIO.FALLING, callback=keys_interrupt, bouncetime=200)

#KEYS

class Screen(Enum):
  MAIN = 0,
  GALLERY = 1

ui = Screen.MAIN
redraw = False

def main():
    global epd, frame, base_font
    global KEY1, KEY2, KEY3, KEY4, HKEY
    global redraw, ui

    #init keys
    keys_init()

    #init images
    gallery_init()
    #gallery_black("asd.jpg")

    #init screen
    screen_init()

    #first ui draw
    redraw = True
    dir = None

    while True:
      #key routine
      if HKEY == KEY1:
        print("SHOT")
        HKEY = 0
        #camera_take()
      elif HKEY == KEY2:
        print("BACK")
        HKEY = 0
        if ui != Screen.MAIN:
          ui = Screen.MAIN
          redraw = True
      elif HKEY == KEY3:
        print("NEXT");
        HKEY = 0
        dir = 1
        ui = Screen.GALLERY
        redraw = True
      elif HKEY == KEY4:
        print("PREV");
        HKEY = 0
        dir = -1
        ui = Screen.GALLERY
        redraw = True

      #refresh ui
      if redraw:
        screen_clear()
        screen_draw_ui(dir)

if __name__ == '__main__':
    main()
