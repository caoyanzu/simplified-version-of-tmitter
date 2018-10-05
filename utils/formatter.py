# -*- coding: utf-8 -*-
import re,urllib
from tmitter.settings import *
from django.shortcuts import render_to_response
from django.template import context
from django.core.paginator import Paginator, InvalidPage


def tiny_url(url):
    #将url转化成tinyurl
    apiurl = 'http://tinyurl.com/api-create.php?url='
    tinyurl = urllib.urlopen(apiurl+url).read()
    return tinyurl
	
def content_tiny_url(content):
    #将消息里的连接转化成更短的tinyurl
    regex_url = r'http:\/\/([\w.]+\/?)\S*'
    for match in refinditer(regex_url,content):
        url = match.group(0)
        content = content.replace(url,tiny_url(url))
        return content
	
def substr(content,length,add_dot = True):
    #截取字符串
    if(len(content) > length):
        content = content[:length]
        if(add_dot):
            content = content[:len(content)-3] + '...'
    return content
	
def pagebar(objects,page_index,username = '',template = 'control/home_pagebar.html'):
    #生成HTML分页条：用传入的参数渲染home_pagebar.html模板
    #objects是数据列表
    #page_index是当前页数
    #username是当前被访问的空间的用户名，没有则传空
    #template是分页模板
    page_index = int(page_index)
    _paginator = Paginator(objects,PAGE_SIZE)
    
    if (username):
        template = 'control/user_pagebar.html'
    	
    return render_to_response(template,{
        'paginator':_paginator,
    	'username':username,
    	'has_pages':_paginator.num_pages>1,
    	'has_next':_paginator.page(page_index).has_next(),
    	'has_prev':_paginator.page(page_index).has_previous(),
    	'page_index':page_index,
    	'page_next':page_index+1,
    	'page_prev':page_index-1,
        'page_count':_paginator.num_pages,
       	'row_count':_paginator.count,
    	'page_nums':range(_paginator.num_pages+1)[1:],
        }).content
