import praw
import OAuth2Util
import sqlite3
import requests
import time

from mailer import DigestMailer

class Digester():
    """Digester checks reddit for changes since the last run."""
    
    def __init__(self, user_agent, user_data, defaults):
        self.r = praw.Reddit(user_agent=user_agent)
        self.o = OAuth2Util.OAuth2Util(self.r)
        self.user_data = user_data
        self.defaults = defaults
            
    def get_karma_change(self):
        """Return the difference in comment and link karma since the
           last database update."""
        self.o.refresh()
        comment_karma_old = self.user_data['comment_karma']
        self.comment_karma = self.r.get_me().comment_karma
        link_karma_old = self.user_data['link_karma']
        self.link_karma = self.r.get_me().link_karma
        self._update_user_db()
        return (self.comment_karma - comment_karma_old,
                self.link_karma - link_karma_old)
    
    def _update_user_db(self):
        """Change the database entry for the user to the latest values."""
        with sqlite3.connect('resources/user_data.db') as conn:
            c = conn.cursor()
            c.execute("UPDATE users SET comment_karma=?, link_karma=?\
                       WHERE username=?", (self.comment_karma, 
                                           self.link_karma, 
                                           self.user_data['username']))
    
    def get_3_hottest_submissions_last_day(self):
        self.o.refresh()
        my_subs = [str(x) for x in self.r.get_my_subreddits()]
        my_non_defaults = [x for x in my_subs if x not in self.defaults]
        print(my_non_defaults)
        for sub in my_non_defaults:
            sub = self.r.get_subreddit(sub)
            subs = sub.subscribers
            hot = [x for x in sub.get_hot(time='day', limit=3)]
            print(sub, subs, hot)

def load_user_data_from_db():
    columns = ['username', 'comment_karma', 'link_karma', 'mail']
    with sqlite3.connect('resources/user_data.db') as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM users")
        data = c.fetchone()
        return {x: data[x] for x in columns}

def load_default_subreddits():
    while True:
        r = requests.get('https://reddit.com/subreddits/default.json').json()
        if 'data' in defaults:
            break
        else:
            time.sleep(2)
    defaults = [str(x['data']['url']).replace('/r/','').replace('/','') 
                for x in defaults['data']['children']]
    return defaults

def main():
    user_data = load_user_data_from_db()
    defaults = load_default_subreddits()
    print(defaults)
    digest = Digester(USER_AGENT, user_data, defaults)
    digest.get_3_hottest_submissions_last_day()
    mail = DigestMailer(user_data)
    mail.send()

VERSION = '0.1'
USER_AGENT = 'digest for reddit v{} by u/individual_throwaway'.format(VERSION)
    
if __name__ == '__main__':
    main()