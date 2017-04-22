#!/usr/bin/env python

import os
import sys
from subprocess import Popen
import commands

# here we import the other skripts for subprocessing
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
    print session_id

    #ignore hidden files in this folder
    print "checking files in folder"
    try:
        if session_id[0] == '.':
            continue
    except Exception as e:
        print "ERROR: Found no files:" + str(e)

    #ignore files with ignore prefix
    if session_id == 'ignore':
        continue


    print "Processing talk:" + session_id



# in the remainder of this scripts an "event" is a talk or or an other session
    # and not the whole conference
    print "fetching meta data from API"
    try:
        event = schedule.get_session_data(session_id);
    except Exception as e:
        print "ERROR:" + " " + str(e)
        continue #TODO why do we continue here?

    video_path = os.path.join(config.source_dir, filename);

    print "DEBUG"

    print event['title'].encode('utf-8')
    print video_path

    final_file = os.path.join(config.final_files_uploaded_dir, "{id}.mp4".format(id=session_id))


    if True:
        if os.path.exists(final_file):
            print ' reusing existing final mp4'
        else:
            print ' generating dependencies... '
            sys.stdout.flush()
            #
            title_ts = os.path.join(config.work_dir, "{id}_title.ts".format(id=session_id))
            if not os.path.exists(title_ts):
                speakers = event['speaker_names'].split(", ")
                command = ["python", "title_generation.py", "-i", session_id, "-p"] + [h.unescape(x) for x in speakers] + ["-b", event['start'], "-d", event['date'], "-t", h.unescape(event['title'])]
                #print command
                process = Popen(command)
                returncode = process.wait()
                if returncode != 0:
                    print "returncode %d != 0 for %r" % (returncode, command)
                    continue

    # convert input video to ts
            sys.stdout.write(' converting input video to transport stream... ')
            sys.stdout.flush()
            command = "ffmpeg -y -v warning -nostdin -i '{video_path}' -c copy -bsf:v h264_mp4toannexb -f mpegts {id}.ts".format(id=session_id, video_path=video_path)
            #print command
            returncode =  commands.getstatusoutput(command)
            if returncode[0] != 0:
                print "\n returncode %d != 0 for %r" % (returncode[0], command)
                print returncode[1]
                continue
            print 'done'
            #sys.stdout.flush()


    # concatenate all videos
            sys.stdout.write(' concatenate all parts to {target}... '.format(target=final_file))
            sys.stdout.flush()
            command = 'ffmpeg -y -v warning -nostdin -i \"concat:intro.ts|{title_ts}|{id}.ts|outro.ts\" -c copy -bsf:a aac_adtstoasc {out}'.format(id=session_id,title_ts=title_ts,out=final_file)
            #if debug:
            #print command
            returncode =  commands.getstatusoutput(command)
            if returncode[0] != 0:
                print "returncode %d != 0 for %r" % (returncode[0], command)
                print returncode[1]
                continue
            print 'done'
            sys.stdout.flush()

            sys.stdout.write(' removing temporary files... ')
            commands.getstatusoutput("rm " + session_id + "*.ts")
            print 'done'

    print ' upload final file to auphonic'
    metadata = schedule.get_yt_upload_options(event)
   # options.category = config.tracks_to_category[event.find('track').text]

    if uploader.upload_file(final_file, metadata):
        # upload succuesfl: move file from cut to done
        os.rename(video_path, os.path.join(config.source_files_uploaded_dir, filename))
    else:
        print "upload failed"

    print ' done'
