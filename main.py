import epd2in7b
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from enum import Enum
import os
import RPi.GPIO as GPIO

#GALLERY
gallery_path = "GALLERY/black"
gallery_normal_path = "GALLERY/norm"
index = 0
count = 0
gallery = []

def gallery_init():
  global gallery_path, gallery, count, index
  gallery = os.listdir(gallery_path)
  count = len(gallery)

def gallery_black(name):
  global gallery_normal_path, gallery_path
  image = Image.open(gallery_normal_path+"/"+name).convert('L')
  image = image.resize((176, 264))
  image.save(gallery_path+"/"+name, "BMP")

def get_next_image():
  global gallery_path, gallery, index, count

  #reset
  if index >= count: index = 0

  if count == 0: return None
  print("Loading "+str(index)+": "+gallery[index])

  image = Image.open(gallery_path + "/" + gallery[index])
  index += 1

  if index >= count: index = 0

  return image

def get_prev_image():
  global gallery_path, gallery, index, count

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

font_path = '/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf'

epd = None
frame_black = []
frame_red = []

class Screen(Enum):
  LIVE = 0,
  GALLERY = 1,
  PHOTO = 2

ui = Screen.LIVE
redraw = False

def screen_init():
  global epd, font, frame_black, frame_red
  epd = epd2in7b.EPD()
  epd.init()

  # clear the frame buffer
  frame_black = [0] * int(epd.width * epd.height / 8)
  frame_red = [0] * int(epd.width * epd.height / 8)

def screen_sleep(t):
  global epd
  epd.delay_ms(t)

def screen_clear():
  global epd, frame_black, frame_red
  for i in range(0, len(frame_black)):
    frame_black[i] = 0
    frame_red[i] = 0

def screen_display():
  global epd, frame_black, frame_red
  epd.display_frame(frame_black, frame_red)

def screen_draw_text(frame, text, x, y, color, font_size):
  global epd, font_path
  font = ImageFont.truetype(font_path, font_size)

  epd.draw_string_at(frame, x, y, text, font, color)

def screen_draw_line(frame, x1, y1, x2, y2, color):
  global epd
  epd.draw_line(frame, x1, y1, x2, y2, color)

def screen_draw_vline(frame, x, y, height, colored):
  global epd
  epd.draw_vertical_line(frame, x, y, height, colored)

def screen_draw_hline(frame, x, y, width, colored):
  global epd
  epd.draw_horizontal_line(frame, x, y, width, colored)

def screen_draw_rectangle(frame, x1, y1, x2, y2, color, filled):
  global epd
  if filled:
    epd.draw_filled_rectangle(frame, x1, y1, x2, y2, color)
  else:
    epd.draw_rectangle(frame, x1, y1, x2, y2, color)

def screen_draw_circle(frame, x, y, r, color, filled):
  global epd
  if filled:
    epd.draw_filled_circle(frame, x, y, r, color)
  else:
    epd.draw_circle(frame, x, y, r, color)

def screen_draw_welcome(frame):
  global epd
  screen_draw_text(frame, "SMILE", 50, 10, COLORED, 25)
  screen_draw_circle(frame, 90, 160, 80, COLORED, False)
  screen_draw_circle(frame, 90, 160, 81, COLORED, False)
  screen_draw_circle(frame, 90, 160, 82, COLORED, False)

  #smile
  screen_draw_circle(frame, 90, 160, 55, COLORED, False)
  screen_draw_circle(frame, 90, 160, 54, COLORED, False)
  screen_draw_rectangle(frame, 40, 95, 140, 160, UNCOLORED, True)

  #eyes
  screen_draw_circle(frame, 50, 120, 5, COLORED, True)
  screen_draw_circle(frame, 130, 120, 5, COLORED, True)
  screen_display()

def screen_draw_image(frame, image):
  global epd

  frame = epd.get_frame_buffer(image)
  return frame

def screen_draw_ui(frame):
  global epd, count, frame_black, frame_red
  global KEY1, KEY2, KEY3, KEY4, HKEY
  global redraw

  #avoid useless refreshing
  redraw = False

  if ui == Screen.LIVE:
    screen_draw_rectangle(frame, 30, 15, 155, 60, COLORED, False)
    screen_draw_rectangle(frame, 31, 16, 154, 59, COLORED, False)
    screen_draw_text(frame, "TAKE A PHOTO", 35, 20, COLORED, 16)
    screen_draw_text(frame, "AND WAIT", 50, 40, COLORED, 16)
    screen_draw_hline(frame,20, 38, 10, COLORED)
    screen_draw_hline(frame,20, 39, 10, COLORED)
    screen_draw_vline(frame,20, 39, 210, COLORED)
    screen_draw_vline(frame,21, 39, 210, COLORED)

    screen_draw_rectangle(frame, 70, 75, 170, 120, COLORED, False)
    screen_draw_rectangle(frame, 71, 76, 169, 119, COLORED, False)
    screen_draw_text(frame, "BACK TO", 90, 80, COLORED, 16)
    screen_draw_text(frame, "MAIN VIEW", 80, 100, COLORED, 16)
    screen_draw_hline(frame,60, 98, 10, COLORED)
    screen_draw_hline(frame,60, 99, 10, COLORED)
    screen_draw_vline(frame,60, 99, 150, COLORED)
    screen_draw_vline(frame,61, 99, 150, COLORED)

    screen_draw_rectangle(frame, 85, 155, 165, 200, COLORED, False)
    screen_draw_rectangle(frame, 86, 156, 164, 199, COLORED, False)
    screen_draw_text(frame, "GALLERY", 90, 160, COLORED, 16)
    screen_draw_text(frame, "NAVIG.", 100, 180, COLORED, 16)
    screen_draw_vline(frame, 105, 200, 50, COLORED)
    screen_draw_vline(frame, 106, 200, 50, COLORED)
    screen_draw_vline(frame, 150, 200, 50, COLORED)
    screen_draw_vline(frame, 151, 200, 50, COLORED)

    screen_draw_text(frame, "SHOT", 8, 250, COLORED, 13)
    screen_draw_text(frame, "BACK", 50, 250, COLORED, 13)
    screen_draw_text(frame, "NEXT", 95, 250, COLORED, 13)
    screen_draw_text(frame, "PREV", 140, 250, COLORED, 13)

    screen_display()
  elif ui == Screen.GALLERY:
    gallery_init()
    screen_clear()
    if count == 0:
      screen_draw_text(frame, "EMPTY GALLERY", 28, 20, COLORED, 16)
    else:
      if HKEY == KEY3:
        frame_black = screen_draw_image(frame, get_next_image())
      elif HKEY == KEY4:
        frame_black = screen_draw_image(frame, get_prev_image())
    screen_display()

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
    global epd, frame_black, frame_red
    global KEY1, KEY2, KEY3, KEY4, HKEY
    global redraw, ui

    keys_init()
    gallery_init()
    gallery_black("asd.jpg")

    screen_init()
    screen_draw_welcome(frame_black)
    screen_sleep(2000)

    #first ui draw
    redraw = True

    while True:
      #key routine
      if HKEY == KEY1:
        print("SHOT")
      elif HKEY == KEY2:
        print("BACK")
        if ui != Screen.LIVE:
          ui = Screen.LIVE
          redraw = True
      elif HKEY == KEY3:
        print("NEXT");
        ui = Screen.GALLERY
        redraw = True
      elif HKEY == KEY4:
        print("PREV");
        ui = Screen.GALLERY
        redraw = True
      else:
        HKEY = 0

      #refresh ui
      if redraw:
        screen_clear()
        screen_draw_ui(frame_black)

      #clear key
      HKEY = 0

if __name__ == '__main__':
    main()
