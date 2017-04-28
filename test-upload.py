#!/usr/bin/env python

import os
import sys
# MOD from subprocess import Popen
import subprocess
import commands
import simplejson as json

#import main as uploader
# here we import the other skripts for subprocessing
import config
import republica_schedule as schedule
#import auphonic_upload as uploader
import youtube_upload as uploader

dry_run = False
#debug = False

import HTMLParser
h = HTMLParser.HTMLParser()

#Get the yt upload options for session by id
session_id = raw_input('Enter talk ID: ')
if len(session_id) == 0:
    session_id=str(13616)
    print 'None given, using: ' + session_id

event = schedule.get_session_data(session_id)
print 'format metadata for youtube upload:'
metadata = schedule.get_yt_upload_options(event)
# options.category = config.tracks_to_category[event.find('track').text]
prettydata = json.dumps(metadata, ensure_ascii=False ,sort_keys=True, indent=4, separators=(',', ': '))
# print prettydata

######## UPLOAD
print 'starting upload with youtube-uploader'
if uploader.upload_file(None, metadata):
    print "upload successful"
else:
    print "upload failed"

print "\nTest finished"

"""
# static file for test here!!
credentialspath = config.ytcredentialspath
filepath = config.ytfilepath
privacy = 'private'
playlist = 'rp17test'
# Version1: create a complete string for subprocess call
metadataStr = ' --title="'+metadata['title']+\
'" --description="'+metadata['description']+\
'" --tags="'+metadata['keywords']+\
'" --playlist="'+playlist+\
'" --privacy="'+privacy+\
'" --recording-date="'+metadata['datetime']+\
'" --category="'+metadata['category']+\
'" --client-secrets="'+credentialspath+'"'

commandline = 'youtube-upload' + metadataStr +' '+filepath
print commandline

print 'starting upload now'
# THIS THROWS ERROR: FILENAME too long, when not setting shell to True!
process = subprocess.check_call(commandline, shell=True)
print 'Finished'
"""
