last_id=0
import sys
import twitter
import json
import urllib
import urllib2
import time
import re
import httplib

def urlparse(tweet):
    p=re.compile(r"https://t.co(/[A-Za-z0-9]+)")
    m=p.search(tweet)
    if m:
        c=httplib.HTTPSConnection("t.co")
        c.request("HEAD",m.group(1))
        tweet = p.sub(c.getresponse().getheader('location'),tweet)
    p=re.compile(r"\B@([\S]+)")
    if p.search(tweet):
        tweet=p.sub(r"<https://twitter.com/\1|@\1>",tweet)
    p=re.compile(r"[\B\s]#([\S]+)")
    if p.search(tweet):
        tweet=p.sub(r"<https://twitter.com/hashtag/\1|#\1>",tweet)
    return tweet

def make_attachment(tweet):
    at = {}
    at["fallback"]="https://twitter.com/%s/status/%d" % (tweet.user.screen_name, tweet.id)
    at["pretext"]=at["fallback"]
    at["author_name"] = tweet.user.name
    at["author_subname"] = "@"+tweet.user.screen_name
    at["author_link"] = at["fallback"]
    at["author_icon"] = tweet.user.profile_image_url
    try:
        at["text"] = urlparse(tweet.full_text.encode('utf-8'))
    except:
        print "oops!"
        at["text"] = tweet.full_text.encode('utf-8')
    tt=time.localtime(tweet.created_at_in_seconds)
    now=time.localtime()
    if tt[2]==now[2]:
        timestr="Today at "+time.strftime("%-1I:%M %P",tt)
    else:
        timestr=time.strftime("%b %-1d %-1I:%M %P",tt)
    #at["fields"]=[{"value":"<%s|%s>" % (at["fallback"],timestr)},]
    #at["fields"]=[{"value":"<%s|Twitter> <!date^%d^{date_short_pretty} at {time}|%s>" % (at["pretext"],tweet.created_at_in_seconds, timestr)}]
    at["footer"]="Twitter"
    at["footer_icon"]="https://slack.global.ssl.fastly.net/6e067/img/services/twitter_pixel_snapped_32.png"
    at["ts"] = tweet.created_at_in_seconds
    at["footer_link"]=at["fallback"]
    at["mrkdwn_in"]=[]
    if tweet.media:
        at["image_url"]=tweet.media.pop().media_url_https
    return at

def do_loop(target):
    try:
        tl = target[0].GetUserTimeline(screen_name=target[1], include_rts=False, since_id=target[2])
        tl.sort(cmp=lambda x,y: cmp(x.id, y.id))
    except twitter.error.TwitterError, e:
        print target[1],sys.exc_info()
        target[4] = target[4]+1
        if target[4] == 2:
            pl = {"text": "_%s has deactivated_" % target[1], "channel":target[6]}
            req = urllib2.Request(target[3], json.dumps(pl))
            resp = urllib2.urlopen(req)
        tl = []
    else:
        if target[4] >= 2:
            pl = {"text":"_%s has reactivated_" % target[1], "channel":target[6]}
            req = urllib2.Request(target[3], json.dumps(pl))
            resp = urllib2.urlopen(req)
        target[4] = 0
    for tweet in tl:
        if tweet.id in target[5]:
            continue
        target[5][tweet.id]=True
        pl = {"attachments": [make_attachment(tweet),]}
        if (tweet.in_reply_to_status_id and not tweet.in_reply_to_status_id in target[5]):     
            target[5][tweet.in_reply_to_status_id]=True
            pl["attachments"][0]["color"]="#0084b4"
            try:
                st = target[0].GetStatus(tweet.in_reply_to_status_id)
                p2 = {"attachments": [make_attachment(st)]}
                p2["attachments"][0]["color"]="#0084b4"
                p2["channel"]=target[6]
                req = urllib2.Request(target[3], json.dumps(p2))
                resp = urllib2.urlopen(req)
            except:
                pass

        pl["channel"]=target[6]
        req = urllib2.Request(target[3], json.dumps(pl))
        resp = urllib2.urlopen(req)

        target[2] = tweet.id
        file("last_id.txt","wc").write(str(tweet.id))

try:
    last_id = int(file("last_id.txt").read())
except:
    pass

from targets import *
for x in targets:
  if targets[2] == -1:
    targets[2] = last_id

def program(id=None):
    if id:
         for t in targets:
            t[2]=id
    while True:
        for t in targets:
            try:
             do_loop(t)
            except:
             print t[1],sys.exc_info()
            time.sleep(30 / len(targets))
        sys.stderr.write('.')

program()
