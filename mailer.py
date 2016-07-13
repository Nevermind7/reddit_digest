import smtplib
from email.mime.text import MIMEText
from datetime import datetime as dt

class DigestMailer():
    """Mail class to send Digester results to the user."""
    
    def __init__(self, user_data):
        self.user = user_data['username']
        self.name = 'Reddit_Digest'
        self.address = user_data['mail']
        self.template = self._load_template()
    
    def _load_template(self):
        with open('resources/mail_template', 'r') as template:
            template = template.read()
        return template
        
    def send(self, digested):
        s = smtplib.SMTP('localhost')
        self.msg = MIMEText(self.template.format(**digested))
        self.msg['Subject'] = 'Reddit digest for {} on {}'.format(self.user, 
                                                                    str(dt.today()).split(' ')[0])
        s.sendmail(self.name, self.address, self.msg.as_string())
        s.quit()
