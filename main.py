import json

import requests

"""Fetch Tweets with Keywords"""

bearer_token = "YOUR_BEARER_TOKEN"

search_url = "https://api.twitter.com/2/tweets/search/recent"

search_headers = {"Authorization": f"Bearer {bearer_token}"}
search_resp = requests.get(
    search_url,
    headers=search_headers,
    params={
        "query": '"what are you building" -is:retweet -is:reply OR "what are you working on" -is:retweet -is:reply OR "anyone building cool things" -is:retweet -is:reply',
        "tweet.fields": "author_id,public_metrics,created_at,entities",
        "expansions": "author_id",
        "user.fields": "username,description,public_metrics,profile_image_url",
        "max_results": 20,  # Optional
    },
)
search_resp.json()


""" Normalize Tweet Data - transform each tweet into a dict."""
tweet_summary = []
for i, tweet in enumerate(search_resp.json()["data"]):
    temp_dict = {}

    # Tweet data
    temp_dict["tweet"] = tweet["text"]
    temp_dict["created_at"] = tweet["created_at"]
    temp_dict["retweet_count"] = tweet["public_metrics"]["retweet_count"]
    temp_dict["reply_count"] = tweet["public_metrics"]["reply_count"]
    temp_dict["like_count"] = tweet["public_metrics"]["like_count"]
    temp_dict["quote_count"] = tweet["public_metrics"]["quote_count"]
    temp_dict[
        "tweet_url"
    ] = f"https://twitter.com/{search_resp.json()['includes']['users'][i]['username']}/status/{tweet['id']}"

    # User data
    temp_dict["user_description"] = search_resp.json()["includes"]["users"][i][
        "description"
    ]
    temp_dict["name"] = search_resp.json()["includes"]["users"][i]["name"]
    temp_dict["username"] = search_resp.json(
    )["includes"]["users"][i]["username"]
    temp_dict["followers_count"] = search_resp.json()["includes"]["users"][i][
        "public_metrics"
    ]["followers_count"]
    temp_dict["following_count"] = search_resp.json()["includes"]["users"][i][
        "public_metrics"
    ]["following_count"]
    temp_dict["tweet_count"] = search_resp.json()["includes"]["users"][i][
        "public_metrics"
    ]["tweet_count"]
    temp_dict["profile_img"] = search_resp.json()["includes"]["users"][i][
        "profile_image_url"
    ]

    # Check if hashtags in tweet
    if "entities" in tweet:
        if "hashtags" in tweet["entities"]:
            tweet_hashtags = []
            for hashtag in tweet["entities"]["hashtags"]:
                tweet_hashtags.append(hashtag["tag"])
            temp_dict["tweet_hashtags"] = tweet_hashtags

    tweet_summary.append(temp_dict)

print(tweet_summary)

""" Send Slack Notification with Tweet Data"""

slack_webhook_url = "YOUR_SLACK_WEBHOOK_URL"

for tweet in tweet_summary:
    temp_tweet = tweet["tweet"].replace("\n", " ")  # Optional to remove \n
    slack_data = {
        "icon_emoji": ":mega:",
        "text": f"Promote yourself here \n *tweet:* {temp_tweet} \n *Author:* {tweet['name']} \n *Description:* {tweet['user_description']} \n *URL:* {tweet['tweet_url']}",
        "username": "New promotion tweet 📣",
        "channel": "#integration-testing",
        "attachments": [
            {
                "fallback": "Required plain-text summary of the attachment.",
                "text": "Optional text that appears within the attachment",
                "image_url": f"{tweet['profile_img']}",
                "thumb_url": f"{tweet['profile_img']}",
            }
        ],
    }

    # Check if hashtag
    if "tweet_hashtags" in tweet:
        slack_data["text"] += f"\n *Hashtags:* {', '.join(tweet['tweet_hashtags'])}"

    response = requests.post(
        slack_webhook_url,
        data=json.dumps(slack_data),
        headers={"Content-Type": "application/json"},
    )
    print(response.text)
