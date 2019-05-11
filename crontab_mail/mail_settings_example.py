import smtplib
from email.mime.text import MIMEText

MAIL_SERVER = 'smtp.163.com'  # 发送邮件服务器
MAIL_PORT = 465  # 服务端口
MAIL_USE_SSL = True  # 是否使用SSL传输
MAIL_USERNAME = 'XXX@163.com'  # 发送邮件服务器登录用户名
MAIL_PASSWORD = 'XXX'  # 登录密码
MAIL_DEFAULT_SENDER = 'XXX@163.com'  # 默认发件邮箱，默认同登录用户名
MAIL_DEFAULT_RECEIVERS = 'XXX@XX.com'  # 默认收件邮箱，收取报警信息的邮箱
'''
多个邮箱请在send_mail函数内receivers参数列表内用逗号隔开
'''


def send_mail(subject,
              body,
              sender=MAIL_DEFAULT_SENDER,
              receivers=[MAIL_DEFAULT_RECEIVERS]):

    message = MIMEText(body, 'plain', 'utf-8')
    message['Subject'] = subject
    message['From'] = "{}".format(sender)
    message['To'] = ",".join(receivers)

    try:
        smtpObj = smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT)
        smtpObj.login(MAIL_USERNAME, MAIL_PASSWORD)
        smtpObj.sendmail(sender, receivers, message.as_string())
    except Exception as e:
        print(e)


if __name__ == '__main__':
    Subject_test = 'hello test'
    body_test = 'this is test mail from flask-mail'
    send_mail(Subject_test, body_test)
