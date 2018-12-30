##########################################
#获取知乎问题下所有回答、评论、子评论Json
#回答统一放在answer文件夹内，按默认排序从0开始命名
#评论放在comments文件夹对应answer文件夹下，前面为精选评论（会与后面的重复）
#子评论放在child_comments文件夹下对应目录，没有子评论的不会创建comment文件夹
#少数链接get不到、content乱码。
##########################################

import requests
import json
import sys
import os

questionId = 306537777
startAns = 0
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0'}

##Get URL
def getAnsUrl(num):
    url = 'https://www.zhihu.com/api/v4/questions/'+str(questionId)+'/answers' \
			'?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed' \
			'%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2' \
			'Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2' \
			'Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crele' \
			'vant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked' \
			'%2Cis_nothelp%2Cis_labeled%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.' \
			'author.follower_count%2Cbadge%5B%2A%5D.topics&limit=1&offset='+str(num)+'&platform=' \
			'desktop&sort_by=default'
    return url
	
def getComUrl(ansId,offset):
    url = 'https://www.zhihu.com/api/v4/answers/'+str(ansId)+'/root_comments' \
			'?include=data%5B*%5D.author%2Ccollapsed%2Creply_to_author%2Cdisliked%2Ccontent%2Cvoting%2C' \
			'vote_count%2Cis_parent_author%2Cis_author&order=normal&limit=1&offset='+str(offset)+'&status=open'
    return url

def getChildComUrl(comId,offset):
    url = 'https://www.zhihu.com/api/v4/comments/'+str(comId)+'/child_comments' \
			'?include=%24%5B%2A%5D.author%2Creply_to_author%2Ccontent%2Cvote_count&limit=1' \
			'&offset='+str(offset)+'&include=%24%5B*%5D.author%2Creply_to_author%2C'\
			'content%2Cvote_count&tdsourcetag=s_pctim_aiomsg'
    return url
## Make dir
def mkdir(path):
    isExists = os.path.exists(path)
    #print(isExists)
    if not isExists:
        os.makedirs(path)

mkdir('./answers')
mkdir('./comments')
mkdir('./child_comments')

##Get Answer Num
ansUrl = getAnsUrl(0)
ansResponse = requests.get(ansUrl,headers = headers)
ansJson = json.loads(ansResponse.text)
#print(firstJson['paging']['totals'])
totalAns = ansJson['paging']['totals']


##Get Json
#os.chdir('answers')
for i in range(startAns,totalAns):
#for i in range(0,2):
    print('Get answer'+str(i)+'.json')
    ansUrl = getAnsUrl(i)
    ansResponse = requests.get(ansUrl,headers = headers)
    ansJson = json.loads(ansResponse.text)
    f = open("./answers/answer"+str(i)+".json","w",encoding='utf-8')
    f.write(ansResponse.text)
    f.close()
    if ansJson['data']:
        ansId = ansJson['data'][0]['id']

        ##Get Comment Num
        comUrl = getComUrl(ansId,0)
        comResponse = requests.get(comUrl,headers = headers)
        comJson = json.loads(comResponse.text)
        
        
        totalCom = comJson['paging']['totals']
        mkdir('./comments/answer'+str(i))
        # 0-14 for Selected Comments
        if totalCom > 0:
            for j in range(0,totalCom):
                print('Get answer'+str(i)+'--comment'+str(j)+'.json')
                comUrl = getComUrl(ansId,j)
                comResponse = requests.get(comUrl,headers = headers)
                f = open("./comments/answer"+str(i)+"/comment"+str(j)+".json","w",encoding='utf-8')
                f.write(comResponse.text)
                f.close()
                comJson = json.loads(comResponse.text)
                if comJson['data']:
                    comId = comJson['data'][0]['id']
                    totalChCom = comJson['data'][0]['child_comment_count']
                    ##Get Child Comment 
                    if totalChCom > 0 :
                        mkdir('./child_comments/answer'+str(i))
                        mkdir('./child_comments/answer'+str(i)+'/comment'+str(j))
                        for k in range(0,totalChCom):
                            print('Get answer'+str(i)+'--comment'+str(j)+''+'--child_comment'+str(k)+'.json')
                            chComUrl = getChildComUrl(comId,k)
                            comResponse = requests.get(chComUrl,headers = headers)
                            f = open("./child_comments/answer"+str(i)+"/comment"+str(j)+"/child_comment"+str(k)+".json","w",encoding='utf-8')
                            f.write(comResponse.text)
                            f.close()
