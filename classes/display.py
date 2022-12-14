
#© Damien Kazewych 2020

"""
Is this a game, or is it real?

WHAT'S THE DIFFERENCE?

~ War Games (1983)
"""


import multiprocessing
from multiprocessing import Value
import time

try: #See if we're running on a pi or not and print a funny message
  import RPi.GPIO as gpio
  test_environment = False
except (ImportError, RuntimeError):
  test_environment = True
  print("Why would you do this to me!?")

if not test_environment: import board, neopixel

class DisplayAdapter(multiprocessing.Process):

    def __init__(self, animations, **kwargs):
        super(DisplayAdapter, self).__init__()
        self.daemon = True
        self._terminated = Value('b', False)
        self.animations = animations
        self.current_anim_index = Value('i', 0) #Index in anims array to play
        #self.current_anim = self.animations[self.current_anim_index.value]
        self.current_frame = Value('i', 0) #Position within animation
        self.is_playing = Value('b', False)
        self.width = kwargs.pop('width', self.animations[0].image_width)
        self.height = kwargs.pop('height', self.animations[0].image_height)
        self.pixels = None
        self.last_frame = None
        self.display_pin = kwargs.pop("pin", board.D12)
        self.num_leds = kwargs.pop("num_leds")
        self.auto_write = kwargs.pop("auto_write", False)
        self.pixel_order = kwargs.pop("pixel_order", neopixel.GRB)
        self.pixels = neopixel.NeoPixel(self.display_pin, self.num_leds, auto_write=self.auto_write, pixel_order=self.pixel_order)
        #self.width = self.height = 16

    @property
    def current_anim(self):
        return self.animations[self.current_anim_index.value]

    def run(self):

        while not self._terminated.value:
            if not self.is_playing.value:
                time.sleep(0.25)
                continue
            #display it
            frame = self.current_frame.value
            anim = self.current_anim #Do this so that we don't cause a situation where we update the animation and start it too late
            animindex = self.current_anim_index.value
            if frame == len(anim.raw_frames):
                if self.current_anim.loop:
                    self.current_frame.value = frame = 0
                else:
                    self.stop_anim()
                    continue #Move to the next loop so we hang on that first wait loop
            #print(len(self.current_anim.raw_frames))
            #print(frame)
            millis = int(round(time.time() * 1000))
            for y in range(self.height):
                for x in range(self.width):
                    #Convert x and y into index. Based on cascade from left to right
                   
                    if (y+1) % 2 == 1: #even, lines 1,3,5,etc.
                        pindex = x + (y * self.width)
                    else: #even, lines 2,4,6,etc.
                        pindex = (y * self.width) + (self.width - 1 - x)

                    cindex = y*self.width + x

                    curframe = anim.raw_frames[frame]
                    color = curframe[cindex]
                    #self.pixels[pindex-1] = [int(x * (self.current_anim.brightness/255)) for x in color]
                    self.pixels[pindex] = color #[int(x * 0.02) for x in color] #brightness control
            self.pixels.show()
            #diff = int(round(time.time() * 1000)) - millis
            diff = 0
            if self.is_playing.value:
                sleeptime = anim.delay - (diff/1000)
                mstimes = int(sleeptime * 1000)
                if sleeptime >= 0:
                    for i in range(mstimes):
                        if not self.is_playing.value or animindex != self.current_anim_index.value:
                            break
                        time.sleep(0.001)
                if animindex == self.current_anim_index.value: self.current_frame.value += 1

    def play(self, anim_ind=0):
        if self.is_playing.value == True:
            self.stop_anim()
        self.current_anim_index.value = anim_ind
        self.current_frame.value = 0
        self.is_playing.value = True

    def pause(self):
        self.is_playing.value = False

    def stop_anim(self, *, clear=False):
        self.is_playing.value = False
        self.current_frame.value = 0
        if clear:
            for p in range(len(self.pixels)):
                self.pixels[p] = (0,0,0)
            self.pixels.show()

    def stop(self):
        self.is_playing = False
        self._terminated.value = True
        for p in range(len(self.pixels)):
            self.pixels[p] = (0,0,0)
        self.pixels.show()
