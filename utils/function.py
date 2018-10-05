# -*- coding:utf-8 -*-
import md5

def md5_encode(passward):       #把传进来的密码md5编码以后返回以供校对
    return md5.new(passward).hexdigest()
	
def get_referer_url(request):   #获取用户上一次访问的URL
    return request,META.get('HTTP_REFERER','/')