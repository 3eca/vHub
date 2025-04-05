import smtplib
from os import environ, path
import utils.logs as logs


LOGER = logs.get_logger(path.basename(__file__))


def send_email(recipient: str, passwd: str) -> bool:
    """
    Send email
    """
    body = f"From: {environ['VHUB_SMTP_USER']}\n" \
           f"To: {recipient}\n" \
           "Subject: Reseted password to vHub\n" \
           "MIME-Version: 1.0\n" \
           "Content-Type: text/plain; charset=utf-8\n" \
           "Your password has been reset.\n\n" \
           f"Your new password {passwd}"
              
    try:
        smtp = smtplib.SMTP(environ['VHUB_SMTP_SRV'], int(environ['VHUB_SMTP_PORT']))
        smtp.starttls()
        smtp.ehlo()
        smtp.login(environ['VHUB_SMTP_USER'], environ['VHUB_SMTP_PWD'])
        smtp.sendmail(
            environ['VHUB_SMTP_USER'],
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
