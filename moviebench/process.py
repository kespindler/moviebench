#!/usr/bin/env python
# coding: utf-8
from __future__ import absolute_import
import os
import subprocess as sub
import re
import os.path as op
from datetime import datetime
import random
import wave
import numpy as np
from moviebench.rip import TRACK_DIR, DATA_DIR, AUDIO_DIR


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
    f = open(op.join(DATA_DIR, 'raw.txt'), 'a')
    for line, wav_data in valid_lines:
        code = '%016x' % random.randrange(16**16)

        fname = op.join(AUDIO_DIR, code + '.wav')
        outwav = wave.open(fname, 'w')
        outwav.setparams(wav.getparams())
        outwav.writeframes(wav_data)

        sub.check_call(['flac', fname])
        os.remove(fname)

        f.write((u'%s,%s,%s\n' % (code, name, line)).encode('utf8'))


def band_pass(signal, lowest=None, highest=None):
    lowest = lowest or 0
    highest = highest or signal.size
    afft = np.fft.fft(signal)
    afft[:lowest] = 0
    afft[highest:] = 0
    filtered = np.fft.ifft(afft)
    real_filtered = np.real(filtered)
    real_filtered /= np.max(np.abs(real_filtered))
    return real_filtered


def amplitude_spikes(signal, window_size=None, spike_threshold=None):
    top_half = np.clip(signal, 0, 1)
    window_size = window_size or 2880
    spike_threshold = spike_threshold or 0.50
    maxed_top_half = top_half.copy()

    for i in range(top_half.size):
        min_i = max(0, i - window_size)
        max_i = min(i + window_size, top_half.size)
        max_value = top_half[min_i:max_i].max()
        maxed_top_half[i] = max_value if top_half[i] == max_value else 0

    maxed_top_half = np.clip(maxed_top_half, spike_threshold, 1)
    where = np.where(maxed_top_half > spike_threshold)
    return where[0]
