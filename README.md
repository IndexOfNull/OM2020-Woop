# OM2020-Woop

![](https://i.imgur.com/jYlKAmU.jpg)

This is the code for a part of my Odyssey of the Mind performance in 2020. This was all put together with the prime intention of making it work, not generating the world's best code. Despite this, there are some cool things, like a custom file format, voice changer, and, of course, a nice LED display.

# Guide

If you want to run this code on your own Woop™, there's some things you're going to want to know. First, you'll want to `pip install pyo pillow keyboard`. Be sure you've also run Adafruits CircuitPython script (otherwise `board` will not be a recognized module). Second, you'll may want ImageMagick installed to split your .GIFs into coalesced frames (using `giftoframes.sh`).

Connect your WS2812B lights to Pin 21 of your RPi3. Also, you'll need a USB microphone and keyboard plugged into the USB ports.

At this point you should be able to run `python3 clock.pyx` and punch some numbers on the number pad to see the animations. In all likelyhood, you will have to tweak the code to get things working.

# What's what

* `animconverter.py` will convert a .gif or directory of frames into a .doom animation

* `perfmanager.py` provided tools specific to the OM performance (like evolving animations, keybinding, etc)

* The `SourceAnimations` directory contains a bunch of PNG frames for animations before they were converted to .doom files.

* The `animations` directory contains converted .doom files.

* The `classes` directory contains relevant code for each component of the system.
    * `voice.py` contains a `pyo` based voice changer. You'll almost certainly have to modify this to use the correct input device should you try to run it yourself.
    * `giftools.py` contains tools for parsing gifs. I don't think I wrote any of it.
    * `display.py` contains the display driver code. On initialization it takes an array of animations and controls which one is displayed.
    * `animation.py` contains logic for encoding/decoding animations into the custom .doom format.