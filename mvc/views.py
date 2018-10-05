# -*- coding: utf-8 -*-
from django.http import HttpResponse,Http404, HttpResponseRedirect, HttpResponseServerError
from django.template import Context, loader
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.core import serializers
#from django.utils.translation import ugettext as _
from mytmitter.settings import *
from mytmitter.mvc.models import Note,User,Category,Area
from mytmitter.mvc.feed import RSSRecentNotes,RSSUserRecentNotes
from mytmitter.utils import mailer,formatter,function,uploader

#登录注册部分
def signup(request):
    #判断是否登录
	_islogin = __is_login(request)
	
	if(_islogin):
	    return HttpResponseRedirect('/')
		
	_userinfo = {
	    'username':'',      #用户信息的数据结构
		'password':'',
		'confirm':'',
		'realname':'',
		'email':'',
	}
	
	try:
	_userinfo = {
	    'username':request.POST['username'],  #从页面获取用户输入
		'password':request.POST['password'],
		'confirm':request.POST['confirm'],
		'realname':request.POST['realname'],
		'email':request.POST['email'],
	}
	except(KeyError):
	    _is_post = False
		
	if(_is_post):
	    _state=__do_signup(request,_userinfo)
	else:
	    _state = {
		    'success':False
			'message':'Signup'
		}
		
	if(_state['success']):   #如果注册成功，返回成功界面
	    return __result_message(request,'Signup successed','Your account was registed success.')
		
	_result = {            #显示注册信息
	    'success':_state['success'],
		'message':_state['message'],
		'form':{
		    'username':_userinfo['username'],
			'realname':_userinfo['realname'],
			'email':_userinfo['email'],
		}
	}
    #body content
    _template = loader.get_template('signup.html')  #渲染注册页面

    _context = {
	    'page_title':'Signup',
		'state':_result,
	}	
	
	_output = _template.render(_context)
	return HttpResponse(_output)
	
def __do_signup(request,_userinfo):
    _state={
	    'success':'False',
		'message':'',
	}
	
	#检查输入合法性,初始的'success'状态是False，所以不用每次重新赋值
	if (_userinfo['username']==''):
	    _state['message']='用户名未输入'
		return _state
	
	if (_userinfo['password']==''):
	    _state['message']='未输入密码'
		return _state
	
	if (_userinfo['realname']==''):
	    _state['message']='未输入真实姓名'
		return _state
		
	if (_userinfo['email']==''):
	    _state['message']='未输入邮件地址'
		return _state
	
    #编写__check_username_exist函数用于检测用户名是否被注册	
	if (__check_username_exist(_userinfo['username'])):  
	    _state['message']='用户名已经被注册'
		return _state
	
	if (_userinfo['confirm']!=_userinfo['password']):
	    _state['message']='两次输入不一致'
		return _state
		
	_user=User(
	    username = _userinfo['username'],
		realname = _userinfo['realname'],
		password = _userinfo['password'],
		email = _userinfo['email'],
		area = Area.objects.get(id=1),
	)

	try:
	    _user.save()
	    _state['success']='True'
	    _state['message']='successed'
	except:
	    _state['success'] = False
		_state['message'] = '程序异常，注册失败'
	mailer.send_regist_success_mail(_userinfo)
	return _state
	
def __check_username_exist(_username):  #__do_signup中检测用户名是否被注册，传入用户输入的用户名，在models中找是否已存在
    _exist = True
	
	try :
	    _user = User.objects.get(username = _username)
		_exist = True
	except(User.DoesNotExist):
	    _exist = False
		
	return _exist
	
def signin(request):
    #首先获取用户登录状态信息,写一个__is_login函数用来获取用户的登录状态
	_islogin = __is_login(request)
	
	try:
	    #获取用户提交的用户名和密码
		_username = request.POST['username']
		_password = request.POST['password']
		_is_post = True
	except(KeyError):
	    _is_post = False
	
	#检查用户名和密码是否输入正确
	if _is_post:
	    #__do_login是用来执行登录操作的函数,登录成功会返回'success'=True的状态
	    _state = __do_login(request,_username,_password)
	
	    if _state['success']:
		    return __result_message(request,'Login successed','you are logining now')
			
	else:
	    _state = {
		    'success':False
			'message':'Pls login first'
		}
	#页面内容，填充模板文件signin.html
	_template = loader.get_template('signin.html')
	_context = {
	    'page_title' : 'Signin'
		'state' : _state
	}
	_output = _template.render(_context)
	return HttpResponse(_output)
	
def __is_login(request):    #判断是否登录，会多次用到
    return request.session.get('islogin',False)
	
def __do_login(request,_username,_password):
    #首先检查登录时输入的用户名和密码是否匹配
	_state = __check_login(_username,_password)
	
	if _state['success']:
	    #把登录信息保存到session
		request.session['islogin'] = True
		request.session['userid'] = _state['userid']
	    request.session['username'] = _username
		request.session['realname'] = _state['realname']
		
	return _state
	
def __check_login(_username,_password):   #实际的登录操作在__check_login中完成
    _state = {
	    'success':True,
		'message':'none',
		'userid':-1,
		'realname':'',
	}
	
	try:
	    #在User这张表中查找传入的用户名
	    _user = User.objects.get(username = _username)
		
		if (_user.password == function.md5_encode(_password)):
		    _state['success'] = True
			_state['userid'] = _user.id
			_state['realname'] = _user.realname
		else:
		    _state['success'] = False
			_state['message'] = '密码不正确'
    except(User.DoesNotExist):
	    _state['success'] = False
        _state['message'] = 'User does exist'
    
	return _state	

def signout(request):
    request.session['islogin'] = False
    request.session['userid'] = -1
	request.session['username'] = ''
	
	return HttpResponseRedirect('/')

#信息显示函数，用于用户做出操作后显示相应的信息，会多次用到	
def __result_message(request,_title = 'Message',message = 'Unknow error',_go_back_url = ''):
    _islogin = __is_login(request)
	
	if _go_back_url =='':
	    _go_back_url = function.get_referer_url(request)
		
	_template = loader.get_template('result_message.html')
	_context = Context({
	    'page_title':_title,
		'message':_message,
		'go_back_url':_go_back_url,
		'islogin':_islogin
	})
	_output = _template.render(_context)
	return HttpResponse(_output)
	
#信息发布和浏览部分
def index(request):
    return index_user(request,'')

def index_user(request,_username):  #用户消息界面
    return index_user_page(request,_username,1)
	
def index_user_self(request):   #自己的消息界面
    _user_name = __user_name(request)
	return index_user(request,_user_name)

def index_page(request,_page_index):   #页数查找
    return index_user_page(request,'',_page_index)

#信息发布功能	
def index_user_page(request,_username,_page_index):
    #获取用户的登录状态
	_islogin = __is_login(request)
	_page_title = 'Home'
	
    try:
	    #获取POST提交的消息
	    _message = request.POST['message']
		_is_post = True
	except(KeyError):
	    _is_post = False
	
	#保存消息
	if _is_post:
	    if not _islogin:
		    return HttpResponseRedirect('/signip/')
		#保存消息
		(_category,_is_added_cate) = Category.objects.get_or_create(name='网页')
		
		try:
		    _user = User.objects.get(id = __user_id(request))  #获得当前登录用户
		except:
		    return HttpResponseRedirect('/signin/')
		
        #初始化模型类Note实例，并保存		
		_note = Note(
		    message = _message,
			category = _category,
			user = _user,
		)
		_note.save()
		
		return HttpResponseRedirect('/user/'+_user.username)
		
	_userid = -1
	

	#获取朋友消息列表
	_offset_index = (int(_page_index)-1)*PAGE_SIZE   #根据页码数_page_index计算读取消息的索引范围
	_last_item_index = PAGE_SIZE * int(_page_index)
	
	#获取朋友，首先检查登录状态，如果登录，可以获取登录用户的朋友
	_login_user_friend_list = None   #初始化朋友列表为空
	
	if _islogin:
	    _login_user = User.objects.get(username = __user_name(request))
		_login_user_friend_list = _login_user.friend.all()
	else:
	    _login_user = None
	
	_friends = None
	_self_home = False
	if _username != '':   #只获取某个用户的消息
	    _user = get_object_or_404(User,username = _username)
		_userid = _user.id
		_notes = Note.objects.filter(user = _user).order_by('-addtime')
		_page_title = '%s' %_user.realname
		#获取朋友列表
		_friends = _user.friend.order_by('id')[0:FRIEND_LIST_MAX]
		print ('..................',_friends)
		if userid ==__user_id(request):
		    _self_home = True
	else:                 #获取所有的消息
	    _user = None
		if _islogin:
		    _query_users = [_login_user]
			_query_users.extend(_login_user.friend.all())
			_notes = Note.objects.filter(user__in = _query_users).order_by('-addtime')
		else:   #不能获取到消息
		    _notes = []
	
	#使用分页工具分页
	_page_bar = formatter.pagebar(_notes,_page_index,_username)
	
	#获取通用页面
	_notes = _notes[_offset_index:_last_item_index]
	
	#消息体
	_template = loader.get_template('index.html')
	
	_context = {
	    'page_title':_page_title,
		'notes':_notes,
		'islogin':_islogin,
		'userid':__user_id(request),
		'self_home':_self_home,
		'user':_user,
		'page_bar':_page_bar,
		'friends':_friends,
		'login_user_friend_list':_login_user_friend_list,
	}
	_output = _template.render(_context)
	
	return HttpResponse(_output)
	
def __user_id(request):
    return request.session.get('userid',-1)
	
def __user_name(request):
    return request.session.get('username','')
	
	
#详细内容视图
def detail(request,_id):
    _islogin = __is_login(request)
	
	_note = get_object_or_404(Note,id = _id)
	
	_template = loader.get_template('detail.html')
	_context = {
	    'page_title':'%s\'s message %s' % (_note.user.realname,_id),
		'item':_note,
		'islogin':_islogin,
		'userid':__user_id(request),
	}
	_output = _template.render(_context)
	
	return HttpResponse(_output)
	
def detail_delete(request,_id):
    _islogin = __is_login(request)
	
	_note = get_object_or_404(Note,id = _id)
	
	_message = ''
	
	try:
	    _note.delete()
		_message = 'Message deleted'
	except:
	    _message = 'delete failed'
	
	return __result_message(request,'Message %s' %_id,_message)
	

#朋友管理部分	
def user_index(request):   #对user_list函数的简单封装,默认传入参数1，即第一页的用户列表
    return user_list(request,1)
	
def user_list(request,_page_index = 1):
    _islogin = __is_login(request)
	
	_page_title = 'Everyone'
	_user = User.objects.order_by('-addtime')
	
	_login_user = None
	_login_user_friend_list = None
	
	if _islogin:
	    try:
		    _login_user = User.objects.get(
			id = __user_id(request)
			)
			_login_user_friend_list = _login_user.frined.all()
		except:
		    _login_user = None
			
	_page_bar = formatter.pagebar(_user,_page_index,'','control/userlist_pagebar.html')#分页
	
	_offset_index = (int(_page_index)-1)*PAGE_SIZE  #计算当前页的起止记录
	_last_item_index = PAGE_SIZE * int(_page_index) 
	
	_users = _users[_offset_index:_last_item_index]
	
	#内容
	_template = loader.get_template('user_list.html')
	
	_context = {
	'page_title':_page_title,
	'users':_users,
	'login_user_friend_list':_login_user_friend_list,
	'islogin':_islogin,
	'userid':__user_id(request),
	'page_bar':_page_bar,
	}
	_output = _template.render(_context)
	
	return HttpResponse(_output)
	
def friend_add(request,_username):   #添加朋友
    _islogin = __is_login(request)
	
	if not _islogin:                 #未登陆则不允许添加朋友
	    return HttpResponseRedirect('/signin/')
	
	_state = {
	'success':False,
	'message':'',
	}
	
	_user_id = __user_id(request)
	
	try:
	    _user = User.objects.get(id = _user_id)
	except:
	    return __result_message(request,'sorry','this user is not exist')
		
	try:           #实际的添加朋友操作在这个地方完成
	    _friend = User.objects.get(username = _username)  #获取被添加朋友的实例
		_user.friend.add(_friend)
		return __result_message(request,'操作成功')
	except:
	    return __result_message(request,'sorry','这个用户不存在')

#个人资料配置		
def settings(request):   
    _islogin = __is_login(request)
	
	if not _islogin:
	    return HttpResponseRedirect('/signin/')
	_user_id = __user_id(request)
	try:
	    _user = User.objects.get(id = _user_id)
	except:
	    return HttpResponseRedirect('/signin/')
		
	if request.method =='POST':
	    _userinfo = {
		'realname':request.POST['realname'],    #用户真名
		'url':request.POST['url'],              #个人主页
		'email':request.POST['email'],          #邮件地址
		'face':request.FILES.get['face',None],  #头像
		'about':request.POST['about'],          #关于（简介）
		}
		_is_post = True
	else:
    _is_post = False
    
    _state = {
	'message':'',
	}
	
	if _is_post:
	    _user.realname = _userinfo['realname']
		_user.url = _userinfo['url']
		_user.email = _userinfo['email']
		_user.about = _userinfo['about']
		_file_obj = _userinfo['face']
		
		try:
		    if _file_obj:
			    _upload_state = uploader.upload_face(_file_obj)
				if _upload_state['success']:
				    _user.face = _upload_state['message']
				else:
				    return __result_message(request,'error',_upload_state['message'])
			
			_user.save(False)
			_state['message'] = 'successed'
		except:
		    return __result_message(request,'错误','提交数据异常')
			
	_template = loader.get_template('settings.html')
	_context = {
	'page_title':Profile,
	'state':_state,
	'islogin':_islogin,
	'user':_user,
	}
	_output = _template.render(_context)
	
	return HttpResponse(_output)
		
def friend_remove(request,_username):
    _islogin = __is_login(request)
	
	if not _islogin:
	    return HttpResponseRedirect('/signin/')
		
	_state = {
	'success':False,
	'message':'',
	}
	
	_user_id = __user_id(request)
	
	try:
	    _user = User.objects.get(id = _user_id)
	except:
	    return __result_message(request.'sorry','用户不存在')
		
	try:
	    _friend = User.objects.get(username = _username)
		_user.friend.remove(_friend)
		return __result_message(request,'successed','该用户已成功移除')
	except:
	    return __result_message(request,'failed','移除用户失败')

		

def api_note_add(request):
    #获取查询参数
	_username = request.GET['uname']
	_password = function.md5_encode(request.GET['pwd'])
	_message = request.GET['msg']
	_from = request.GET.['from']
	
	#获取用户信息和检查用户
	try:
	    _user = User.objects.get(username = _username,password = _password)
	except:
	    return HttpResponse('-2')
		
	#获取分类信息，如果不存在则创建一个新的分类
	(_cate,_is_added_cate) = Category.objects.get_or_create(name = _from)
	
	try:
	    _note = Note(message = _message,user = _user,category = _cate)
		_note.save()
		return HttpResponse('1')
	except:
	    return HttpResponse('-1')
