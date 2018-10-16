#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
	阿里云录播播放sdk测试
"""
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import MySQLdb as mdb
import json,datetime,time
import aliyunsdkcore
import requests
import xlrd,os,sys,xlwt
from aliyunsdkcore import client
from aliyunsdkvod.request.v20170321 import GetPlayInfoRequest
from aliyunsdkvod.request.v20170321 import GetVideoPlayAuthRequest
from aliyunsdkvod.request.v20170321 import GetVideoListRequest
from aliyunsdkvod.request.v20170321 import GetCategoriesRequest

# 初始化客户端
def init_vod_client(accessKeyId, accessKeySecret):
    regionId = 'cn-shanghai'   # 点播服务所在的Region，国内请填cn-shanghai，不要填写别的区域
    connectTimeout = 10        # 连接超时，单位：秒。连接失败默认会自动重试，且最多重试3次
    return client.AcsClient(accessKeyId, accessKeySecret, regionId, auto_retry=True, max_retry_time=3, timeout=connectTimeout)

# 获取播放地址
def get_play_info(clt, videoId):
    request = GetPlayInfoRequest.GetPlayInfoRequest()
    request.set_accept_format('JSON')
    request.set_VideoId(videoId)
    request.set_AuthTimeout(3600*24)     # 播放地址过期时间（只有开启了URL鉴权才生效），默认为3600秒，支持设置最小值为3600秒
    response = json.loads(clt.do_action(request))
    return response

# 获取播放凭证 
def get_video_playauth(clt, videoId):
    request = GetVideoPlayAuthRequest.GetVideoPlayAuthRequest()
    request.set_accept_format('JSON')
    request.set_VideoId(videoId)
    request.set_AuthInfoTimeout(3600)    # 播放凭证过期时间，默认为100秒，取值范围100~3600；注意：播放凭证用来传给播放器自动换取播放地址，凭证过期时间不是播放地址的过期时间
    response = json.loads(clt.do_action(request))
    return response




# 获取视频播放列表
def get_video_list(clt,page):
    request = GetVideoListRequest.GetVideoListRequest()
    utcNow = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    utcMonthAgo = datetime.datetime.utcfromtimestamp(time.time() - 30*86400).strftime("%Y-%m-%dT%H:%M:%SZ")
    request.set_StartTime(utcMonthAgo)   # 视频创建的起始时间，为UTC格式
    request.set_EndTime(utcNow)          # 视频创建的结束时间，为UTC格式
    request.set_Status('Uploading,Normal,Transcoding')  # 视频状态，默认获取所有状态的视频，多个用逗号分隔
    #request.set_CateId(0)               # 按分类进行筛选
    request.set_PageNo(page)
    request.set_PageSize(200)
    request.set_accept_format('JSON')
    response = json.loads(clt.do_action(request))
    return response

# 获取视频分类
# 获取指定的分类信息，及其子分类（即下一级分类）的列表
def get_categories(clt, cateId=-1, pageNo=1, pageSize=10):
    request = GetCategoriesRequest.GetCategoriesRequest()
    request.set_CateId(cateId)         # 分类ID，默认为根节点分类ID即-1
    request.set_PageNo(pageNo)
    request.set_PageSize(pageSize)
    request.set_accept_format('JSON')
    response = json.loads(clt.do_action(request))
    return response



# 下载视频
def download_mp4(vid):
	try:
		play_info = get_play_info(clt,vid)
		urls = play_info['PlayInfoList']['PlayInfo']
		mp4_url = ''
		for url in urls:
			if url['Format'] == 'mp4' and url['Definition'] == 'FD':
				mp4_url = url['PlayURL']
				local_mp4 = '/www/mp4_download/'+vid+'.mp4'
				print "正在下载视频: " + mp4_url
				if not os.path.exists(local_mp4):
					with open(local_mp4,'wb') as f1:
						res = requests.get(mp4_url,stream=True)
    						f1.write(res.content)
	except Exception,e:
		print "vid 不存在,或者" + vid + "调用接口处错"
	finally:
		pass



if __name__ == "__main__":
    mp4_domain = "http://mp4-down.yikaobang.com.cn/"
    res = dict()
    clt = init_vod_client('LTAI1aTbTiPWINmZ','bhzSeQhw3vAnZbf9HNcAwHSf4Y0RmL')
    db_conn = mdb.connect('rm-2ze344l3eokzmxot5.mysql.rds.aliyuncs.com','yxs_root','Yxs@yunwei123','api.letiku.net',unix_socket='/tmp/mysql.sock',charset='utf8')
    cursor = db_conn.cursor()
    sql = "select `exam_id`,`title`,`topic_no`,`videourl`,`point_analysis`,`point_restore`,`option`,`type` from yjy_10_exam_topic"
    try:
    	f = xlwt.Workbook()
    	sheetname = u"五套卷视频对照表"
    	# 创建表单1
    	newsheet1 = f.add_sheet(sheetname,cell_overwrite_ok=True)
	titles = [u'考试ID',u'题目标题',u'题目编号',u'mp4下载视频名称',u'考点解析',u'考点还原',u'选项',u'题型']
	# 开始写入标题到sheet1
	for i in range(0,8):
		newsheet1.write(0,i,titles[i])
	#f.save('/tmp/aaa.xlsx')
	#sys.exit(1)
	cursor.execute(sql)
	data = cursor.fetchall()
	for j in range(0,len(data)):
		if data[j]:
			vid = data[j][3]
			exam_id = data[j][0]
			title = data[j][1].encode('utf-8')
			topic_no = data[j][2]
			point_analysis = data[j][4]
			point_restore = data[j][5]
			option = data[j][6]
			t_type = data[j][7]
			if t_type == 0:
				t_type = '单选'
			if t_type == 1:
				t_type = '多选'
			if data[j][3]:
				vid = data[j][3].split('/')[3]
			if vid:
				download_mp4(vid)
			# 开始填充数据到sheet1
			for i in range(1,9):
				newsheet1.write(j+1,0,int(exam_id))
				newsheet1.write(j+1,1,u''+title)
				newsheet1.write(j+1,2,u'' +topic_no)
				newsheet1.write(j+1,3,u''+ mp4_domain + vid+'.mp4')
				newsheet1.write(j+1,4,u''+ point_analysis)
				newsheet1.write(j+1,5,u''+ point_restore)
				newsheet1.write(j+1,6,u''+ option)
				newsheet1.write(j+1,7,u''+ t_type)
	f.save('/tmp/aaa.xlsx')
    except Exception,e:
        print e	    
