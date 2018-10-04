# -*- coding: utf-8 -*-
from django.http import HttpResponse,Http404, HttpResponseRedirect, HttpResponseServerError
from django.template import Context, loader
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.core import serializers
from django.utils.translation import ugettext as _
from tmitter.settings import *
from tmitter.mvc.models import Note,User,Category,Area
from tmitter.mvc.feed import RSSRecentNotes,RSSUserRecentNotes
from tmitter.utils import mailer,formatter,function,uploader

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
			'message':_('Signup')
		}
		
	if(_state['success']):   #如果注册成功，返回成功界面
	    return __result_message(request,_('Signup successed'),_('Your account was registed success.'))
		
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
	    'page_title':_('Signup'),
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
	    _state['message']=_('用户名未输入')
		return _state
	
	if (_userinfo['password']==''):
	    _state['message']=_('未输入密码')
		return _state
	
	if (_userinfo['realname']==''):
	    _state['message']=_('未输入真实姓名')
		return _state
		
	if (_userinfo['email']==''):
	    _state['message']=_('未输入邮件地址')
		return _state
	
    #编写__check_username_exist函数用于检测用户名是否被注册	
	if (__check_username_exist(_userinfo['username'])):  
	    _state['message']=_('用户名已经被注册')
		return _state
	
	if (_userinfo['confirm']!=_userinfo['password']):
	    _state['message']=_('两次输入不一致')
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
	    _state['message']=_('successed')
	except:
	    _state['success'] = False
		_state['message'] = _('程序异常，注册失败')
	mailer.send_regist_success_mail(_userinfo)
	return _state

#__do_signup中检测用户名是否被注册，传入用户输入的用户名，在models中找是否已存在	
def __check_username_exist(_username):
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
		    return __result_message(request,_('Login successed'),_('you are logining now'))
			
	else:
	    _state = {
		    'success':False
			'message':'Pls login first'
		}
	#页面内容，填充模板文件signin.html
	_template = loader.get_template('signin.html')
	_context = {
	    'page_title' : _('Signin')
		'state' : _state
	}
	_output = _template.render(_context)
	return HttpResponse(_output)
	
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

#实际的登录操作在__check_login中完成	
def __check_login(_username,_password):
    _state = {
	    'success':True,
		'message':'none',
		'userid':-1,
		'realname':'',
	}
	
	try:
	    #在User这张表中查找传入的用户名
	    _user = User.objects.get(username = _username)
		
		if (_user.password ==function.md5_encode(_password)):
		    _state['success'] = True
			_state['userid'] = _user.id
			_state['realname'] = _user.realname
		else:
		    _state['success'] = False
			_state['message'] = _('密码不正确')
    except(User.DoesNotExist):
	    _state['success'] = False
        _state['message'] = _('User does exist')
    
	return _state	

def signout(request):
    request.session['islogin'] = False
    request.session['userid'] = -1
	request.session['username'] = ''
	
	return HttpResponseRedirect('/')
	
def __result_message(request,_title = 'Message',message = _('Unknow error'),_go_back_url = ''):
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
	
#视图方法
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
	_page_title = _('Home')
	
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
		(_category,_is_added_cate) = Category.objects.get_or_create(name=u'网页')
		
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
		_page_title = u'%s' %_user.realname
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
	    'page_title':_(%s\'s message %s) % (_note.user.realname,_id),
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
		_message = _('Message deleted')
	except:
	    _message = _('delete failed')
	
	return __result_message(request,_('Message %s') %_id,_message)