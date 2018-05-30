import json
import sys

lt = ['D:\\Anaconda3\\envs\\py36\\python36.zip', 'D:\\Anaconda3\\envs\\py36\\DLLs', 'D:\\Anaconda3\\envs\\py36\\lib', 'D:\\Anaconda3\\envs\\py36', 'D:\\Anaconda3\\envs\\py36\\lib\\site-packages', 'D:\\Anaconda3\\envs\\py36\\lib\\site-packages\\win32', 'D:\\Anaconda3\\envs\\py36\\lib\\site-packages\\win32\\lib', 'D:\\Anaconda3\\envs\\py36\\lib\\site-packages\\Pythonwin', 'D:\\PyWork\\helpers\\pycharm_matplotlib_backend']
for i in lt:
    sys.path.append(i)

import pymongo

def MongoClient():
    try:
        client = pymongo.MongoClient()
        db = client['APP']
        tb = db['JD']
        return tb
    except:
        print('数据库连接失败')


def save_to_mongoDB(data):
    try:
        tb = MongoClient()
        tb.insert(data)
        print('数据插入成功')
    except:
        print('数据插入失败')


def response(flow):
    global pid,comment_list
    url = flow.request.url
    url_product = 'cdnware.m.jd.com'
    text = flow.response.text
    dt = {}
    if url_product in url:
        data = json.loads(text)
        #用于储存评论
        comment_list = []
        if data.get('wareInfo') and data.get('wareInfo').get('basicInfo'):
            info = data.get('wareInfo').get('basicInfo')
            name = info.get('name')
            pid = info.get('wareId')
            dt.update({'name':name,'pid':pid})
            print(name,pid)
            save_to_mongoDB(dt)
    url_price = 'client.action?functionId=wareBusiness'
    if url_price in url:
        data = json.loads(text)
        try:
            price = data['floors'][0]['data']['priceInfo']['jprice']['value'] or data['floors'][0]['data']['priceInfo']['mprice']['value']
        except:
            price = ''
        tb = MongoClient()
        tb.update_one({'pid':pid},{'$set':{'price':price}})
    url_comment = 'client.action?functionId=getCommentListWithCard'
    if url_comment in url:
        data = json.loads(text)
        if  data.get('commentInfoList'):
            comments = data.get('commentInfoList')
            for comment in comments:
                if comment.get('commentInfo'):
                    comment = comment.get('commentInfo')
                    nickname = comment.get('userNickName')
                    content = comment.get('commentData')
                    print(nickname, content)
                    comment_list.append((nickname,content))
            if len(comment_list) >= 30:
                tb = MongoClient()
                tb.update_one({'pid': pid}, {'$set':{'comment': comment_list}})
                print('数据更新成功')