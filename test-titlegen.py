#!/usr/bin/env python

import os
import sys
from subprocess import Popen
import commands


import config

import republica_schedule as schedule
import auphonic_upload as uploader

dry_run = False
#debug = False

import HTMLParser
h = HTMLParser.HTMLParser()

#files = [ str(a)+'.mp4' for a in [190]]
files = os.listdir(config.source_dir)

#print files

for index, filename in enumerate(files):

    print '\n'
    session_id = os.path.splitext(filename)[0].split('_')[0]

    #ignore hidden files in this folder
    if session_id[0] == '.':
        continue

    #ignore files with ignore prefix
    if session_id == 'ignore':
        continue

    print "Generating Title for talk:" + session_id

# in the remainder of this scripts an "event" is a talk or or an other session
    # and not the whole conference
    print "fetching meta data from API"
    try:
        event = schedule.get_session_data(session_id);
    except Exception as e:
        print "ERROR:" + " " + str(e)
        continue

    video_path = os.path.join(config.source_dir, filename);

    print 'Title: ' + event['title'].encode('utf-8')
    print 'Path_to_file: ' + str(video_path)

    final_file = os.path.join(config.final_files_uploaded_dir, "{id}.mp4".format(id=session_id))

    if True:
        if os.path.exists(final_file):
            print ' reusing existing final mp4'
        else:
            print ' generating dependencies... '
            sys.stdout.flush()
            title_ts = os.path.join(config.work_dir, "{id}_title.ts".format(id=session_id))
            if not os.path.exists(title_ts):
                speakers = event['speaker_names']
                workpath= os.path.abspath(config.work_dir)
                print workpath
                command = ["sudo", "python", "title_generation.py", "-i", session_id, "-p"] + [h.unescape(x) for x in speakers] + ["-w", workpath, "-b", event['start_iso'], "-d", event['date'], "-t", h.unescape(event['title'])]
                print command
                process = Popen(command)
                returncode = process.wait()
                if returncode != 0:
                    print "returncode %d != 0 for %r" % (returncode, command)
                    continue

    print 'created titles'
