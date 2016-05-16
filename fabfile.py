#!/usr/bin/env python
# coding: utf-8
from fabric.api import *
from moviebench import rip, process
from moviebench.lib import s3
import os.path as op
import subprocess as sub


def clean():
    local('rm -rf data')


def bootstrap():
    local('mkdir -p data/audio movies tracks')
    local('touch data/raw.txt')


def rip_tracks(src):
    rip.rip_tracks(src)


def rip_dvd(src):
    rip.rip_dvd(src)


def extract(name):
    ripped = (op.exists('tracks/%s.srt' % name) and
              op.exists('tracks/%s.wav' % name))

    if not ripped:
        rip.rip_tracks('movies/%s.mkv' % name)

    process.extract_movie_dialog(name)


def count():
    data.tally_audio_directory()


def check_quality(movie=None):
    filter_func = None
    if movie is not None:
        filter_func = lambda x: x == movie
    data.check_quality(filter_func)


def split_s3_track(name):
    process.split_s3_track(name)


def upload_movie_to_s3(mkv_fpath):
    """Takes path to an mkv and uploads (as srt and flac) to s3.

    :param fpath:
    :return:
    """
    proc = sub.Popen(['ffmpeg', '-i', mkv_fpath], stderr=sub.PIPE, stdout=sub.PIPE)
    out, err = proc.communicate()
    if 'Subtitle' not in err:
        print 'No subtitles found.'
        return
    name, wav_fpath, srt_fpath = rip.rip_tracks(mkv_fpath)
    flac_fpath = op.splitext(wav_fpath)[0] + '.flac'
    sub.check_call(['sox', wav_fpath, flac_fpath])
    s3.upload_tracks(name, flac_fpath, srt_fpath)
