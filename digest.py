import praw
import json
from datetime import datetime as dt
import smtplib
from email.mime.text import MIMEText


__version__ = '0.1'

r = praw.Reddit(user_agent='reddit_digest v{} by u/individual_throwaway'.format(__version__))

with open('settings.json', 'r') as _settings:
    settings = json.load(_settings)

class DigestMailer():
    def __init__(self, settings):
        self.user = settings['user']
        self.name = 'Reddit Digest'
        self.address = settings['email']
        self.msg = MIMEText()
        self.msg['Subject'] = 'Reddit digest for u/{} on {}'.format(self.user, 
                                                                    dt.today().split(' ')[0])
        
    def send(self):
        s = smtplib.SMTP('localhost')
        s.sendmail(self.name, self.email, msg.as_string())
        s.quit()