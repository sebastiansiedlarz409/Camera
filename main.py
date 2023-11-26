import os
import busio
import epd4in2
from board import SCL, SDA
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from enum import Enum
from picamera import PiCamera
from datetime import datetime
import RPi.GPIO as GPIO
import adafruit_ssd1306 as ada

#OLED

i2c = None
oled = None
oled_frame = None
oled_draw = None

def oled_init():
  global i2c, oled
  i2c = busio.I2C(SCL, SDA)
  oled = ada.SSD1306_I2C(128,32,i2c)

def oled_clear():
  global oled_frame, oled_draw
  oled.fill(0)
  oled.show()
  #oled.rotate(180)
  oled_frame = Image.new("1", (oled.width, oled.height))
  oled_draw = ImageDraw.Draw(oled_frame)

def oled_display():
  oled.image(oled_frame)
  oled.show()

def oled_draw_text(font_path, text, x, y, font_size):
  font = ImageFont.truetype(font_path, font_size)
  oled_draw.text((x,y), text, font=font, fill=255)

#OLED

#CAMERA

def camera_take():
  camera = PiCamera()

  now = datetime.now()
  name = now.strftime("P_%Y%m%d_%H%M%S")
  camera.color_effects = (128,128)
  camera.capture(f"{gallery_normal_path}/{name}.jpg")

  print(f"Saved {name}.jpg")

  gallery_black(f"{name}.jpg")

  print(f"Converted {name}.jpg")
  camera.close()

  oled_clear()
  oled_draw_text(base_font, name, 5, 2, 12)
  oled_display()

  screen_draw_image(f"{gallery_path}/{name}.jpg")

#CAMERA

#GALLERY
gallery_path = "GALLERY/black"
gallery_normal_path = "GALLERY/norm"
index = 0
count = 0
gallery = []
target_image = ""

def gallery_init():
  global gallery, count
  gallery = os.listdir(gallery_path)

  count = len(gallery)
  print(f"{count} images loaded")
  print(gallery)

def gallery_black(name):
  image = Image.open(gallery_normal_path+"/"+name).convert('L')
  image = image.resize((400, 300))
  image.save(gallery_path+"/"+name, "JPEG")

def get_next_image():
  global index

  #reset
  if index >= count: index = 0

  if count == 0: return None
  print("Loading "+str(index)+": "+gallery[index])

  image = gallery_path + "/" + gallery[index]

  oled_clear()
  oled_draw_text(base_font, "#" + gallery[index], 5, 2, 10)
  index += 1
  if index >= count: 
    index = 0
  oled_draw_text(base_font, " " + gallery[index], 5, 15, 10)
  oled_display()

  return image

def get_prev_image():
  global index

  #reset
  if index >= count: index = 0

  if count == 0: return None
  print("Loading "+str(index)+": "+gallery[index])

  image = gallery_path + "/" + gallery[index]

  oled_clear()
  oled_draw_text(base_font, " " + gallery[index], 5, 15, 10)
  index -= 1
  if index < 0:
    index = count - 1
  oled_draw_text(base_font, "#" + gallery[index], 5, 2, 10)
  oled_display()

  return image

#GALLERY

#DRAWING

base_font = '/usr/share/fonts/truetype/freefont/DejaVuSans.ttf'
cool_font = 'Pacifico.ttf'

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
  epd.display(epd.getbuffer(img))

def screen_draw_ui(dir):
  global redraw, target_image

  #avoid useless refreshing
  redraw = False

  if ui == Screen.MAIN:
    screen_draw_text(cool_font, "TAKE A PHOTO", 8, 40, 46)
    screen_draw_text(cool_font, "AND WAIT :)", 30, 150, 46)

    screen_display()
  elif ui == Screen.GALLERY:
    if count == 0:
      screen_draw_text(cool_font, "EMPTY GALLERY", 35, 70, 44)
      screen_display()
    else:
        print(f"Draw from gallery {target_image}")
        screen_draw_image(target_image)

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
    global epd, frame, base_font, target_image
    global KEY1, KEY2, KEY3, KEY4, HKEY
    global redraw, ui

    #init keys
    keys_init()

    #init images
    gallery_init()

    #init screen
    screen_init()

    #init oled
    oled_init()
    oled_clear()
    oled_draw_text(base_font, "GALLERY", 15,2, 20)
    oled_display()

    #first ui draw
    redraw = True
    dir = None

    while True:
      #key routine
      if HKEY == KEY1:
        print("SHOT")
        camera_take()
        gallery_init()
        HKEY = 0
      elif HKEY == KEY2:
        print("BACK")
        HKEY = 0
        if ui != Screen.MAIN:
          ui = Screen.MAIN
          redraw = True
        else:
          ui = Screen.GALLERY
          redraw = True
      elif HKEY == KEY3:
        print("NEXT");
        HKEY = 0
        target_image = get_next_image()
      elif HKEY == KEY4:
        print("PREV");
        HKEY = 0
        target_image = get_prev_image()

      #refresh ui
      if redraw:
        screen_clear()
        screen_draw_ui(dir)

if __name__ == '__main__':
    main()
