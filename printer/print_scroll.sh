#!/bin/bash

SRC=$1

if [ "$SRC" = "" ]; then
    echo "usage: $0 SRC"
    exit 1
fi

convert $SRC -resample 36 -density 72 -resize "162x" out.ps
lp -d Epson-TM-T88V -o TmtPaperSource=DocNoFeedNoCut -o TmtPaperReduction=Both out.ps
