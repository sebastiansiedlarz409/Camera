import epd2in7b
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from enum import Enum

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

  #smile
  screen_draw_circle(frame, 90, 160, 55, COLORED, False)
  screen_draw_rectangle(frame, 40, 95, 140, 160, UNCOLORED, True)

  #eyes
  screen_draw_circle(frame, 50, 120, 5, COLORED, True)
  screen_draw_circle(frame, 130, 120, 5, COLORED, True)
  screen_display()

def screen_draw_ui(frame):
  global epd

  if ui == Screen.LIVE:
    screen_draw_text(frame, "TAKE A PHOTO", 35, 20, COLORED, 16)
    screen_draw_text(frame, "AND WAIT", 50, 40, COLORED, 16)

    screen_draw_line(frame, 90, 60, 15, 245, COLORED)
    screen_draw_line(frame, 15, 245, 6, 225, COLORED)
    screen_draw_line(frame, 15, 245, 39, 234, COLORED)

    screen_draw_text(frame, "TRIGGER", 5, 255, COLORED, 10)
    screen_draw_text(frame, "CLEAR", 60, 255, COLORED, 10)
    screen_draw_text(frame, "LEFT", 105, 255, COLORED, 10)
    screen_draw_text(frame, "RIGHT", 145, 255, COLORED, 10)
    screen_display()

#DRAWING


def main():
    global epd, frame_black, frame_red

    screen_init()
    screen_draw_welcome(frame_black)
    screen_sleep(2000)
    screen_clear()
    screen_draw_ui(frame_black)

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
