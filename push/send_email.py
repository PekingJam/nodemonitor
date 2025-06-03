import smtplib
from email.mime.text import MIMEText
from smtplib import SMTP_SSL
from email.header import Header


class SendEmail(object):
    @staticmethod
    def send_email(title, msg):
        # 设置服务器所需信息
        # 163邮箱服务器地址
        mail_host = 'smtp.163.com'
        # 163用户名
        mail_user = 'fleeword@163.com'
        # 密码(部分邮箱为授权码)
        mail_pass = 'fdfafdfafdfa'
        # 邮件发送方邮箱地址
        sender = 'dfadfafda'
        # 邮件接受方邮箱地址，注意需要[]包裹，这意味着你可以写多个邮件地址群发
        receivers = ['dafdfadfaf']

        # 设置email信息
        # 邮件内容设置
        message = MIMEText(msg, 'plain', 'utf-8')
        # 邮件主题
        message['Subject'] = title
        # 发送方信息
        message['From'] = Header("自动更新订阅程序", "utf-8")
        # 接受方信息
        message['To'] = receivers[0]

        # 登录并发送邮件
        try:
            # smtpObj = smtplib.SMTP()
            # 连接到服务器
            # smtpObj.connect(mail_host, 587)
            smtp = SMTP_SSL(mail_host)
            # 登录到服务器
            smtp.login(mail_user, mail_pass)
            # 发送
            smtp.sendmail(
                sender, receivers, message.as_string())
            # 退出
            smtp.quit()
            print('send email success')
        except smtplib.SMTPException as e:
            print('send email error', e)  # 打印错误