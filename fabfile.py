#!/usr/bin/env python
# coding: utf-8
from fabric.api import *
from moviebench import rip


def bootstrap():
    local('mkdir -p data/audio movies')


def rip_tracks(src):
    rip.rip_tracks(src)


def rip_dvd(src):
    rip.rip_dvd(src)
