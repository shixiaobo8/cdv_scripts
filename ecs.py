#!/usr/bin/env python
# -*- coding:utf8 -*-
"""
	阿里云  python sdk  ecs 管理 demo
"""
import logging,json,sys
from aliyunsdkcore import client
from aliyunsdkecs.request.v20140526.DescribeInstancesRequest import DescribeInstancesRequest
from aliyunsdkecs.request.v20140526.DescribeRegionsRequest import DescribeRegionsRequest
clt = client.AcsClient('LTAIxxxxxQ', 'FOxxxxxxxxxxxxxxxxlExxxx', 'cbw-wewewew')


# 停止服务器
def stop_instance(instance_id, force_stop=False):
    '''
    stop one ecs instance.
    :param instance_id: instance id of the ecs instance, like 'i-***'.
    :param force_stop: if force stop is true, it will force stop the server and not ensure the data
    write to disk correctly.
    :return:
    '''
    request = StopInstanceRequest()
    request.set_InstanceId(instance_id)
    request.set_ForceStop(force_stop)
    logging.info("Stop %s command submit successfully.", instance_id)
    _send_request(request)


# 释放服务器
def release_instance(instance_id, force=False):
    '''
    delete instance according instance id, only support after pay instance.
    :param instance_id: instance id of the ecs instance, like 'i-***'.
    :param force:
    if force is false, you need to make the ecs instance stopped, you can
    execute the delete action.  正确返回格式 {"RequestId":"689E5813-D150-4664-AF6F-2A27BB4986A3"}
    错误返回格式:  
    {"RequestId":"3C6DEAB4-7207-411F-9A31-6ADE54C268BE","HostId":"ecs-cn-hangzhou.aliyuncs.com","Code":"IncorrectInstanceStatus","Message":"The current status of the resource does not support this operation."}
    If force is true, you can delete the instance even the instance is running.
    :return:
    '''
    request = DeleteInstanceRequest();
    request.set_InstanceId(instance_id)
    request.set_Force(force)
    _send_request(request)


# 设置云服务器的自动释放时间
def set_instance_auto_release_time(instance_id, time_to_release = None):
	#执行 set_instance_auto_release_time(‘i-1111’, ‘2017-01-30T00:00:00Z’) 后完成设置 
    '''
    setting instance auto delete time
    :param instance_id: instance id of the ecs instance, like 'i-***'.
    :param time_to_release: if the property is setting, such as '2017-01-30T00:00:00Z'
    it means setting the instance to be release at that time.
    if the property is None, it means cancel the auto delete time.
    :return:
    '''
    request = ModifyInstanceAutoReleaseTimeRequest()
    request.set_InstanceId(instance_id)
    if time_to_release is not None:
        request.set_AutoReleaseTime(time_to_release)
    _send_request(request)



# 获取 ecs 总数
def getEcsCount():
    request = DescribeInstancesRequest()
    request.set_accept_format('json')
    request.set_PageSize(1)
    response_str = clt.do_action(request)
    response_total = json.loads(response_str)
    TotalCount = response_total['TotalCount']
    return TotalCount


# 获取ecs 列表    
def list_instances(TotalCount):
	ecs_list = []
	for i in range(0,TotalCount/100+1):
		request = DescribeInstancesRequest()
		request.set_accept_format('json')
		request.set_PageSize(100)
		request.set_PageNumber(i+1)
		response_str = clt.do_action(request)
		response = json.loads(response_str)
		with open("c://Users/bobo/Desktop/aaa.json","ab+") as f:
			f.write(response_str)
		# print response
		# sys.exit(1)
		if response is not None:
			ecs_list.extend(response.get('Instances').get('Instance'))
	with open("c://Users/bobo/Desktop/ass.json","ab+") as f1:
			f1.write(repr(ecs_list))
	return ecs_list


if __name__ == '__main__':
	ecsCount = getEcsCount()
	ecss = list_instances(ecsCount)
	print len(ecss)


