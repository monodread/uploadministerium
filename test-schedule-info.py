#!/usr/bin/env python

import os
import sys
from subprocess import Popen
import commands
import simplejson as json

import youtube_upload as upload
# here we import the other skripts for subprocessing
import config
import republica_schedule as schedule
import auphonic_upload as uploader

dry_run = False
#debug = False

import HTMLParser
h = HTMLParser.HTMLParser()

######## GET INPUT
rawIn = raw_input('Enter Type (session/person/all/yt-options): ')
def containsAll(str, set):
    for c in set:
        if c not in str: return 0;
    return 1;
if rawIn == 'session' or rawIn == '1':
    test = 0
if rawIn == 'person' or rawIn == '2':
    test = 1
if rawIn == 'all' or rawIn == '3':
    test = 2
if rawIn == 'yt-options' or rawIn == '4':
    test = 3

if test==0:
######### TEST 1: Get the talk info from RP Website!
    # get the session ID from commandline
    session_id = raw_input('Enter talk ID: ')
    if len(session_id) == 0:
        session_id=str(13616)
        print 'None given, using: ' + session_id

    print "fetching meta data from API:"+session_id
    event = schedule.get_session_data(session_id)

    print "Title of Talk is: "
    print event['title'].encode('utf-8')

    # FOR DEBUG
    prettyevent = json.dumps(event, ensure_ascii=False ,sort_keys=True, indent=4, separators=(',', ': '))
    print prettyevent

if test==1:
######## TEST 2: Get the speaker info from RP Website!
    person_id = raw_input('Enter Person ID: ')
    if len(person_id) == 0:
        person_id = str(2219)
        print 'None given, using: ' + person_id

    print "fetching speaker data from API:"+person_id
    person = schedule.get_person_data(person_id)

    print "Speaker Name is: "
    print person['name']
    prettydata = json.dumps(person, ensure_ascii=False ,sort_keys=True, indent=4, separators=(',', ': '))
    #print prettydata
    ####
    for i,x in enumerate(person['links']):
        print i
        word = 'twitter'
        for k,v in x.items():
            if k == 'url':
                if word in v:
                    print "%s=%s" % (k, v)

    #####

if test==2:
    ########## TEST 3: Get complete Json info
    print 'calling the rp webiste for all session info:'
    jsondata = schedule.get_all_sessions(config.event_id)
    print 'Found '+str(len(jsondata))+' entries: '
    # Generate a list of ...
    allspeakers = [e['speaker_names'][0].encode('utf-8') for i, e in enumerate(jsondata)]
    alltitles = [e['title'] for i, e in enumerate(jsondata)]
    l1,l2 = [len(e) for i,e in enumerate(allspeakers)] , [len(e) for i,e in enumerate(alltitles)]
    #print l1, l2
    print "Longest Speaker Name : ", max(l1)
    print "Longest Session Title : ", max(l2)

    #for i, e in enumerate(jsondata):
        # print i, e['nid']
        # nid = e['nid']
        #allnames = allnames.append(e['title'])
        #allspeakers[nid] = e['speaker_names'][0]
    #print allnames

if test==3:
####### TEST 3: Get the yt upload options
    session_id = raw_input('Enter Session ID: ')
    if len(session_id) == 0:
        session_id = str(13616)
    print 'Using: ' + session_id

    event = schedule.get_session_data(session_id)
    print 'format metadata for youtube upload:'
    metadata = schedule.get_yt_upload_options(event)
    # options.category = config.tracks_to_category[event.find('track').text]
    prettydata = json.dumps(metadata, ensure_ascii=False ,sort_keys=True, indent=4, separators=(',\n', ': '))
    print prettydata
