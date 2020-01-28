#I love spaghetti

"""Caveats

#File format is large
#Memory use is (probably) pretty terrible
#There are no per-frame durations

"""
import signal

from PIL import Image
import sys, os

import multiprocessing
from multiprocessing import Value, Array, Event

from io import BytesIO


try: #See if we're running on a pi or not
  import RPi.GPIO as gpio
  test_environment = False
except (ImportError, RuntimeError):
  test_environment = True

if len(sys.argv) >= 2: 
    if sys.argv[1].lower() in ('-t', '--test', 'test'): test_environment = True

if not test_environment: import board, neopixel, keyboard

#from classes.voice import VoiceProcessor
from classes.display import DisplayAdapter
from classes.animation import Animation

import time

import ctypes

import glob

def test():
    a = Animation()
    a.delay = 0.25
    a.open_dir("d")
    a.save_anim_file("animations/countdown.out")

    b = Animation()
    b.read_anim_file("animations/countdown.out")
    b.construct_image(b.raw_frames[0])
    """a = Animation(width=16, height=16)
    f = Image.open("gc3.jpg")
    a.frames = [f]*10
    a.save_anim_file("test.out")

    b = Animation()
    b.read_anim_file("test.out")
    print(a.raw_frames, "\n\n\n", b.raw_frames)
    #a = Animation().read_anim_file("test.out")
    #print(len(a.raw_frames))"""
    """e = a.encode_frames([f,f])
    print([a.hex() for a in e])
    b = a.decode_frames(e[0])
    print(b[0])
    print(b[1])
    print(b[0] == b[1])

    print(a.decode_anim(b"\xff\x00\xff\x00\xff\x00\x21\x00\xff\xff\x00"))"""
    #with open("file.b", "wb") as f:
    #    f.write(e)
"""test()
a = Animation().read_anim_file("test.out")
print(a.loop)"""

b = Animation().read_anim_file("animations/sign.doom")
c = Animation().read_anim_file("animations/wave.doom")
d = Animation().read_anim_file("animations/faceevil.doom")
e = Animation().read_anim_file("animations/sands.doom")
f = Animation().read_anim_file("animations/bomb.doom")
g = Animation().read_anim_file("animations/wooploading.doom")
h = Animation().read_anim_file("animations/buizel.doom")
a = Animation().read_anim_file("animations/woopidle.doom")


b.loop = True
a.loop = True
c.loop = True
d.loop = True
e.loop = True
f.loop = True
h.loop = True


val = Value('d',0.0)
v = VoiceProcessor(val)
v.start()

anims = [a, b, c, d, e, f, g, h]

display = DisplayAdapter(anims, num_leds=256, pin=board.D21, pixel_order=neopixel.RGB)
display.start()
print("Started display")
#display.play(1)

def cleanup():
    display.stop()
    #v.stop()
    sys.exit(0)

def on_key(key):
    try:
        num = int(key.name)
    except:
        return
    if num < len(anims):
        display.play(num)

if __name__ == "__main__":
    if test_environment:
        display.play(0)
    try:
        while True:
            try:
                keyboard.on_press(on_key)
                keyboard.wait()
            except KeyboardInterrupt:
                print("Interrupting")
                break
            except OSError:
                print("No keyboard!")
                pass
    except KeyboardInterrupt:
        print("Exiting for keyboard interrupt!")
    finally:
        cleanup()


"""
last = None
while True:
    try:
        #print(v1.value)
        for cur in range(4):
          display.play(cur)
          cur += 1
          time.sleep(3)
        #display.stop()
    except KeyboardInterrupt:
        display.stop()
        v.terminate()
        exit()
"""



#print(timeit.timeit(test, number=1))
