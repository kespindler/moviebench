#!/usr/bin/env python
# coding: utf-8
import subprocess as sub
import simplejson as json
import string
import urllib2
import os
from time import sleep
join = os.path.join

DATA_DIR = './data'

def send_request(output):
    print "querying google..."
    url = "https://www.google.com/speech-api/v1/recognize?xjerr=1&client=chromium&lang=en-US"
    headers={'Content-Type': 'audio/x-flac; rate='+str(48000), 'User-Agent':'Mozilla/5.0'}
    request = urllib2.Request(url, data=output, headers=headers)
    response = urllib2.urlopen(request)
    text = response.read()
    print 'Received response'
    print text
    command = json.loads(text)
    try:
        utterance = command['hypotheses'][0]['utterance']
    except IndexError:
        print 'Failed to understand audio.'
        utterance = ""
    return utterance


def query_results(data):
    outfile = open('google.txt', 'w')
    for each in data:
        print 'Flacify', each[1]
        flac = flacify(each[0])

        attempts = 0
        utterance = None
        while attempts < 2:
            sleep(1)
            utterance = send_request(flac)
            break
            attempts += 1
        outfile.write((utterance.strip() if utterance else "") + "\n")
    outfile.close()
    print 'Complete.'


def compare_str(str1, str2):
    # remove punctuation
    arr = [str1, str2]
    for i in range(len(arr)):
        arr[i] = arr[i].strip().upper()
        arr[i] = arr[i].translate(string.maketrans("",""), string.punctuation)
    print '\n'.join(arr)
    return arr[0] == arr[1]


def score_results():
    yhat = open('google.txt').readlines()
    y = open(join(DATA_DIR, 'test.txt')).readlines()
    
    correct = sum(compare_str(yhat[i], y[i]) 
            for i in range(len(y)))
    print correct, 'out of', len(y)
    print '%03f' % (correct * 1.0 / len(y), )
