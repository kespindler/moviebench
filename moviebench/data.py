import os
import subprocess as sub
import os.path as op
from moviebench.rip import AUDIO_DIR, DATA_DIR
from moviebench.process import band_pass, amplitude_spikes
import soundfile as sf
from collections import OrderedDict


def build_subtitle_map(filter_func=None):
    subtitle_path = op.join(DATA_DIR, 'raw.txt')
    subtitle_map = OrderedDict()
    with open(subtitle_path) as f:
        for line in f:
            audio_hash, movie_src, text = line.split(',', 2)
            if filter_func and not filter_func(movie_src):
                continue
            subtitle_map[audio_hash] = text
    return subtitle_map


def check_quality(filter_func=None):
    subtitle_map = build_subtitle_map(filter_func=filter_func)
    for audio_hash, text in subtitle_map.iteritems():
        with sf.SoundFile(op.join(AUDIO_DIR, '%s.flac' % audio_hash)) as w:
            signal = w.read()
        signal = band_pass(signal, 300, 7000)
        spikes = amplitude_spikes(signal)
        num_spikes = spikes.size
        num_words = len(text.split())
        print('%s s:%d w:%d d:%d' % (
            audio_hash, num_spikes, num_words,
            num_spikes - num_words
        ))


def tally_audio_directory():
    dir_path = op.join(DATA_DIR, 'audio')
    total = 0
    print('Counting...')
    for fname in os.listdir(dir_path):
        cmd = ['metaflac', '--show-total-samples', '--show-sample-rate',
               op.join(dir_path, fname)]
        p = sub.Popen(cmd, stdout=sub.PIPE, stdin=sub.PIPE, stderr=sub.STDOUT)
        result, err = p.communicate()
        if p.returncode:
            continue
        frames, framerate = [int(l) for l in result.splitlines()]
        seconds = frames * 1.0 / framerate
        total += seconds
    print '%.1f seconds of audio.' % (total, )
    print '%.1f minutes of audio.' % (total / 60, )
    print '%.2f hours of audio.' % (total / 3600, )
