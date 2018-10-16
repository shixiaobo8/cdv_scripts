#!/usr/bin/env python
# -*- coding:utf8 -*-
"""
	模拟中华云登陆并测试接口
"""

import requests
import time
import sys
import os
import pytesseract
from PIL import Image
reload(sys)
sys.setdefaultencoding('utf8')

main_page = 'http://testconverge.huayun.china.com/converge/loadHotArticles/'
login_page1 = 'http://testconverge.huayun.china.com/login.jsp'
login_page = 'http://testhuayun.china.com/welcome.do?processID=login'
login_action = 'http://testhuayun.china.com/welcome.do?processID=login'
image_url = 'http://testhuayun.china.com/webframework/jsp/image.jsp'

# 建立 session
session_requests = requests.session()


def getImageCode():
# 模拟登陆参数,尝试登陆5次,匹配成功即保存登陆会话退出
	# for i in range(0,5):
	img = session_requests.get(image_url+"?"+str(int(time.time())))
	print session_requests.cookies.get_dict()
	# 删除一样写入的图片
	if os.path.exists("./image.jpg"):
		os.remove("./image.jpg")
	with open("./image.jpg","ab+") as f:
		f.write(img.content)
	# 识别图片验证码
	image = Image.open("./image.jpg")
	image_code = pytesseract.image_to_string(image)
	print image_code
	return image_code.encode('utf-8')

# 登陆
def login():
	login_form_data = {
			"username":"zhonghuayun",
			"password":"111111",
			"image":""
		}
	headers = {
	"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
	"Upgrade-Insecure-Requests": "1",
	"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36",
	"Accept-Encoding": "gzip, deflate, sdch",
	"Accept-Language": "zh-CN,zh;q=0.8",
	"Content-Type":"application/x-www-form-urlencoded"

    	}
	# 提前访问一次(必要)
	result_test = session_requests.post(login_action,headers = headers,data = login_form_data)
	# 重新设置登陆验证码
	login_form_data['image'] = getImageCode()
	print login_form_data
	# 保存登陆结果
	result = session_requests.post(login_action,headers = headers,data = login_form_data)
	print result.cookies.get_dict()

# 测试页面访问数据
def getPageData(test_page):
	post_body_data = {
		"flag":"day",
		"pagesize":"5",
		"centerid":"5",
		}
	res = session_requests.post(test_page,data=post_body_data)
	print res.content
	
if __name__ == '__main__':
	# 必须要登陆才能访问下面的页面,
	login()
	# 测试页面
	#test_url = "http://testconverge.huayun.china.com/converge/loadHotArticles/"
	test_url = "http://testconverge.huayun.china.com/reminding/queryReminding/"
	getPageData(test_url)


