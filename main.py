import epd2in7b
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from enum import Enum
import os
import RPi.GPIO as GPIO

#GALLERY
gallery_path = "GALLERY/black"
index = 0
count = 0
gallery = []

def gallery_init():
  global gallery_path, gallery, count, index
  gallery = os.listdir(gallery_path)
  count = len(gallery)
  index = 0

def get_next_image():
  global gallery_path, gallery, index, count

  if count == 0: return None

  image = Image.open(gallery_path + "/" + gallery[index])
  index += 1

  if index >= count: index = 0

  return image

def get_prev_image():
  global gallery_path, gallery, index, count

  if count == 0: return None

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

ui = Screen.GALLERY

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

  if ui == Screen.LIVE:
    screen_draw_text(frame, "TAKE A PHOTO", 35, 20, COLORED, 16)
    screen_draw_text(frame, "AND WAIT", 50, 40, COLORED, 16)

    screen_draw_line(frame, 90, 60, 15, 245, COLORED)
    screen_draw_line(frame, 89, 60, 14, 245, COLORED)
    screen_draw_line(frame, 15, 245, 6, 225, COLORED)
    screen_draw_line(frame, 15, 245, 39, 234, COLORED)

    screen_draw_text(frame, "TRIGGER", 5, 255, COLORED, 10)
    screen_draw_text(frame, "CLEAR", 60, 255, COLORED, 10)
    screen_draw_text(frame, "LEFT", 105, 255, COLORED, 10)
    screen_draw_text(frame, "RIGHT", 145, 255, COLORED, 10)
    screen_display()
  elif ui == Screen.GALLERY:
    gallery_init()
    screen_clear()
    if count == 0:
      screen_draw_text(frame, "EMPTY GALLERY", 28, 20, COLORED, 16)
    else:
      frame_black = screen_draw_image(frame, get_next_image())
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

    keys_init()
    gallery_init()

    screen_init()
    screen_draw_welcome(frame_black)
    screen_sleep(2000)
    screen_clear()
    screen_draw_ui(frame_black)

    while True:
      #key routine
      if HKEY == KEY1:
        print("TRIGGER")
        HKEY = 0
      elif HKEY == KEY2:
        print("CLEAR")
        HKEY = 0
      elif HKEY == KEY3:
        print("NEXT");
        HKEY = 0
      elif HKEY == KEY4:
        print("PREV");
        HKEY = 0
      else:
        HKEY = 0

    # For simplicity, the arguments are explicit numerical coordinates
    #epd.draw_rectangle(frame_black, 10, 130, 50, 180, COLORED)
    #epd.draw_line(frame_black, 10, 130, 50, 180, COLORED)
    #epd.draw_line(frame_black, 50, 130, 10, 180, COLORED)
    #epd.draw_circle(frame_black, 120, 150, 30, COLORED)
    #epd.draw_filled_rectangle(frame_red, 10, 200, 50, 250, COLORED)
    #epd.draw_filled_rectangle(frame_red, 0, 76, 176, 96, COLORED)
    #epd.draw_filled_circle(frame_red, 120, 220, 30, COLORED)

    # draw strings to the buffer
    #font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 18)
    #epd.draw_string_at(frame_black, 4, 50, "e-Paper Demo", font, COLORED)
    #epd.draw_string_at(frame_red, 18, 80, "Hello world!", font, UNCOLORED)
    # display the frames
    #epd.display_frame(frame_black, frame_red)

    # display images
    #frame_black = epd.get_frame_buffer(Image.open('black.bmp'))
    #frame_red = epd.get_frame_buffer(Image.open('red.bmp'))
    #epd.display_frame(frame_black, frame_red)

    # You can get frame buffer from an image or import the buffer directly:
    #epd.display_frame(imagedata.IMAGE_BLACK, imagedata.IMAGE_RED)

if __name__ == '__main__':
    main()
