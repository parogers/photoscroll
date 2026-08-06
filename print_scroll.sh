#!/bin/bash

./process.py $* || exit
convert out.png -resample 18 -density 72 -resize "162x" out.ps
lp -d Epson-TM-T88V -o TmtPaperSource=DocFeedNoCut -o TmtPaperReduction=Both out.ps
