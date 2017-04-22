#!/usr/bin/env python

import os
import sys
# MOD from subprocess import Popen
import subprocess
import commands
import simplejson as json

import main as uploader
# here we import the other skripts for subprocessing
import config
import republica_schedule as schedule
import auphonic_upload as uploader

dry_run = False
#debug = False

import HTMLParser
h = HTMLParser.HTMLParser()

####### Case 3: Get the yt upload options
session_id=str(13616) # example ID
event = schedule.get_session_data(session_id)
print 'format metadata for youtube upload:'
metadata = schedule.get_yt_upload_options(event)
# options.category = config.tracks_to_category[event.find('track').text]
prettydata = json.dumps(metadata, ensure_ascii=False ,sort_keys=True, indent=4, separators=(',', ': '))
print prettydata

######## UPLOAD
print 'preparing upload'
filepath = '/Users/bonusjonas/MEINEDATEN/PROJEKTE/2017-051-RP2017/code/youtube-uploads/BlueNotesTribute_HKW.MOV'
credentialspath = 'client_secret.json'
privacy = 'private'
playlist = 'test'
metadataStr = ' --title="'+metadata['title']+\
'" --description="'+metadata['description']+\
'" --category="'+metadata['category']+\
'" --tags="'+metadata['keywords']+\
'" --recording-date="'+metadata['datetime']+\
'" --playlist="'+playlist+\
'" --privacy="'+privacy+\
'" --credentials-file="'+credentialspath+'"'

commandline = 'youtube-upload' + metadataStr + ' '+filepath
#youtube-upload could in fact be loaded as a python module
print commandline
print 'uploading file now'
#subprocess.call(commandline)
#uploader.main(commandline)
#uploader.upload_file(final_file, metadata)
#@echo off
uploader.main(commandline)
#pause
