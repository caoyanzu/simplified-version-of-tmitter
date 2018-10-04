# -*- coding: utf-8 -*-
#from tmitter.mvc import models
import time
from django.db import connection, models
from django.contrib import admin
from django.utils import timesince,html
from tmitter.utils import formatter,function
from tmitter.settings import *
import PIL
from StringIO import StringIO

class User(models.Model):
    id=models.AutoField(primary_key=True)
	username=models.CharField('用户名',max_length=20)
	password=models.CharField('密码',max_length=100)
	realname=models.CharField('姓名',max_length=20)
	email=models.EmailField('邮箱')
	area=models.ForeignKey(Area,verbose_name='地区')
	face=models.ImageField('头像',upload_to='face/%Y/%m/%d',default='',blank=True)
	url=models.CharField('个人主页',max_length=200,default='',blank=True)
	about=models.TextField('关于我',max_length=1000,default='',blank=True)
	addtime=models.DateTimeField('注册时间',auto_now=True)
	friend=models.ManyToManyField('self',verbose_name='朋友')
	
	def __unicode__(self):
	    return self.realname
		
	def addtime(self):
	    return self.addtime.strftime('%Y/%m/%d %H:%M:%S')
		
	def save(self,modify_pwd=True):
	    if modify_pwd:
		    self.password=function.md5_encode(self.password)
		self.about=formatter.substr(self.about,20,True)
		super(User,self).save()
		
	class Meta:
	    verbose_name=u'用户'
		verbose_name_plural=u'用户'
		
class UserAdmin(models.Model):
    list_display = ('id','username','realname','email','addtime_format')
	list_display_link = ('username','realname','email')
	list_per_page = ADMIN_PAGE_SIZE
		
class Note(models.Model):
    
	id = models.AutoField(primary_key = True)
	message = models.TextField('消息')       #消息数据
	addtime = models.DateTimeField('发布时间',auto_now = True)
	category = models.ForeignKey(Category,verbose_name = '来源')
	user = models.ForeignKey(User,verbose_name = '发布者')
	
	def __unicode__:
	    return self.message
		
	def message_short(self):                       #简略消息
	    return formatter.substr(self.message,30)
		
	def addtime_format_admin(self):                #发布时间
        return self.strftime('%Y-%m-%d %H:%M:%S')

    def user_name(self):                           #获取用户名
        return self.user.realname
	
    def save(self):                                #持久化
        self.message = formatter.content_tiny_url(self.message)
        self.message = html.escape(self.message)
		self.message = formatter.substr(self.message)
		super(Note,self).save()
    
    class Mate:
        verbose_name = u'消息'
        verbose_name_plural = u'消息'
    def get_absolute_url(self):
        return APP_DOMAIN + 'message/%s/' % self.id
	
class NoteAdmin(models.Model):
    list_display = ('id','user_name','message_short','addtime_format_admin','category_name')
    list_display_link = ('id','message_short')
    search_fields = ['message']
    list_per_page = ADMIN_PAGE_SIZE	
	
admin.site.register(Note,NoteAdmin)
admin.site.register(User,UserAdmin)