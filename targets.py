import twitter

consumer_key = "CONSUMER_KEY"
consumer_secret = "CONSUMER_SECRET"
slack_hook = "SLACK_HOOK"

class target:
    def __init__(self, twapi, username, channel, hook=slack_hook, last_id=-1):
        self.twapi = twapi
        self.username = username
        self.last_id = last_id
        self.hook = hook
        self.channel = channel
        self.sent = {}

api1 = twitter.Api(consumer_key=consumer_key, consumer_secret=consumer_secret, tweet_mode='extended',
                   access_token_key='ATK',
                   access_token_secret='ATS')
api2 = twitter.Api(consumer_key=consumer_key, consumer_secret=consumer_secret, tweet_mode='extended',
                   access_token_key='ATK',
                   access_token_secret='ATS')

targets = [
    target(api1, "target1", "#foo"),
    target(api2, "target2", "#bar"),
]

for t in targets:
  if t.last_id == -1:
    t.last_id = last_id
