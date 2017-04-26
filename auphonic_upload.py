#!/usr/bin/python
#   -  *  - cod ing: UTF-8 - * -

# based on https://github.com/MaZderMind/c3voc-toolz/blob/master/auphonic-upload/upload.py from MaZderMind

import sys
import requests
from poster.encode import multipart_encode

#if __name__ == '__main__':
import config


# an adapter which makes the multipart-generator issued by poster accessable to requests
# based upon code from http://stackoverflow.com/a/13911048/1659732
class IterableToFileAdapter(object):
	def __init__(self, iterable):
		self.iterator = iter(iterable)
		self.length = iterable.total

	def read(self, size=-1):
		return next(self.iterator, b'')

	def __len__(self):
		return self.length

# define a helper function simulating the interface of posters multipart_encode()-function
# but wrapping its generator with the file-like adapter
def multipart_encode_for_requests(params, boundary=None, cb=None):
	datagen, headers = multipart_encode(params, boundary, cb)
	return IterableToFileAdapter(datagen), headers

# tupload progress callback
def progress(param, current, total):
	sys.stderr.write("\r uploading {0}: {1:.2f}% ({2:d} MB of {3:d} MB)".format(param.filename if param else "", float(current)/float(total)*100, current/1024/1024, total/1024/1024))
	sys.stderr.flush()

# upload a single file to auphonic
def upload_file(filepath, event):
	print " creating Auphonic-Production for Talk-ID {0} '{1}'".format(event['id'], "") # event['title'])


	params = {
		# talk metadata
		"title": unicode(event['title']),
		"subtitle": unicode(event['subtitle']),
		"artist": unicode(event['person_labels']),

		# prepend personnames to description (makes them searchable in youtube)
# 		"summary": unicode(event['description']),
#		WORKAROUND BY Tom Orr because of changes to republica_schedule:
		"summary": event['description'],

		# whatever filename the input has, always name the outout as talkid.format
		#"output_basename": unicode(event['id']),

		# auphonic preset identifier
		'preset': unicode(config.auphonic_preset),

		# tell auphonic to start the production as soon as possible
		"action": "start",

		# file pointer to the input-file
		"input_file": open(filepath, 'rb')
	}

	# generate multipoart-encoder with progress display
	datagen, headers = multipart_encode_for_requests(params, cb=progress)

	# pass the generated encoder to requests which handles the http
	r = requests.post(
		'https://auphonic.com/api/simple/productions.json',
		auth=(config.auphonic_login[0], config.auphonic_login[1]),
		data=datagen,
		headers=headers
	)

	# linebreak
	print ""

	# check for success
	if r.status_code == 200:
		print " auphonic-upload successfull "
		return True

	else:
		print " auphonic-upload failed with response: ", r, r.text
		return False

