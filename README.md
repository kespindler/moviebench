
# Contribute Data

First, rip a DVD (DVD -> mkv)

    # Put the DVD in
    fab rip_dvd:$DVD_PATH

Second, convert the mkv into a tracks file

    fab rip_tracks:$MKV_PATH

Lastly, process the movie. Provide the name of the srt/wav/mkv file, without the file ending.

    fab process_tracks:$MOVIE_NAME

# Data Structure

    moviebench/
    movies/   # DVDs are ripped into mkv here
        movie.mkv
    tracks/   # mkv are ripped into tracks here
        movie.wav
        movie.srt
    data/     # compile mkv into data
        raw.txt
        audio/
            1.flac
            2.flac
