#!/usr/bin/env python
#    Copyright (C) 2011  derpeter
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

# workround to run this script on Mac OS X
#inkscape = '/Applications/Inkscape.app/Contents/Resources/bin/inkscape-bin'
inkscape = '/Applications/Inkscape.app/Contents/Resources/script'

import argparse
import fileinput
import commands
import sys
import os
import re

parser = argparse.ArgumentParser(description='Generate prerole file: make sure you have avconv and inkscape in $PATH')
parser.add_argument('-f', action="store", dest="background", help="background SVG. Default title.svg", default='title.svg' )
parser.add_argument('-t', action="store", dest="title", help="talk title")
parser.add_argument('-s', action="store", dest="subtitle", help="talk subtitle")
parser.add_argument('-p', action="store", dest="speakers", help="person(s). Persons are separated with a blank.", nargs="+")
parser.add_argument('-d', action="store", dest="date", help="date of the talk")
parser.add_argument('-b', action="store", dest="begin", help="begin of the talk")
parser.add_argument('-i', action="store", dest="id", help="talk id")
parser.add_argument('-o', action="store", dest="output", help="output dir", default='./')
parser.add_argument('-w', action="store", dest="workdir", help="working dir", default='./')
#parser.add_argument('--force', action="store_true", default=False, dest="force", help="ignore waring message about var length") # not yet implemented

args = parser.parse_args()
output=[]

# line lengths
line_len_speaker = 25
line_len_title = 35
# was 30, but we need to stretch it for longer titles (and we have 3 lines)
line_len_subtitle = 50

# replace the string in a given svg
def build_svg():

    #check the inputs fields
    if args.id == None:
        print "id not defined"
        sys.exit(1)
    if args.title == None:
        print "title not defined"
        sys.exit(1)
    if len(args.title) > (line_len_title*3):
        print "title too long, " + str(len(args.title)) + 'chars'
        sys.exit(1)
    if args.subtitle == None:
        # republica has no subtitles --Andi
        #print "subtitle not defined"
        args.subtitle = ''
    if len(args.subtitle) > (line_len_subtitle*2):
        print "subtitle to long"
        sys.exit(1)
    if args.speakers == None:
        print "WARNING: person not defined"
        #sys.exit(1)
    if args.date == None:
        print "date not defined"
        args.date=''
    if args.begin == None:
        print "begin not defined"
        args.begin = ''

    # build the speaker name list
    # show what the title is
        #for i, name in enumerate(args.title):
        #    temp = '\n'.join([str(item) for item in args.speakers])
        #print "Speakernames: " + temp
    #print "Titel = " + args.title
    print "Titellaenge= " + str(len(args.title)) + ' chars von ' + str(3*line_len_title)

    # show the speakers
    for i, name in enumerate(args.speakers):
        temp = ', '.join([str(item) for item in args.speakers])
    print 'Found ' + str(len(args.speakers)) + ' Speaker(s): ' + temp
    #for name in args.speakers:
    #    print len(name)
    #    print "total char length= " +

    # split title into two lines if necessary
    if len(args.title) > line_len_title:
        titleRE = re.compile(r'^(.{0,'+str(line_len_title)+r'}) (.{0,'+str(line_len_title)+r'})(?: (.*))?$')
        titles = titleRE.search(args.title).groups()
        title1 = titles[0]
        title2 = titles[1] or ''
        title3 = titles[2] or ''
        if len(title3) > line_len_title:
            print "title too long (2nd line) by " +  str(len(title3) - line_len_title) + 'chars'
            sys.exit(1)
    else:
        title1 = ''
        title2 = args.title
        title3 = ''
    #DEBUG
    print "Titel Zeile 1: " + title1
    print "Titel Zeile 2: " + title2
    print "Titel Zeile 3: " + title3

    # split subtitle into two lines if necessary
    if len(args.subtitle) > line_len_subtitle:
        subtitleRE = re.compile(r'^(.{0,'+str(line_len_subtitle)+r'}) (.*)$')
        subtitles = subtitleRE.search(args.subtitle).groups()
        subtitle1 = subtitles[0]
        subtitle2 = subtitles[1]
        if len(subtitle2) > line_len_subtitle:
            print "subtitle too long (2nd line)"
            sys.exit(1)
    else:
        subtitle1 = args.subtitle
        subtitle2 = ''

    if args.speakers is None:
        speakers1 = ''
        speakers2 = ''
        speakers3 = ''
    elif len(args.speakers) == 2:
        speakers1 = args.speakers[0]
        speakers2 = args.speakers[1]
        speakers3 = ''
    else:
        speakers = []
        tmp = ''
        for spk in args.speakers:
            if (len(tmp) + 3 + len(spk)) > line_len_speaker:
                speakers.append(tmp)
                tmp = ''
            # append
            if tmp != '':
                tmp += ' + '
            tmp += spk.upper()
        if tmp != '':
            speakers.append(tmp)
        if len(speakers) == 1:
            speakers1 = speakers[0]
            speakers2 = ''
            speakers3 = ''
        elif len(speakers) == 2:
            speakers1 = speakers[0]
            speakers2 = speakers[1]
            speakers3 = ''
        elif len(speakers) == 3:
            speakers1 = speakers[0]
            speakers2 = speakers[1]
            speakers3 = speakers[2]
        elif len(speakers) > 3:
            speakers1 = speakers[0]
            speakers2 = speakers[1]
            speakers3 = speakers[2] + ' et al'
        else:
            print "too many authors"
            speakers1 = ''
            speakers2 = ''
            speakers3 = ''
            #sys.exit(1)
    #DEBUG
    print 'Speakers Line1: ' + speakers1
    print 'Speakers Line2: ' + speakers2
    print 'Speakers Line3: ' + speakers3
# why is this not used?
#    if len(args.speakers) == 1:
#        speaker = args.speakers[0]
#    elif len(args.speakers) == 2:
#        speaker = args.speakers[0] + ' ' + args.speakers[1]
#    elif len(args.speakers) == 3:
#        speaker = args.speakers[0] + ' - ' + args.speakers[1] + ' - ' + args.speakers[2]
#    elif len(args.speakers) == 4:
#        speaker = args.speakers[0] + ' - ' + args.speakers[1] + ' - ' + args.speakers[2] + ' - ' + args.speakers[3]
#    # in the rare case that we have more than 4 speaker we replace the last speakers with et al.
#    elif len(args.speakers) > 4:
#        speaker = args.speakers[0] + ' - ' + args.speakers[1] + ' - ' + args.speakers[2] + ' - ' + args.speakers[3] + ' - et al.'


    from xml.sax.saxutils import escape

    # replace the strings in the svg
    # add here some filtering to precent to long names
    for line in fileinput.FileInput(args.background,inplace=0):
        if "%title$1%" in line:
            line=line.replace('%title$1%', escape(title1))
        elif "%title$2%" in line:
            line=line.replace('%title$2%', escape(title2))
        elif "%title$3%" in line:
            line=line.replace('%title$3%', escape(title3))
        elif "%subtitle$1%" in line:
            line=line.replace('%subtitle$1%', escape(subtitle1))
        elif "%subtitle$2%" in line:
            line=line.replace('%subtitle$2%', escape(subtitle2))
        elif "%speaker$1%" in line:
            line=line.replace('%speaker$1%', escape(speakers1))
        elif "%speaker$2%" in line:
            line=line.replace('%speaker$2%', escape(speakers2))
        elif "%speaker$3%" in line:
            line=line.replace('%speaker$3%', escape(speakers3))
        elif "%date%" in line:
            line=line.replace('%date%', escape(args.date+' '+args.begin))
        output.append(line)

    outfileName = args.workdir+args.id+".svg"
    outfile = file(outfileName, 'w')
    outfile.writelines(output)

# create a png out of the svg
def build_png():
    cmd = inkscape+" "+ args.workdir+args.id +".svg -e "+args.workdir+args.id+".png"
    #print cmd
    result = commands.getstatusoutput(cmd)
    if result[0] != 0:
        print "png not created"
        print result[1]
        sys.exit(1)

# build the video file
def build_video():
    #print " talk ID "+args.id
    # check if tmp file already present and remove it
    if os.path.exists(args.workdir+args.id+".tmp"):
        commands.getstatusoutput("rm -f "+args.workdir+args.id+".tmp")
    #result = commands.getstatusoutput("avconv -qscale 3 -loop 1 -i "+ args.workdir+args.id +".png -t 20 -target pal-dv "+args.workdir+args.id+".tmp -r 25 -an")
    #print result[1]
    #if result[0] != 0:
    #    print "inital dv file not created"
    #    print result[1]
    #    sys.exit(1)

    #check if silence file is present, if not generate it
    #if not os.path.exists('silence'):
    #    os.system('dd if=/dev/zero of=silence ibs=10240 count=10240')

    #check if prerole file is present if yes delete it
    if os.path.exists(args.output+args.id+"_title.ts"):
        commands.getstatusoutput("rm -f "+args.output+args.id+"_title.ts")

#    #cat the first part of the prerole in front of the edittedt one
#    result = commands.getstatusoutput('cat prerole.dv '+ args.workdir+args.id +'.tmp > '+ args.workdir+args.id +'.dv')
    #cmd = "avconv -f dv -i "+args.workdir+args.id+".tmp -f s16le -i silence -target pal-dv -t 10s "+args.output+args.id+"prerole.dv"
    #cmd = "ffmpeg -loop 1 -f image2 -i {file_in}.png -ar 48000 -ac 2 -f s16le -i /dev/zero -c:v libx264 -t 3 -pix_fmt yuv420p -profile:v baseline -refs 2 -b 15M {file_out}_prerole.mp4".format(file_in=(args.workdir+args.id), file_out=(args.output+args.id))
    #cmd = "ffmpeg -loop 1 -f image2 -i {file_in}.png -i intro_prerole.wav -c:v libx264 -t 3 -pix_fmt yuv420p -profile:v baseline -refs 2 -b 15M {file_out}_prerole.mp4".format(file_in=(args.workdir+args.id), file_out=(args.output+args.id))
    #cmd = "ffmpeg -loop 1 -f image2 -i {file_in}.png -ar 48000 -ac 2 -f s16le -i /dev/zero -c:v libx264 -t 3 -pix_fmt yuv420p -profile:v baseline -refs 2 -b 15M {file_out}_title.ts".format(file_in=(args.workdir+args.id), file_out=(args.output+args.id))
    #cmd = "ffmpeg -loop 1 -f image2 -i {file_in}.png -ar 48000 -ac 2 -f s16le -i /dev/zero -c:v libx264 -t 3 -pix_fmt yuv420p -profile:v main -c:a libfaac {file_out}_title.ts".format(file_in=(args.workdir+args.id), file_out=(args.output+args.id))
    cmd = "ffmpeg -loop 1 -f image2 -i {file_in}.png -ar 48000 -ac 2 -f s16le -i /dev/zero -c:v libx264 -t 5 -pix_fmt yuv420p -profile:v main -c:a aac {file_out}_title.ts".format(file_in=(args.workdir+args.id), file_out=(args.output+args.id))

    print cmd

    result = commands.getstatusoutput(cmd)
    if result[0] != 0:
        print result[1]


    commands.getstatusoutput("rm -f "+args.workdir+args.id+".tmp")

    #clean up
    commands.getstatusoutput("rm -f "+args.workdir+args.id+".png")
    commands.getstatusoutput("rm -f "+args.workdir+args.id+".svg")


sys.stdout.write('   title: SVG \n'); sys.stdout.flush
build_svg()
sys.stdout.write('PNG '); sys.stdout.flush
build_png()
sys.stdout.write('video TS'); sys.stdout.flush
build_video()

print " done."
sys.exit(0)
