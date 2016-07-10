import praw
from datetime import datetime as dt
import smtplib
from email.mime.text import MIMEText
import OAuth2Util
import sqlite3
import json

class DigestMailer():
    
    def __init__(self, user_data):
        self.user = user_data['username']
        self.name = 'Reddit_Digest'
        self.address = user_data['mail']
        self.msg = MIMEText('test')
        self.msg['Subject'] = 'Reddit digest for u/{} on {}'.format(self.user, 
                                                                    str(dt.today()).split(' ')[0])
    def send(self):
        s = smtplib.SMTP('localhost')
        s.sendmail(self.name, self.address, self.msg.as_string())
        s.quit()

class Digester():
    
    def __init__(self, user_agent, user_data):
        self.r = praw.Reddit(user_agent=user_agent)
        self.o = OAuth2Util.OAuth2Util(self.r)
        self.user_data = user_data
            
    def get_karma_change(self):
        self.o.refresh()
        comment_karma_old = self.user_data['comment_karma']
        self.comment_karma = self.r.get_me().comment_karma
        link_karma_old = self.user_data['link_karma']
        self.link_karma = self.r.get_me().link_karma
        self._update_user_db()
        return (self.comment_karma - comment_karma_old,
                self.link_karma - link_karma_old)
    
    def _update_user_db(self):
        with sqlite3.connect('user_data.db') as conn:
            c = conn.cursor()
            c.execute("UPDATE users SET comment_karma=?, link_karma=?\
                       WHERE username=?", (self.comment_karma, 
                                           self.link_karma, 
                                           self.user_data['username']))
    
    def get_3_hottest_submissions_last_day(self):
        self.o.refresh()
        subreddits = [str(x) for x in self.r.get_my_subreddits()]
        for sub in subreddits:
            sub = self.r.get_subreddit(sub)
            subs = sub.subscribers
            top = [str(x) for x in sub.get_hot(time='day', limit=3)]
            print(sub, subs, top)

def load_user_data_from_db():
    columns = ['username', 'comment_karma', 'link_karma', 'mail']
    with sqlite3.connect('user_data.db') as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM users")
        data = c.fetchone()
        return {x: data[x] for x in columns}

def load_default_subs():
    with open('default.json', 'r') as default:
        defaults = json.load(default)
    defaults = [str(x['data']['url']).replace('/r/','').replace('/','') 
                for x in defaults['data']['children']]
    return defaults

def main():
    user_data = load_user_data_from_db()
    default_subs = load_default_subs()
    digest = Digester(USER_AGENT, user_data)
    digest.get_3_hottest_submissions_last_day()
    mail = DigestMailer(user_data)
    #mail.send()

VERSION = '0.1'
USER_AGENT = 'digest for reddit v{} by u/individual_throwaway'.format(VERSION)
    
if __name__ == '__main__':
    main()