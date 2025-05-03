import smtplib
import utils.logs as logs
from .database import config, path


LOGER = logs.get_logger(path.basename(__file__))


def send_email(recipient: str, passwd: str) -> bool:
    """
    Send email
    """
    body = f"From: {config['Email']['user']}\n" \
           f"To: {recipient}\n" \
           "Subject: Reseted password to vHub\n" \
           "MIME-Version: 1.0\n" \
           "Content-Type: text/plain; charset=utf-8\n" \
           "Your password has been reset.\n\n" \
           f"Your new password {passwd}"
              
    try:
        if not config['Email'].getboolean('email'):
            raise Exception('Option disable.')
        smtp = smtplib.SMTP(config['Email']['host'], config['Email'].getint('port'))
        smtp.starttls()
        smtp.ehlo()
        smtp.login(config['Email']['user'], config['Email']['password'])
        smtp.sendmail(
            config['Email']['user'],
            recipient,
            body.encode('utf-8')
            )
        LOGER.info(f'{send_email.__name__}(): send email to "{recipient}".')
        return True
    except Exception as err:
        LOGER.error(f'{send_email.__name__}(): fail send email to "{recipient}".\n{err}.')
        return False


if __name__ == '__main__':
    pass
