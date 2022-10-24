#!/bin/bash
#ImageMagick must be installed
convert $1 -coalesce "frames/frame_%02d.png"

if [ "$2" != "" ]; then
    python3 animconverter.py frames --output frames.doom --delay "$2"
fi