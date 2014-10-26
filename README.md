# Structure

## Data directory

data/
    test.txt
    train.txt
    audio/      
        1.flac
        2.flac
    rips/
        movie.wav
        movie.srt
        movie.txt

## Files

{test,train}.txt

<sample number>,<line from movie or blank>

<movie>.txt
<sample number>

# Workflows

## Rip a DVD

1. Put the DVD in
2. fab ripdvd:"<path-to-movie>"

## Rip a .mkv

1. Put the movie in movies/
2. fab process:"Movie"

## Rip all non-processed movies

1. Put all movies in movies/
2. fab batch

## Run test/train assignment

1. fab assign

