import os
import subprocess as sub
import re
import os.path as op

MOVIE_DIR = 'movies'
DATA_DIR = 'data'
TRACK_DIR = 'tracks'


def rip_dvd(src):
    """
    Given a DVD file path, use HandBrakeCLI to rip the DVD into an MKV file.

    :param src:
    :return:
    """
    name = os.path.basename(os.path.normpath(src))
    cmd = ['HandBrakeCLI', '--scan', '-i', src]
    handbrake = sub.Popen(cmd, stderr=sub.PIPE)
    _, out = handbrake.communicate()
    result = re.search('(\d).*\(Text\)', out) # find track with closed captioning
    if result is None:
        print "Failed to find Text subtitles. Exiting..."
        return
    cctrack = str(result.group(1))
    output = op.join(MOVIE_DIR, name + ".mkv")
    try:
        os.remove(output)
    except:
        pass
    cmd = ["HandBrakeCLI", "--preset", '"High Profile"', '--subtitle',
           cctrack, "-i", src, "-o", output]
    cmd = ' '.join(cmd)
    print cmd
    os.system(cmd)
    return output


def rip_tracks(src):
    """Given an mkv src file, rip out the srt and the wav tracks.

    :param src:
    :return:
    """
    assert src.endswith('.mkv')
    name = os.path.splitext(os.path.basename(src))[0]
    srt = op.join(TRACK_DIR, name+".srt")
    cmd2 = "ffmpeg -i %s -vn -an -c:s:0 srt %s" % (src, srt)
    print cmd2
    os.system(cmd2)

    wav = op.join(TRACK_DIR, name+".wav")
    cmd3 = "ffmpeg -i %s -ac 1 %s" % (src, wav)
    print cmd3
    os.system(cmd3)
    return wav, srt
