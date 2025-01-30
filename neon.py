import time
import board
import displayio
import framebufferio
import rgbmatrix
import terminalio
import json
import urllib.request
import vectorio
from adafruit_display_text import label

displayio.release_displays()
matrix = rgbmatrix.RGBMatrix(
    width=64, height=32, bit_depth=4,
    rgb_pins=[board.D6, board.D5, board.D9, board.D11, board.D10, board.D12],
    addr_pins=[board.A5, board.A4, board.A3, board.A2],
    clock_pin=board.D13, latch_pin=board.D0, output_enable_pin=board.D1
)
display = framebufferio.FramebufferDisplay(matrix, auto_refresh=True)
main_group = displayio.Group()

border_color = 0xFFFFFF
border_thickness = 1
border_palette = displayio.Palette(1)
border_palette[0] = border_color

top_border = vectorio.Rectangle(pixel_shader=border_palette, width=64, height=border_thickness, x=0, y=0)
bottom_border = vectorio.Rectangle(pixel_shader=border_palette, width=64, height=border_thickness, x=0, y=31)
left_border = vectorio.Rectangle(pixel_shader=border_palette, width=border_thickness, height=32, x=0, y=0)
right_border = vectorio.Rectangle(pixel_shader=border_palette, width=border_thickness, height=32, x=63, y=0)

border_group = displayio.Group()
border_group.append(top_border)
border_group.append(bottom_border)
border_group.append(left_border)
border_group.append(right_border)
main_group.append(border_group)

CHANNEL_ID = "CHANNEL_ID"
API_KEY = "YOUTUBE_API_V3"
API_URL = f"https://www.googleapis.com/youtube/v3/channels?part=statistics,snippet&id={CHANNEL_ID}&key={API_KEY}"

channel_name_label = label.Label(terminalio.FONT, text="Loading...", color=0xFFFFFF, x=2, y=5)
views_label = label.Label(terminalio.FONT, text="V ...", color=0x00FFFF, x=2, y=15)
subs_label = label.Label(terminalio.FONT, text="S ...", color=0xFF0000, x=2, y=25)

main_group.append(channel_name_label)
main_group.append(views_label)
main_group.append(subs_label)
display.root_group = main_group

def get_youtube_stats():
    try:
        response = urllib.request.urlopen(API_URL)
        data = json.loads(response.read().decode())

        if 'items' in data and len(data['items']) > 0:
            stats = data['items'][0]['statistics']
            snippet = data['items'][0]['snippet']
            view_count = stats['viewCount']
            sub_count = stats['subscriberCount']
            channel_name = snippet['title']
            return channel_name, view_count, sub_count
    except Exception:
        pass
    return "Error", "Error", "Error"

def format_number(num):
    try:
        num = int(num)
        if num >= 1_000_000:
            return f"{num/1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num/1_000:.1f}K"
        return str(num)
    except:
        return num

def scroll_text():
    text_width = len(channel_name_label.text) * 6
    start_x = 64
    end_x = -text_width
    while True:
        channel_name_label.x = start_x
        while channel_name_label.x > end_x:
            channel_name_label.x -= 1
            time.sleep(0.1)

while True:
    try:
        channel_name, views, subs = get_youtube_stats()

        channel_name_label.text = f"{channel_name}"
        views_label.text = f"V: {format_number(views)}"
        subs_label.text = f"S: {format_number(subs)}"
        scroll_text()
    except:
        channel_name_label.text = "Error"
        views_label.text = "V: ..."
        subs_label.text = "S: ..."
        time.sleep(5)
