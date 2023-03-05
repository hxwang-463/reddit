import praw
from praw.models import MoreComments
import json
from datetime import datetime
import toml

class RedditPost:
    def __init__(self):
        config = toml.load('config.toml')
        self.reddit = praw.Reddit(
            client_id=config['client_id'],
            client_secret=config['client_secret'],
            user_agent=config['user_agent'],
        )
        self.subreddit = None

    def set_subreddit(self, subreddit):
        self.subreddit = self.reddit.subreddit(subreddit)

    def flush(self, file_path, contents:list[dict]):
        with open(file_path, "a") as f:
            for content in contents:
                json.dump(content, f, separators=(',', ':'))
                f.write("\n")
        last_time = contents[-1]["time"]
        print("Last post time:", datetime.fromtimestamp(last_time).strftime("%Y-%m-%d %H:%M:%S"))

    def get_reply(self, target):
        reply = {}
        reply["text"] = target.body.replace("\n", " ")
        reply["time"] = target.created_utc
        reply["comments"] = []
        for comment in target.replies:
            if isinstance(comment, MoreComments):
                continue
            reply["comments"].append(self.get_reply(comment))
        return reply

    def get_new(self, file_path):
        with open(file_path, "w") as f:
            pass
        i = 0
        posts = []
        for submission in self.subreddit.new(limit=None):
            # submission.comment_sort = "new"
            # submission.comments.replace_more(limit=None)
            post = {}
            post["title"] = submission.title
            post["text"] = submission.selftext.replace("\n", " ")
            post["time"] = submission.created
            comments = []
            for comment in submission.comments:
                if isinstance(comment, MoreComments):
                    continue
                comments.append(self.get_reply(comment))
            post["comments"] = comments
            posts.append(post)
            i+=1
            if i==10:
                self.flush(file_path, posts)
                posts = []
                i=0
        if i>0:
            self.flush(file_path, posts)



if __name__ == '__main__':

    reddit_post = RedditPost()
    reddit_post.set_subreddit("GameStop")
    reddit_post.get_new("./GameStop.txt")



