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
    d2 = json.dumps(data, ensure_ascii=False ,sort_keys=True, indent=4, separators=(',', ': '))
    # print d2
    event_tmp.close()

    # MOD! was if len(data) > 0 and len(data['items']) > 0:
        # event = data['items'][0]
    if len(data) > 0 and len(data[0]) > 0:
        event = data[0]
        # fix a few things: keep date from datetime
        event['date'] = event['datetime']['value'].split(' ', 1)[0]
        event['time'] = event['datetime']['value'].split(' ', 1)[1]
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
#     print "\n\n"
#     print p2
#     print "\n\n"
    p_tmp.close()
    # add value for a full name
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

def get_yt_upload_options(event):
    #event = get_session_data(session_id, event_id)
    # for later concatenation
    title = event['title']
    description = event['description_short']

    # convenience array of speaker names
    persons = event['speaker_names']
    # convenience array of speaker profile user ids
    person_ids = event['speaker_uids']

    # dict used to submit options to youtube (needs to be converted to youtube object, I believe)
    options = dict(event=event['event_title']) # create dict with one entry ('event': 'rpYEAR')
    options['id'] = event['nid']
    # 08.05.2014 - 10:30 bis 11:00 (start and end are also avail)
    options['datetime'] = event['date']+'T'+event['time']

    # I really dislike this heuristic, but I think we'll keep it for now
    if len(persons) == 1 and persons[0]:
        options["title"] = event['event_title'] + ' - ' + persons[0] + ': ' + title
    #elif len(persons) == 2:
    #    options["title"] =  event['event_title'] + ' - ' + persons[0] + ', ' + persons[1] + ': ' + title
    else:
        options["title"] = event['event_title']  + ' - ' + title

    # trim title. this is stupid since we've concatenated a bunch of crap without checking it's length
    # Youtube allows max 100 chars, see https://groups.google.com/d/msg/youtube-api-gdata/RzzD0MxFLL4/YiK83QnS3rcJ
    if len(options["title"]) > 100:
         options["title"] = options["title"][:100] # hard trim
         print 'trimmed title for youtube compatibility!/n'

    # truncated on word boundary
    temp_desc = textwrap.wrap(description, 700)
    description = textwrap.wrap(description, 700)[0]
    # add ... if description was truncated
    if len(temp_desc) > 1:
        description += '...'
        print 'truncated description !!/n'

    options["description"] = '\n\n'. join(filter(None, [
            'Find out more at: ' + event['uri'],
            description
        ]))


    for p in person_ids:
        # ignore empty person entries (was relevant for rp13 xml)
        if not p:
            continue
        person = get_person_data(p, config.event_id)
        wo = person['org_uri']

#
#         options["description"] += ('\n\n'
#           + person['label'] + str(wo and '\n') + str(wo)
#         )

# here was Tom Orr's unicode Workaround!!


        #options["description"] += ('\n\n'
        #    + ' | '.join(  [ person['label'] ] + person['link_uris'] )
        #    + str(wo and '\n') + str(wo)
        #)
        #options["description"] += ('\n\n'
        #    + ' | '.join(filter(None, [person[a] for a in ['label', 'website_personal', 'twitter', 'facebook']]))
        #    + str(wo and '\n') + str(wo)

    options["description"] += '\n\nCreative Commons Attribution-ShareAlike 3.0 Germany \n(CC BY-SA 3.0 DE)'

    # this sucks. we should use meta data from the event itself
    keywords = ['#rp'+config.year, 'rp'+config.year, 're:publica', 'republica',
        event["category"], event["room"]] + [p for p in persons]
    options["keywords"] = ', ' . join(keywords)
    options["category"] = event["category"]
    options["subtitle"] = ''

    options["person_labels"] = ', '.join(persons)

    options["slug"] = event['uri'].split('/', 2)[2]

    return options

if __name__ == '__main__':
    debug = True

    # argument handling
    parser = argparse.ArgumentParser(description='return session json from re-publica.de/event/arg1/session/arg2/json')
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
