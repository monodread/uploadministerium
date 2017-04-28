# A script to get the talk details from the republica website

#!/usr/bin/env python
import argparse, simplejson as json, urllib2, textwrap

#if __name__ == '__main__':
import config

debug = False

def get_session_data(session_id, event_id=config.event_id):
    # fetch individual session
    jsonurl='https://re-publica.com/rest/sessions.json?args[0]='+event_id
    if config.offline:
        event_tmp = open(session_id+'.json')  # not currently used?
    else:
        if debug:
            print jsonurl+'&nid='+session_id
        event_tmp = urllib2.urlopen(jsonurl+'&nid='+session_id)
    data = json.load(event_tmp, 'utf-8') # format input from json to python dict type
    # pretty-format obj as json str for posting? #DEBUG
    # d2 = json.dumps(data, ensure_ascii=False ,sort_keys=True, indent=4, separators=(',', ': '))
    # print d2
    event_tmp.close()

    # MOD 2017! was if len(data) > 0 and len(data['items']) > 0:
        # event = data['items'][0]
    if len(data) > 0 and len(data[0]) > 0:
        event = data[0]
        # fix a few things: keep date from datetime
        event['date'] = event['datetime']['value'].split(' ', 1)[0]
        event['time'] = event['datetime']['value'].split(' ', 1)[1]
        # fix non-escaped html charsets (&amp;)
        event['category'] = event['category'].replace("&amp;", "&")

        print "got event"
    else:
        print "no session data found"
        raise Exception('no sessions with id: ' + session_id)

    return event

def get_person_data(person_id, event_id=config.event_id):
    speakerurl='https://re-publica.com/rest/speakers.json?args[0]='+event_id
    if config.offline:
        p_tmp = open('speaker_'+person_id+'.json')  # not currently used?
    else:
        if debug:
            print speakerurl+'&uid='+person_id
        p_tmp = urllib2.urlopen(speakerurl+'&uid='+person_id)
    data = json.load(p_tmp,'utf-8')
    persondata = data[0]
    p2 = json.dumps(data, ensure_ascii=False ,sort_keys=True, indent=4, separators=(',', ': '))
#   print "\n\n"
#    print p2
#   print "\n\n"
    p_tmp.close()
    # add a field for a full name
    persondata['name'] = persondata['gn']+' '+persondata['sn']

    return persondata

def get_all_sessions(event_id='1'):
    jsonurl='https://re-publica.com/rest/sessions.json?args[0]='+event_id
    if config.offline:
        tmp = open('sessions.json') # not currently used?
    else:
        tmp = urllib2.urlopen(jsonurl)
    data = json.load(tmp, 'utf-8')
    # pretty-format obj as json str for posting? #DEBUG
    # d2 = json.dumps(data, ensure_ascii=False ,sort_keys=True, indent=4, separators=(',', ': '))
    # print d2
    tmp.close()
    return data

def get_yt_upload_options(event, privacy=config.ytprivacy, playlist=config.ytplaylist):

    title = event['title']
    description = event['description_short']
    persons = event['speaker_names']
    person_ids = event['speaker_uids']

    # dict used to submit options to youtube
    options = dict(event=event['event_title']) # create dict with one entry ('event': 'rpYEAR')
    options['id'] = event['nid']
    # "Recording date (ISO 8601): YYYY-MM-DDThh:mm:ss.sZ" or "2011-03-10T15:32:17.0Z"
    options['datetime'] = event['date']+'T'+event['time']+'.1Z'
    # alternative provided by API: options['datetime'] = event['start_iso']

    # FORMAT THE TITLE
    # only mention speakers in video title if not more than one
    if len(persons) == 1 and persons[0]:
        options["title"] = event['event_title'] + ' - ' + persons[0] + ': ' + title
    #elif len(persons) == 2:
    #    options["title"] =  event['event_title'] + ' - ' + persons[0] + ', ' + persons[1] + ': ' + title
    else:
        options["title"] = event['event_title']  + ' - ' + title
    # Youtube allows max 100 chars, see https://groups.google.com/d/msg/youtube-api-gdata/RzzD0MxFLL4/YiK83QnS3rcJ
    if len(options["title"]) > 100:
         options["title"] = options["title"][:100] # hard trim
         print 'trimmed title for youtube compatibility!/n'

    # FORMAT THE YT DESCRIPTION
    # truncate description text from session on word boundary, max 700 chars
    temp_desc = textwrap.wrap(description, 700)
    description = textwrap.wrap(description, 700)[0]
    # add ... if description was truncated
    if len(temp_desc) > 1:
        description += '...'
        print 'yt description longer than 700, was truncated !!/n' #debug
    # start desc with link to rp-website for session
    options["description"] = '\n\n'. join(filter(None, [
            'Find out more at: ' + event['uri'],
            description
        ]))

    # Now we add the speaker names with their personal infos to yt desc
    for p in person_ids:
        # ignore empty person entries (was relevant for rp13 xml)
        if not p:
            continue
        persondata = get_person_data(p, config.event_id)
        personurl = persondata['org_uri']
        #print "adding a social media/twitter url for: " + persondata['name']
        if len(persondata['links']) > 1 and persondata['links']:
            urls = []
            word = 'twitter'
            for x in persondata['links']:
                for k,v in x.items():
                    if k =='url' and word in v:
                        urls.append(v)
                        break
        else:
            urls = []
        #print urls
        twiturls = " | ".join(urls)
        # !! WORKAROUND BY TOM ORR due to UnicodeEncodeError
        s = ""
        for i, l in enumerate(persondata['name']):
            if ord(persondata['name'][i]) <= 128:
                s += persondata['name'][i]
            else:
                print " ---- WORKAROUND FOR UNICODE ERROR ---- "
                s += '~'
                print "WARNING: NON ASCII CHAR FOUND. "
                print persondata['name'][i]
                print "SEARCH FOR '~' AND REPLACE MANUALLY AFTER PROCESSING"
        persondata['name'] = s

        # do the same for the url
        s = ""
        for i, l in enumerate(personurl):
            if ord(personurl[i]) <= 128:
                s += personurl[i]
            else:
                print " ---- WORKAROUND FOR UNICODE ERROR ---- "
                s += '~'
                print "WARNING: NON ASCII CHAR FOUND. "
                print personurl[i]
                print "SEARCH FOR '~' AND REPLACE MANUALLY AFTER PROCESSING"
        personurl = s
        # !! END WORKAROUND
        if len(twiturls) > 0:
            options["description"] += ('\n\n' + (persondata['name']) + '\n' + str(personurl) + '\n' + str(twiturls))
        else:
            options["description"] += ('\n\n' + (persondata['name']) + '\n' + str(personurl))

    options["description"] += '\n\nCreative Commons Attribution-ShareAlike 3.0 Germany \n(CC BY-SA 3.0 DE)'

    # this sucks. we should use metadata from the event itself
    keywords = ['#rp'+config.year, 'rp'+config.year, 're:publica', 'republica',
        event["category"], event["room"]] + [p for p in persons]
    options["keywords"] = ', ' . join(keywords)

    # CAREFUL THIS MUST BE COMPLIANT WITH YOUTUBE VIDEO CATS!
    # For now we will post all videos in same category: Bildung, as done previously
    options["category"] = "Education"

    options["subtitle"] = ''

    options["person_labels"] = ', '.join(persons) # What is this needed for?

    options["slug"] = event['uri'].split('/', 2)[2]
    # extra youtube relevant args
    options["privacy"] = privacy
    options["playlist"] = playlist

    return options

if __name__ == '__main__':
    debug = True

    # argument handling, # old! from 2014??
    parser = argparse.ArgumentParser(description='return session json from '+config.event_url)
    parser.add_argument('-e', '--event', default='3013', help='event id, group node id, 1 = 2014', dest='event')
    parser.add_argument('-s', '--session', default='3094', help='session id, node id',dest='session')
    args = parser.parse_args()

    event = get_session_data(args.session, args.event)
    options = get_yt_upload_options(event)

    print "printing the options "
    print options['title']
    print options['category']
    print options['datetime']
    print options['description']
    print
    print options['keywords']
