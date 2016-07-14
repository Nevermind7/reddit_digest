import praw
import OAuth2Util
import sqlite3
import requests
import time

from mailer import DigestMailer

class Digester():
    """Digester checks reddit for changes since the last run."""
    
    def __init__(self, user_agent, user_data):
        self.r = praw.Reddit(user_agent=user_agent)
        self.o = OAuth2Util.OAuth2Util(self.r, configfile='resources/oauth.ini')
        self.user_data = user_data
        self.defaults = self._load_default_subreddits()
        self.digested = {}
    
    def _load_default_subreddits(self):
        while True:
            defaults = requests.get('https://reddit.com/subreddits/default.json').json()
            if 'data' in defaults:
                break
            else:
                print('Oops, looks like we made too many requests to reddit. Waiting before retry...')
                time.sleep(2)
        defaults = [str(x['data']['url']).replace('/r/','').replace('/','') 
                    for x in defaults['data']['children']]
        return defaults
            
    def get_karma_change(self):
        """Return the difference in comment and link karma since the
           last database update."""
        self.o.refresh()
        comment_karma_old = self.user_data['comment_karma']
        self.comment_karma = self.r.get_me().comment_karma
        link_karma_old = self.user_data['link_karma']
        self.link_karma = self.r.get_me().link_karma
        self._update_user_db()
        self.digested['comment_karma'] = self.comment_karma - comment_karma_old
        self.digested['link_karma'] = self.link_karma - link_karma_old
    
    def _update_user_db(self):
        """Change the database entry for the user to the latest values."""
        with sqlite3.connect('resources/user_data.db') as conn:
            c = conn.cursor()
            c.execute("UPDATE users SET comment_karma=?, link_karma=?\
                       WHERE username=?", (self.comment_karma, 
                                           self.link_karma, 
                                           self.user_data['username']))
    
    def get_hottest_submissions_last_day(self, amount=5):
        """Get the {amount} hottest submissions from all non-default subreddits."""
        self.o.refresh()
        my_subs = [str(x) for x in self.r.get_my_subreddits()]
        my_non_defaults = '+'.join([x for x in my_subs if x not in self.defaults])
        subs = self.r.get_subreddit(my_non_defaults)
        hot = [x for x in subs.get_hot(time='day', limit=amount)]
        self.digested['amount_hot'] = amount
        hot = ['{:20}: {}({})'.format(str(x.subreddit),
                                   str(self._shorten(x.title)),
                                   str(x.short_link)) for x in hot]
        self.digested['hot_submissions'] = '\n'.join(hot)
    
    def _shorten(self, str):
        if len(str) < 48:
            return str
        else:
            return str[:48] + '...'
                

def load_user_data_from_db():
    columns = ['username', 'comment_karma', 'link_karma', 'mail']
    with sqlite3.connect('resources/user_data.db') as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM users")
        data = c.fetchone()
        return {x: data[x] for x in columns}

def main():
    user_data = load_user_data_from_db()
    mail = DigestMailer(user_data)
    digest = Digester(USER_AGENT, user_data)
    digest.get_hottest_submissions_last_day(amount=10)
    digest.get_karma_change()
    mail.send(digest.digested)

VERSION = '0.1'
USER_AGENT = 'digest for reddit v{} by u/individual_throwaway'.format(VERSION)
    
if __name__ == '__main__':
    main()