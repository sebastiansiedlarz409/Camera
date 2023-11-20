import epd2in7b
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
  image = image.resize((176, 264))
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

COLORED = 1
UNCOLORED = 0

base_font = '/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf'

epd = epd2in7b.EPD()
frame = []

class Screen(Enum):
  MAIN = 0,
  GALLERY = 1

ui = Screen.MAIN
redraw = False

def screen_init(epd, frame):
  epd.init()

  # clear the frame buffer
  for i in range(0, int(epd.width * epd.height / 8)):
    frame.append(0)

def screen_sleep(epd, t):
  epd.delay_ms(t)

def screen_clear(epd, frame):
  for i in range(0, len(frame)):
    frame[i] = 0

def screen_display(epd, frame):
  epd.display_frame(frame)

def screen_draw_text(epd, frame, font_path, text, x, y, color, font_size):
  font = ImageFont.truetype(font_path, font_size)

  epd.draw_string_at(frame, x, y, text, font, color)

def screen_draw_line(epd, frame, x1, y1, x2, y2, color):
  epd.draw_line(frame, x1, y1, x2, y2, color)

def screen_draw_vline(epd, frame, x, y, height, colored):
  epd.draw_vertical_line(frame, x, y, height, colored)

def screen_draw_hline(epd, frame, x, y, width, colored):
  epd.draw_horizontal_line(frame, x, y, width, colored)

def screen_draw_rectangle(epd, frame, x1, y1, x2, y2, color, filled):
  if filled:
    epd.draw_filled_rectangle(frame, x1, y1, x2, y2, color)
  else:
    epd.draw_rectangle(frame, x1, y1, x2, y2, color)

def screen_draw_circle(epd, frame, x, y, r, color, filled):
  if filled:
    epd.draw_filled_circle(frame, x, y, r, color)
  else:
    epd.draw_circle(frame, x, y, r, color)

def screen_draw_welcome(epd, frame):
  screen_draw_text(epd, frame, base_font, "SMILE", 50, 10, COLORED, 25)
  screen_draw_circle(epd, frame, 90, 160, 80, COLORED, False)
  screen_draw_circle(epd, frame, 90, 160, 81, COLORED, False)
  screen_draw_circle(epd, frame, 90, 160, 82, COLORED, False)

  #smile
  screen_draw_circle(epd, frame, 90, 160, 55, COLORED, False)
  screen_draw_circle(epd, frame, 90, 160, 54, COLORED, False)
  screen_draw_rectangle(epd, frame, 40, 95, 140, 160, UNCOLORED, True)

  #eyes
  screen_draw_circle(epd, frame, 50, 120, 5, COLORED, True)
  screen_draw_circle(epd, frame, 130, 120, 5, COLORED, True)
  screen_display(epd, frame)

def screen_draw_image(epd, image):
  frame = epd.get_frame_buffer(image)
  return frame

def screen_draw_ui(epd, frame, dir):
  global count
  global KEY1, KEY2, KEY3, KEY4, HKEY
  global redraw

  #avoid useless refreshing
  redraw = False

  if ui == Screen.MAIN:
    screen_draw_rectangle(epd, frame, 30, 15, 155, 60, COLORED, False)
    screen_draw_rectangle(epd, frame, 31, 16, 154, 59, COLORED, False)
    screen_draw_text(epd, frame, base_font, "TAKE A PHOTO", 35, 20, COLORED, 16)
    screen_draw_text(epd, frame, base_font, "AND WAIT", 50, 40, COLORED, 16)
    screen_draw_hline(epd, frame,20, 38, 10, COLORED)
    screen_draw_hline(epd, frame,20, 39, 10, COLORED)
    screen_draw_vline(epd, frame,20, 39, 210, COLORED)
    screen_draw_vline(epd, frame,21, 39, 210, COLORED)

    screen_draw_rectangle(epd, frame, 70, 75, 170, 120, COLORED, False)
    screen_draw_rectangle(epd, frame, 71, 76, 169, 119, COLORED, False)
    screen_draw_text(epd, frame, base_font, "BACK TO", 90, 80, COLORED, 16)
    screen_draw_text(epd, frame, base_font, "MAIN VIEW", 80, 100, COLORED, 16)
    screen_draw_hline(epd, frame,60, 98, 10, COLORED)
    screen_draw_hline(epd, frame,60, 99, 10, COLORED)
    screen_draw_vline(epd, frame,60, 99, 150, COLORED)
    screen_draw_vline(epd, frame,61, 99, 150, COLORED)

    screen_draw_rectangle(epd, frame, 85, 155, 165, 200, COLORED, False)
    screen_draw_rectangle(epd, frame, 86, 156, 164, 199, COLORED, False)
    screen_draw_text(epd, frame, base_font, "GALLERY", 90, 160, COLORED, 16)
    screen_draw_text(epd, frame, base_font, "NAVIG.", 100, 180, COLORED, 16)
    screen_draw_vline(epd, frame, 105, 200, 50, COLORED)
    screen_draw_vline(epd, frame, 106, 200, 50, COLORED)
    screen_draw_vline(epd, frame, 150, 200, 50, COLORED)
    screen_draw_vline(epd, frame, 151, 200, 50, COLORED)

    screen_draw_text(epd, frame, base_font, "SHOT", 8, 250, COLORED, 13)
    screen_draw_text(epd, frame, base_font, "BACK", 50, 250, COLORED, 13)
    screen_draw_text(epd, frame, base_font, "NEXT", 95, 250, COLORED, 13)
    screen_draw_text(epd, frame, base_font, "PREV", 140, 250, COLORED, 13)

    screen_display(epd, frame)
  elif ui == Screen.GALLERY:
    gallery_init()
    screen_clear(epd, frame)
    if count == 0:
      screen_draw_text(epd, frame, base_font, "EMPTY GALLERY", 28, 20, COLORED, 16)
    else:
      if dir == 1:
        frame = screen_draw_image(epd, get_next_image())
      elif dir == -1:
        frame = screen_draw_image(epd, get_prev_image())
    screen_display(epd, frame)

#DRAWING

#KEYS

HKEY = 0

KEY1 = 5
KEY2 = 6
KEY3 = 13
KEY4 = 19

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

def main():
    global epd, frame, base_font
    global KEY1, KEY2, KEY3, KEY4, HKEY
    global redraw, ui

    #init keys
    keys_init()

    #init images
    gallery_init()

    #init screen
    screen_init(epd, frame)
    #screen_draw_welcome(epd, frame)
    #screen_sleep(epd, 1000)

    #first ui draw
    redraw = True
    dir = None

    while True:
      #key routine
      if HKEY == KEY1:
        print("SHOT")
        HKEY = 0
        camera_take()
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
        screen_clear(epd, frame)
        screen_draw_ui(epd, frame, dir)

if __name__ == '__main__':
    main()
