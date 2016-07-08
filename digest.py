import praw
import json
from datetime import datetime as dt
import smtplib
from email.mime.text import MIMEText

class DigestMailer():
    
    def __init__(self, settings):
        self.user = settings['user']
        self.name = 'Reddit_Digest'
        self.address = settings['email']
        self.msg = MIMEText('test')
        self.msg['Subject'] = 'Reddit digest for u/{} on {}'.format(self.user, 
                                                                    str(dt.today()).split(' ')[0])
    def send(self):
        s = smtplib.SMTP('localhost')
        s.sendmail(self.name, self.address, self.msg.as_string())
        s.quit()

class Digester():
    
    def __init__(self, settings, version):
        self.user_agent = 'reddit_digest v{} by u/individual_throwaway'.format(version)
        self.agent = praw.Reddit(user_agent=self.user_agent)
        self.user = self.agent.get_redditor(settings['user'])
    
    def get_karma(self):
        return self.user.comment_karma
    
    def get_subscriptions(self):
        return self.user.get_multireddit()    

def load_settings():
    with open('settings.json', 'r') as _settings:
        settings = json.load(_settings)
    return settings

def main():
    settings = load_settings()    
    digest = Digester(settings, __version__)
    print(digest.get_subscriptions())
    mail = DigestMailer(settings)
    #mail.send()

__version__ = '0.1'
    
if __name__ == '__main__':
    main()