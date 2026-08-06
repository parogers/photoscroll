#!/bin/bash

./make_strip.py --width 640 --margin 30 --gutter 15 --dest out.png $* || exit
convert out.png -resample 36 -density 72 -resize "162x" out.ps
lp -d Epson-TM-T88V -o TmtPaperSource=DocFeedNoCut -o TmtPaperReduction=Both out.ps
