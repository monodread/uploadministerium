#!/usr/bin/python

# Integrating https://github.com/tokland/youtube-upload
# into automated RP Workflow
# necessary to put the "youtube-upload" folder into /work_dir !

import config
from subprocess import check_output, CalledProcessError

# usage: youtube_uploader.upload_file(final_file, metadata):
def upload_file(filepath, metadata):
    if not filepath:
        filepath = config.ytfilepath
        print "no valid filepath given; using the test file\n"
        print filepath

    if not metadata['privacy']:
        metadata['privacy'] = 'private'
    if not metadata['playlist']:
        metadata['playlist'] = 'rp'+config.year+'-test'

    credentialspath = config.ytcredentialspath
    print " creating Youtube-Upload for Talk-ID {0} '{1}'".format(metadata['id'], "")
    print str("uploading as " + metadata['privacy'] + " to list" + metadata['playlist'])

    # Version1: create a complete string for subprocess call
    metadataStr = ' --title="'+metadata['title']+\
    '" --description="'+metadata['description']+\
    '" --tags="'+metadata['keywords']+\
    '" --playlist="'+metadata['playlist']+\
    '" --privacy="'+metadata['privacy']+\
    '" --recording-date="'+metadata['datetime']+\
    '" --category="'+metadata['category']+\
    '" --client-secrets="'+credentialspath+'"'

    commandline = 'youtube-upload' + metadataStr +' '+filepath
    #print commandline

    print 'starting upload now'
    try:
        # THIS THROWS ERROR: FILENAME too long, when not setting shell to True!
        out = check_output(commandline, shell=True)
        t = 0, out #assigns a tuple
        # output of the uploader will be the yt video id!
        outStr = str(t[1])
        print "Video ID is: " + outStr
    except CalledProcessError as e:
        t = e.returncode, e.message
        #return e.returncode, t.read()

    if t[0] == 0:
        return True
    else:
        return t

    # check for success
#    if process.returncode == 0:
    #	print " youtube-uploader was successful "
	#	return True
    #else:
	#	print " youtube-uploader failed with response: "
	#	return False

"""

EXIT_CODES = {
    OptionsError: 2,
    InvalidCategory: 3,
    RequestError: 3,
    AuthenticationError: 4,
    oauth2client.client.FlowExchangeError: 4,
    NotImplementedError: 5,
}
"""
