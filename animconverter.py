# © Damien Kazewych 2020
# PREPARE TO MEET YOUR .DOOM*
# *not compatible with any major file format

import argparse
import os
from classes.animation import Animation


parser = argparse.ArgumentParser(description='Convert a GIF into the usable format.')
parser.add_argument('input', help='the input .gif file')
parser.add_argument('--output', '-o', dest='output', help='the output file')
parser.add_argument('--delay', type=int, dest='delay', help='how long each frame should be displayed in ms', default=33)
parser.add_argument("--loop", action="store_true")
parser.add_argument('-t', dest='test', help='attempts to reconstruct the first frame', action="store_true")

args = parser.parse_args()

isdir = os.path.isdir(args.input)

if args.output is None:
    if not isdir:
        args.output = args.input.split("/")[-1:][0].split(".")[0] + ".doom"
    else:
        args.output = args.input.split("/")[-1:][0] + ".doom"

anim = Animation()
if isdir:
    anim.open_dir(args.input)
else:
    anim.open_gif(args.input)
anim.delay = args.delay/1000
anim.loop = args.loop
anim.save_anim_file(args.output)

if args.test:
    anim2 = Animation().read_anim_file(args.output)
    for frame in anim2.raw_frames:
        anim2.construct_image(frame)