"""mytmitter URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,patterns,include
from mytmitter.mvc.feed import RSSRecentNotes,RSSUserRecentNotes
import mytmitter, django
import mytmitter.mvc.views
import django.contrib.syndication.views 
import django.views.static
import django.conf.urls.i18n
from django.conf import settings
from django.conf.urls.static import static

admin.autodiscover()

rss_feeds = {
    'recent': RSSRecentNotes,
}

rss_user_feeds = {
    'recent': RSSUserRecentNotes,
}

urlpatterns = [
    path('admin/', admin.site.urls),  #后台站点管理
	path('',mytmitter.mvc.views.index),  #消息发布页面，主页
	path('p/(?p<_page_index>\d+)',mytmitter.mvc.views.index_page),  #消息发布页面，分页
	#查看登陆用户
	path('user/',mytmitter.mvc.views.index_user_self),
	#查看指定用户
	path('user/(?p<_username>)[a-zA-Z\-_\d]+',mytmitter.mvc.views.index_user,name='mytmitter-mvc-views-index_user'),
	#查看指定用户的消息分页
	path('user/(?p<_username>[a-zA-Z\-_\d]+)/(?p<_page_index>\d+)/',mytmitter.mvc.views.index_user_page),
	#查看所有用户朋友
	path('users/',mytmitter.mvc.views.users_index),
	#查看所有用户分页
	path('users/(?p<_page_index>\d+)/',mytmitter.mvc.views.users_list),
	#登陆
	path('signin',mytmitter.mvc.views.signin),
	#登出
	path('signout',mytmitter.mvc.views.signout),
	#注册
	path('signup',mytmitter.mvc.views.signup),
	#修改登陆用户的信息
	path('settings/',mytmitter/mvc.views.settings.name='mytmitter-mvc-views-settings'),
	#消息详情页面
	path('message/(?p<_id>\d+)/',mytmitter.mvc.views.detail,name='mytmitter-mvc-views-detail'),
	#删除单条消息
	path('message/(?p<_id>)d+/delete/',mytmitter.mvc.views.detail_delete,name='mytmitter-mvc-views-detail_delete'),
	#添加朋友
	path('friend/add/(?p<_username>[a-zA-Z\-_\d]+)',mytmitter.mvc.views.friend_add,name='mytmitter-mvc-views-friend_add'),
	#删除朋友
	path('friend/remove/(?p<_username>[a-zA-Z\-_\d]+)',mytmitter.mvc.views.friend_remove),
	#发布消息
	path('api/note/add/',mytmitter.mvc.views.api_note_add),
	path('feed/rss/(?P<url>.*)/', django.contrib.syndication.views.Feed, {'feed_dict': rss_feeds}),
    path('user/feed/rss/(?P<url>.*)/', django.contrib.syndication.views.Feed, {'feed_dict': rss_user_feeds}),
]+static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
