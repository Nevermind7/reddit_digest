import praw
import json
from datetime import datetime as dt
import time
import smtplib
from email.mime.text import MIMEText
import OAuth2Util
import sqlite3

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
        return (self.comment_karma - comment_karma_old,
                self.link_karma - link_karma_old)
    
    def update_user_db(self):
        with sqlite3.connect('user_data.db') as conn:
            c = conn.cursor()
            c.execute("UPDATE users SET comment_karma=?, link_karma=?\
                       WHERE username=?", (self.comment_karma, 
                                           self.link_karma, 
                                           self.user_data['username']))
    
    def get_subscriptions(self):
        self.o.refresh()
        return [str(x) for x in self.r.get_my_subreddits()]

def load_user_data_from_db():
    columns = ['username', 'comment_karma', 'link_karma', 'mail']
    with sqlite3.connect('user_data.db') as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM users")
        data = c.fetchone()
        return {x: data[x] for x in columns}

def main():
    user_data = load_user_data_from_db()
    digest = Digester(USER_AGENT, user_data)
    print(digest.get_karma_change())
    digest.update_user_db()
    mail = DigestMailer(user_data)
    #mail.send()

VERSION = '0.1'
USER_AGENT = 'digest for reddit v{} by u/individual_throwaway'.format(VERSION)
    
if __name__ == '__main__':
    main()