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

from classes.voice import VoiceProcessor
from classes.display import DisplayAdapter
from classes.animation import Animation

import numpy as np

import time

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

"""b = Animation().read_anim_file("animations/sign.doom")
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
h.loop = True"""


val = Value('d',0.0)
v = VoiceProcessor(val)
v.start()

#anims = [a, b, c, d, e, f, g, h]






current_milli_time = lambda: int(round(time.time() * 1000))
class AnimationPerformanceManager(): #because a person pushing a button every minute isn't really a timer

    def __init__(self, **adapteropts):
        self.adapter_options = adapteropts
        self.current_anim = None
        self.animations = []
        self.adapter = None
        self.named_animations = {}
        self.keybinds = {}
        self.timeline_keybinds = {}
        self.timelines = {}
        #{"timeline1": [[anim1,anim2],[10000,15000],]}
        self.timeline_playing = None
        self.time_started = None
        self.timer_started = False
        keyboard.on_press(self.on_key)

    def start_timer(self):
        self.time_started = current_milli_time()
        self.timer_started = True

    def change_animation(self, animid):
        self.current_anim = animid
        self.timeline_playing = None
        self.adapter.play(animid)
        
    def get_timeline_animind(self, timeline):
        ind = self.timelines[timeline]['cur_ind']
        anim_name = self.timelines[timeline]['anims'][ind]
        anim_ind = self.named_animations[anim_name]
        return anim_ind
    
    def play_timeline(self, name):
        anim_ind = self.get_timeline_animind(name)
        self.adapter.play(anim_ind)
        print("now playing", anim_ind)
        self.current_anim = anim_ind
        self.timeline_playing = name

    def add_animation(self, anim, name, **kwargs):
        key = kwargs.pop("key", None)
        self.animations.append(anim)
        index = len(self.animations) - 1 
        print(name, index)
        self.named_animations[name] = index #
        if key:
            self.keybinds[key] = index

    def add_timeline(self, anims, times, name, **kwargs):
        key = kwargs.pop("key", None)
        times = list(np.cumsum(times))
        self.timelines[name] = {"anims": anims, "times": times, "cur_ind": 0, "done": False}
        if key:
            self.timeline_keybinds[key] = name

    def on_key(self, key):
        key = key.name
        if key == "y": self.start_timer()
        try:
            if key in self.keybinds:
                self.change_animation(self.keybinds[key]) 
            elif key in self.timeline_keybinds:
                self.play_timeline(self.timeline_keybinds[key])
        except Exception as e:
            print("ERROR:",e)

    def run_program(self):
        self.adapter = DisplayAdapter(self.animations, **self.adapter_options)
        self.adapter.start()
        while True:
            if not self.timer_started: continue
            for name, timeline in self.timelines.items():
                if timeline['done'] == True: continue
                cur_ind = timeline['cur_ind']
                if current_milli_time() > timeline['times'][cur_ind] + self.time_started:
                    cur_ind += 1
                    if cur_ind >= len(timeline['times']):
                        self.timelines[name]['done'] = True
                        continue
                    self.timelines[name]['cur_ind'] = cur_ind
                    if self.timeline_playing == name:
                        anim_ind = self.get_timeline_animind(name)
                        self.adapter.play(anim_ind)
                        self.current_anim = anim_ind

    def cleanup(self):
        self.adapter.stop()

if __name__ == "__main__":
    a1 = Animation().read_anim_file("animations/sign.doom")
    a2 = Animation().read_anim_file("animations/wooploading.doom")
    a3 = Animation().read_anim_file("animations/woopidle.doom")

    a1.loop = True
    a2.loop = True
    a3.loop = True

    man = AnimationPerformanceManager(num_leds=256, pin=board.D21, pixel_order=neopixel.RGB)
    man.add_animation(a1, "sign", key="0")
    man.add_animation(a2, "loading", key="1")
    man.add_animation(a3, "woopidle", key="2")
    man.add_timeline(["sign", "loading", "woopidle"], [10000, 10000, 10000], "testtl", key="b")
    try:
        man.run_program()
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
    finally:
        man.cleanup()
        v.stop()
        exit()
