# slackecho

First thing you gotta do is create a Twitter app (http://dev.twitter.com/apps)
This will give you a consumer key and a consumer secret
Put these in targets.py

Then you need to create a Slack incoming hook. That will give you a URL,
put that in targets.py too.

Finally, you need Twitter users to authenticate with your app, which will give you an access_token_key and an access_token_secret. One way to get them to authenticate is to use the get_access_token.py example script which comes with the Python Twitter API.

Now initialize the targets array with:
 * the API you're going to use for that target (useful to read locked accounts)
 * the username of the target,
 * optionally, the channel name to direct the target's feed to
 * optionally, another slack hook in case you want to use more than one
 * optionally, a different last_id -- use 0 the first time you add a new target to start up with their recent tweets

 OK, that should be enough.