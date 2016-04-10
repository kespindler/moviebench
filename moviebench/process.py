from __future__ import absolute_import
import os
import subprocess as sub
import re
import os.path as op
from datetime import datetime
import random
import wave
from moviebench.rip import TRACK_DIR, DATA_DIR


def calculate_wav_frame(wav, time):
    """Given a timestamp in a wav, give the index into the wav for that timestamp.

    :param wav: wav file
    :param time:
    :return:
    """
    frame_rate = wav.getframerate()
    t = (time.hour * 60 + time.minute) * 60 + time.second + time.microsecond / 1e6
    frame = int(t * frame_rate)
    return frame


def get_dialog_lines_from_movie(name):
    """Given the name of a movie, read the srt and wav from file system, and return
    the dialog lines as (dialog text, wav data) tuples.

    :param name:
    :return:
    """
    with open(op.join(TRACK_DIR, name + '.srt'), 'rU') as f:
        lines = f.readlines()
    wav = wave.open(op.join(TRACK_DIR, name + '.wav'))
    result_lines = []
    i = 0
    while i < len(lines):
        match = re.match('([0-9:,]+) --> ([0-9:,]+)', lines[i])
        if not match:
            i += 1
            continue
        times = [datetime.strptime(stamp, "%H:%M:%S,%f").time()
                 for stamp in match.groups()]
        startframe = calculate_wav_frame(wav, times[0])
        endframe = calculate_wav_frame(wav, times[1])
        wav.setpos(startframe)
        data = wav.readframes(endframe - startframe)

        i += 1
        text = ""
        while lines[i] != "\n":
            text += lines[i]
            i += 1
        text = clean_subtitle(text)
        if text is not None:
            result_lines.append((text, data))
        i += 1
    return result_lines


def write_as_flac(wav_bytes):
    """Given wav bytes (in memory), write to file system as flac file.

    :param wav_bytes:
    :return:
    """
    p = sub.Popen(['flac', '-'], stdout=sub.PIPE, stdin=sub.PIPE, stderr=sub.STDOUT)
    result = p.communicate(input=wav_bytes)[0]
    print result
    return result


def clean_subtitle(text):
    """Given raw data from a srt file, clean it up.

    :param text:
    :return:
    """
    text = text.replace('\n', ' ').strip()
    text = re.sub('\[.*?\]', "", text)
    text = re.sub('\(.*?\)', "", text)
    text = re.sub('\<.*?\>', "", text)
    text = text.decode('utf8')
    text = text.replace(u'♪', u"")
    text = re.sub('^([a-zA-Z]*:)', "", text)
    text = text.strip().upper()
    if ":" in text or not text:
        return None
    return text


def extract_movie_dialog(name):
    valid_lines = get_dialog_lines_from_movie(name)
    wav = wave.open(op.join(TRACK_DIR, name + '.wav'))
    f = open(op.join(DATA_DIR, 'raw.txt'))
    for line, wav_data in valid_lines:
        code = '%016x' % random.randrange(16**16)

        fname = op.join(DATA_DIR, 'audio', code + '.wav')
        outwav = wave.open(fname, 'w')
        outwav.setparams(wav.getparams())
        outwav.writeframes(wav_data)

        sub.check_call(['flac', fname])
        os.remove(fname)

        f.seek(2)
        f.write((u'%s,%s,%s\n' % (code, name, line)).encode('utf8'))


def tally_audio_directory():
    dir_path = op.join(DATA_DIR, 'audio')
    total = 0
    print 'Counting...'
    for fname in os.listdir(dir_path):
        secs = os.system('metaflac --show-total-samples --show-sample-rate ' +
                   op.join(dir_path, fname) + ' ' + '| tr \'\n\' \' \' | awk \'{print $1/$2}\'')
        total += float(secs)
    print '%.1f seconds of audio.' % (total, )
    print '%.1f minutes of audio.' % (total / 60, )
    print '%.2f hours of audio.' % (total / 3600, )
