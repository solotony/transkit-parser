import smtplib
import logging

def send_notification(subject, body):
    sender = 'akpp@mskakpp.ru'
    recipient = 'akpp@mskakpp.ru'
    sender_password = "Ali22na03"


    try:
        mail_lib = smtplib.SMTP_SSL('smtp.yandex.ru', 465)
        mail_lib.login(sender, sender_password)
        headers = [
            f'From: {sender}',
            f'To: {recipient}',
            'Content-Type: text/plain; charset="utf-8"',
            f'Subject: {subject}'
        ]
        msg = '\r\n'.join(headers) + '\r\n\r\n' + body
        mail_lib.sendmail(sender, recipient, msg.encode('utf8'))
        mail_lib.quit()
    except Exception as e:
        logging.exception(e)