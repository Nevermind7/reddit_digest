import smtplib
from email.mime.text import MIMEText
from datetime import datetime as dt

class DigestMailer():
    """Mail class to send Digester results to the user."""
    
    def __init__(self, user_data):
        self.user = user_data['username']
        self.name = 'Reddit_Digest'
        self.address = user_data['mail']
        self.content = ''
        
    def send(self):
        s = smtplib.SMTP('localhost')
        self.msg = MIMEText(self.content)
        self.msg['Subject'] = 'Reddit digest for u/{} on {}'.format(self.user, 
                                                                    str(dt.today()).split(' ')[0])
        s.sendmail(self.name, self.address, self.msg.as_string())
        s.quit()
        
    def add_content(self, ext):
        self.content += str(ext) + '\n\n'