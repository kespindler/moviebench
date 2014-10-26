#!/usr/bin/env python
# coding: utf-8
from fabric.api import local as run, task
import subprocess as sub
import argparse
import os
import re
from datetime import datetime
import wave
import random
from lib import dataset

DATA_DIR = 'data'
MOVIE_DIR = 'movies'

join = os.path.join


@task
def ripdvd(src):
    """Input: DVD
    Output: mkv"""
    name = os.path.basename(os.path.normpath(src))
    cmd = 'HandBrakeCLI --scan -i'.split() + [src]
    handbrake = sub.Popen(cmd, stderr=sub.PIPE)
    _, out = handbrake.communicate()
    result = re.search('(\d).*\(Text\)', out) # find track with closed captioning
    if result is None:
        print "Failed to find Text subtitles. Exiting..."
        return
    cctrack = str(result.group(1))
    output = join(MOVIE_DIR, name + ".mkv")
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


@task
def process(src):
    """Input: mkv
    Output: Audio files written and test/train written"""
    wav, srt = riptracks(src)
    process_wav(wav)


def riptracks(src):
    name = os.path.splitext(os.path.basename(src))[0]
    srt = join(DATA_DIR, 'rips', name+".srt")
    cmd2 = "ffmpeg -i %s -vn -an -c:s:0 srt %s" % (src, srt)
    print cmd2
    os.system(cmd2)
    
    wav = join(DATA_DIR, 'rips', name+".wav")
    cmd3 = "ffmpeg -i %s -ac 1 %s" % (src, wav)
    print cmd3
    os.system(cmd3)
    return wav, srt


def calcframe(wav, time):
    framerate = wav.getframerate()
    t = (time.hour * 60 + time.minute) * 60 + time.second + time.microsecond / 1e6
    frame = int(t * framerate)
    return frame


def clean_subtitle(text):
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


def flacify(wav_bytes):
    p = sub.Popen(['flac', '-'], stdout=sub.PIPE, stdin=sub.PIPE, stderr=sub.STDOUT)
    result = p.communicate(input=wav_bytes)[0]
    print result
    return result


def get_lines(name):
    with open(join(DATA_DIR, 'rips', name + '.srt'), 'rU') as f:
        lines = f.readlines()
    wav = wave.open(join(DATA_DIR, 'rips', name + '.wav'))
    result_lines = []
    i = 0
    while i < len(lines):
        match = re.match('([0-9:,]+) --> ([0-9:,]+)', lines[i])
        if not match:
            i += 1
            continue
        times = [datetime.strptime(stamp, "%H:%M:%S,%f").time()
                 for stamp in match.groups()]
        startframe = calcframe(wav, times[0])
        endframe = calcframe(wav, times[1])
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


def process_wav(src):
    name = os.path.splitext(os.path.basename(src))[0]
    movie_f = open(join(DATA_DIR, 'rips', name + '.txt'), 'w')
    valid_lines = get_lines(name)
    wav = wave.open(join(DATA_DIR, 'rips', name + '.wav'))
    test_f = open(join(DATA_DIR, 'test.txt'), 'a')
    train_f = open(join(DATA_DIR, 'train.txt'), 'a')
    for line, wav_data in valid_lines:
        code = '%016x' % random.randrange(16**16)

        fname = join(DATA_DIR, 'audio', code + '.wav')
        outwav = wave.open(fname, 'w')
        outwav.setparams(wav.getparams())
        outwav.writeframes(wav_data)

        sub.check_call(['flac', fname])
        #flac = flacify(wav_data)
        #fpath = join(DATA_DIR, 'audio', code + '.flac')
        #with open(fpath, 'w') as flac_f:
        #   flac_f.write(flac)
        os.remove(fname)

        if random.random() > .9:
            f = test_f
        else:
            f = train_f
        f.seek(2)
        f.write((u'%s,%s\n' % (code, line)).encode('utf8'))
        movie_f.write(code + '\n')

@task
def benchmark_google():
    from lib import googlespeech as google
    _, test = dataset.load_data()
    google.query_results(test)
    google.score_results()
    

@task
def clean():
    run('rm data/audio/*')
    run('echo -n > data/train.txt')
    run('echo -n > data/test.txt')



