import sys
import twitter
import json
import urllib2
import re

link_re = re.compile(r"https://t.co(/[A-Za-z0-9]+)")
username_re = re.compile(r"\B@([\S]+)")
hashtag_re = re.compile(r"[\B\s]#([\S]+)")
def urlparse(tweet):
    m=link_re.search(tweet)
    if m:
        c = urllib2.Request("https://t.co/%s" % m.group(1))
        c.get_method = lambda : 'HEAD'
        r = urllib2.urlopen(c)
        tweet = p.sub(r.info().getheader('location'),tweet)
    if username_re.search(tweet):
        tweet = username_re.sub(r"<https://twitter.com/\1|@\1>",tweet)
    if hashtag_re.search(tweet):
        tweet = hashtag_re.sub(r"<https://twitter.com/hashtag/\1|#\1>",tweet)
    return tweet

def make_attachment(tweet):
    at = {
      "fallback":"https://twitter.com/%s/status/%d" % (tweet.user.screen_name, tweet.id),
      "pretext": at["fallback"],
      "author_name": tweet.user.name,
      "author_subname": "@"+tweet.user.screen_name,
      "author_link": at["fallback"],
      "author_icon": tweet.user.profile_image_url,
      "footer": "Twitter",
      "footer_icon": "https://slack.global.ssl.fastly.net/6e067/img/services/twitter_pixel_snapped_32.png",
      "ts": tweet.created_at_in_seconds,
      "footer_link": at["fallback"],
      "mrkdwn_in"=[]
    }
    try:
        at["text"] = urlparse(tweet.full_text.encode('utf-8'))
    except:
        at["text"] = tweet.full_text.encode('utf-8')
    if tweet.media:
        at["image_url"]=tweet.media.pop().media_url_https
    return at

def do_loop(target):
    try:
        tl = target.twapi.GetUserTimeline(screen_name=target.username, include_rts=False, since_id=target.last_id)
        tl.sort(cmp=lambda x,y: cmp(x.id, y.id))
    except twitter.error.TwitterError, e:
        print target.username,sys.exc_info()
        target.fail = target.fail+1
        if target.fail == 2:
            pl = {"text": "_%s has deactivated_" % target.username, "channel":target.channel}
            urllib2.urlopen(urllib2.Request(target.hook, json.dumps(pl)))
        tl = []
    else:
        if target.fail >= 2:
            pl = {"text":"_%s has reactivated_" % target.username, "channel":target.channel}
            urllib2.urlopen(urllib2.Request(target.hook, json.dumps(pl))
        target.fail = 0

    for tweet in tl:
        if tweet.id in target.sent:
            continue
        
        target.sent[tweet.id]=True

        pl = {"attachments": [make_attachment(tweet),],
              "channel": target.channel}

        # if reply, include the tweet being replied to
        if (tweet.in_reply_to_status_id and not tweet.in_reply_to_status_id in target.sent):     
            target.sent[tweet.in_reply_to_status_id]=True
            pl["attachments"].twapi["color"]="#0084b4"
            try:
                st = target.twapi.GetStatus(tweet.in_reply_to_status_id)
                p2 = {"attachments": [make_attachment(st)],
                      "channel": target.channel}
                p2["attachments"].twapi["color"]="#0084b4"
                urllib2.urlopen(urllib2.Request(target.hook, json.dumps(p2)))
            except:
                pass

        urllib2.urlopen(urllib2.Request(target.hook, json.dumps(pl)))

        target.last_id = tweet.id
        file("last_id.txt","wc").write(str(tweet.id))

# Initialization and main loop

try:
    last_id = int(file("last_id.txt").read())
except:
    last_id=0

from targets import *

def main(id=None):
    for t in targets:
        if t.last_id == -1:
            t.last_id = last_id
    while True:
        for t in targets:
            try:
              do_loop(t)
            except:
              print t.username,sys.exc_info()
            time.sleep(30 / len(targets))
        sys.stderr.write('.')

main()
