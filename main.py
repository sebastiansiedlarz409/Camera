import epd2in7b
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

COLORED = 1
UNCOLORED = 0

def main():
    epd = epd2in7b.EPD()
    epd.init()

    # clear the frame buffer
    frame_black = [0] * int(epd.width * epd.height / 8)
    frame_red = [0] * int(epd.width * epd.height / 8)

    # For simplicity, the arguments are explicit numerical coordinates
    epd.draw_rectangle(frame_black, 10, 130, 50, 180, COLORED)
    epd.draw_line(frame_black, 10, 130, 50, 180, COLORED)
    epd.draw_line(frame_black, 50, 130, 10, 180, COLORED)
    epd.draw_circle(frame_black, 120, 150, 30, COLORED)
    epd.draw_filled_rectangle(frame_red, 10, 200, 50, 250, COLORED)
    epd.draw_filled_rectangle(frame_red, 0, 76, 176, 96, COLORED)
    epd.draw_filled_circle(frame_red, 120, 220, 30, COLORED)

    # draw strings to the buffer
    font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 18)
    epd.draw_string_at(frame_black, 4, 50, "e-Paper Demo", font, COLORED)
    epd.draw_string_at(frame_red, 18, 80, "Hello world!", font, UNCOLORED)
    # display the frames
    epd.display_frame(frame_black, frame_red)

    # display images
    frame_black = epd.get_frame_buffer(Image.open('black.bmp'))
    frame_red = epd.get_frame_buffer(Image.open('red.bmp'))
    epd.display_frame(frame_black, frame_red)

    # You can get frame buffer from an image or import the buffer directly:
    #epd.display_frame(imagedata.IMAGE_BLACK, imagedata.IMAGE_RED)

if __name__ == '__main__':
    main()
