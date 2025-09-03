from django.core import mail
from celery import shared_task
from django.utils.html import strip_tags
from django.conf import settings
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

@shared_task(name="send_email")
def send_email(mail_subject, message, to):
    # k = smtplib.SMTP_SSL(settings.EMAIL_HOST,settings.EMAIL_PORT)
    # k.connect(settings.EMAIL_HOST,settings.EMAIL_PORT)
    # k.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
    
    # message_body = MIMEText(message, 'HTML', 'utf-8')
    # message_body['From'] = formataddr(['社团联技术顾问', settings.EMAIL_HOST_USER])
    # message_body['Subject'] = Header(mail_subject,'utf-8')

    # k.sendmail(settings.EMAIL_HOST_USER,to,message_body.as_string())
    # k.quit()
    
    with smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT) as k:
            k.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)

            msg = MIMEText(message, 'html', 'utf-8')
            msg['From'] = formataddr(['社团联技术顾问', settings.EMAIL_HOST_USER])
            msg['To'] = to
            msg['Subject'] = Header(mail_subject, 'utf-8')

            k.sendmail(settings.EMAIL_HOST_USER, [to], msg.as_string())
            
    # plain_message = strip_tags(message)

    # mail.send_mail(mail_subject, plain_message, settings.FROM_EMAIL, to, html_message = message)
    
    # email = EmailMessage(
    #     mail_subject,
    #     message,
    #     to=to
    # )

    # # print("sending email")

    # email.send()
    
def send_email_nosync(mail_subject, message, to):

    # k = smtplib.SMTP_SSL(settings.EMAIL_HOST,settings.EMAIL_PORT)
    # k.connect(settings.EMAIL_HOST,settings.EMAIL_PORT)
    # k = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
    # # k.starttls()
    # # k.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
    
    # message_body = MIMEText(message, 'HTML', 'utf-8')
    # message_body['From'] = formataddr(('社团联技术顾问', settings.EMAIL_HOST_USER))
    # message_body['Subject'] = Header(mail_subject,'utf-8')

    # k.sendmail(settings.EMAIL_HOST_USER,to,message_body.as_string())
    # k.quit()
    
    smtp_server = 'smtp.163.com'
    smtp_port = 465
    email_user = 'hsefz_technician@163.com'
    email_password = 'abcdefg'

    server = smtplib.SMTP_SSL(smtp_server, smtp_port)
    server.login(email_user, email_password)

    if isinstance(to, list):
        to_header = ', '.join(to)
    else:
        to_header = to

    message_body = MIMEText(message, 'HTML', 'utf-8')
    message_body['From'] = formataddr(('社团联技术顾问', email_user))
    message_body['To'] = to_header
    message_body['Subject'] = Header(mail_subject, 'utf-8')

    server.sendmail(email_user, to, message_body.as_string())
    server.quit()
