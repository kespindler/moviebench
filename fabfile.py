#!/usr/bin/env python
# coding: utf-8
from fabric.api import *
from moviebench import rip, process


def bootstrap():
    local('mkdir -p data/audio movies tracks')


def rip_tracks(src):
    rip.rip_tracks(src)


def rip_dvd(src):
    rip.rip_dvd(src)


def extract(name):
    process.extract_movie_dialog(name)


def count():
    process.tally_audio_directory()
