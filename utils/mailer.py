# -*- coding:utf-8 -*-
from django core.mail import send_mail

FROM_EMAIL = 'see_spiker@163.com'

MAIL_FOOT = '''<br/>spiker<br/>
<a href = 'http://www.tmitter.com">tmitter.com</a>'''

def send_regist_success_mail(userinfo):
    subject = u'注册成功'
	body = u'''你已经成为tmitter用户，以下是你的用户信息:
	<ul>
	<li>用户名：%s</li>
	<li>密码：%s</li>
	</ul>''' %(userinfo['username'],userinfo['password'])
	recipient_list = [userinfo['email']]
	send(subject,body,recipient_list)
	
def send(subject,body,recipient_list):
    body += MAIL_FOOT
	send_mail(subject,body,FROM_EMAIL,recipient_list)
	
def test(request):
    send_regist_success_mail({
	    'username':'spiker',
		'password':'123',
		'email':'see_spiker@163.com',
		'realname':'spiker',
	})