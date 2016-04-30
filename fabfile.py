#!/usr/bin/env python
# coding: utf-8
from fabric.api import *
from moviebench import rip, process, data
import os.path as op


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

