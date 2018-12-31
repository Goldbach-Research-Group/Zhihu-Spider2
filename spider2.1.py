##可以爬取数据，速度也稍微快了一点，但中文乱码问题比较严重
##暂时改成只爬答案部分
import requests
import json
import sys
import os

questionId = 306537777     ##知乎问题ID
isDefineRange = 0          ##设为0表示爬取全部，非0表示自定义爬取回答范围
startAns = 50
endAns = 300                  ##范围为[startAns,endAns)
onceLimit = 20              ##每次最多下载个数，不能超过20
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0'}

##Get URL
def getAnsUrl(queId,offset,limit):
    url = 'https://www.zhihu.com/api/v4/questions/'+str(queId)+'/answers?include=data[*].is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%3Bdata[*].mark_infos[*].url%3Bdata[*].author.follower_count%2Cbadge[*].topics&limit='+str(limit)+'&offset='+str(offset)+'&platform=desktop&sort_by=default'
    return url
	
def getComUrl(ansId,offset,limit):
    url = 'https://www.zhihu.com/api/v4/answers/'+str(ansId)+'/root_comments' \
			'?include=data%5B*%5D.author%2Ccollapsed%2Creply_to_author%2Cdisliked%2Ccontent%2Cvoting%2C' \
			'vote_count%2Cis_parent_author%2Cis_author&order=normal&limit='+str(limit)+'&offset='+str(offset)+'&status=open'
    return url

def getChildComUrl(comId,offset,limit):
    url = 'https://www.zhihu.com/api/v4/comments/'+str(comId)+'/child_comments' \
			'?include=%24%5B%2A%5D.author%2Creply_to_author%2Ccontent%2Cvote_count&limit='+str(limit)+ \
			'&offset='+str(offset)+'&include=%24%5B*%5D.author%2Creply_to_author%2C'\
			'content%2Cvote_count&tdsourcetag=s_pctim_aiomsg'
    return url

##获取问题下回答总数
ansUrl = getAnsUrl(questionId,0,1)
#print(ansUrl)
ansResponse = requests.get(ansUrl,headers = headers)
ansJson = json.loads(ansResponse.text)
#print(firstJson['paging']['totals'])
totalAns = ansJson['paging']['totals']

##获取回答JSON
if isDefineRange == 0:
   startAns = 0
   endAns = totalAns

limitCount = onceLimit
ansJson = {'totals' : 0,'startIndex':startAns,'data':{'questionId':questionId}}

#for i in range(startAns,endAns):
i = startAns
while i < endAns:
    ansTotals = ansJson['totals']
    if endAns - i < limitCount:
        limitCount = endAns - i
    print('Get answer['+str(i)+','+str(i+limitCount)+')')
    ansUrl = getAnsUrl(questionId,i,limitCount)
    ansResponse = requests.get(ansUrl,headers = headers)
    ansTempJson = json.loads(ansResponse.text)
    for j in range(len(ansTempJson['data'])):
        ansJson['data'][startAns+ansTotals+j] = ansTempJson['data'][j] 
    ansTotals += limitCount
    ansJson['totals'] = ansTotals
    i += limitCount
#print(json.dumps(ansJson))

with open('./answers.json','w',encoding='utf-8')as f:
    f.write(json.dumps(ansJson,ensure_ascii=False))

'''
##获取一级评论JSON
countCom = 0
comJson = {'totals':ansTotals,'startIndex':startAns,'data':{}}
#while i < endAns:
for i in range(startAns,endAns):
    ansId = ansJson['data'][i]['id']
    ##获取当前回答一级评论数
    comUrl = getComUrl(ansId,0,1)
    comResponse = requests.get(comUrl,headers = headers)
    comTempJson = json.loads(comResponse.text)
    totalCom = comTempJson['paging']['totals']
    limitCount = onceLimit
    comJson['data'][i] = {'totals':totalCom}
    if comTempJson['featured_counts']:
        comJson['data'][i]['featured_counts'] = comTempJson['featured_counts']
    
    j = 0
    while j < totalCom:
        if totalCom - j < limitCount:
            limitCount = totalCom - j
        print('Get answer['+str(i)+']-comments['+str(j)+','+str(j+limitCount)+')')
        comUrl = getComUrl(ansId,j,limitCount)
        comResponse = requests.get(comUrl,headers = headers)
        comTempJson = json.loads(comResponse.text)
        for k in range(len(comTempJson['data'])):
            comJson['data'][i][j + k] = comTempJson['data'][k]
        j += limitCount
        countCom += limitCount

                
with open('./comments.json','w',encoding='utf-8')as f:
    #s = json.dumps(comJson)
    #s = json.dumps(comJson,ensure_ascii=False)
    #f.write(s.encode('utf-8').decode('utf8'))
    #f.write(s)
    f.write(json.dumps(comJson,ensure_ascii=False))

##获取二级评论JSON
countChCom = 0
chComJson = {'totals':ansTotals,'startIndex':startAns,'data':{}}
#while i < endAns:
for i in range(startAns,endAns):
    chComJson['data'][i] = {'totals':comJson['data'][i]['totals']}
    for j in range(comJson['data'][i]['totals']):
        if j in comJson['data'][i]:
            #comId = comJson.get('data').get(i).get(j).get('id')
            comId = comJson['data'][i][j]['id']
            ##获取当前评论二级评论数
            totalChCom = comJson['data'][i][j]['child_comment_count']
            limitCount = onceLimit
            chComJson['data'][i][j] = {'totals':totalChCom}
            #print('i='+str(i)+'j='+str(j))
            k = 0
            while k < totalChCom:
                if totalChCom - k < limitCount:
                    limitCount = totalChCom - k
                print('Get answer['+str(i)+']-comment['+str(j)+']-child_comments['+str(k)+','+str(k+limitCount)+')')
                chComUrl = getChildComUrl(comId,k,limitCount)
                #print(chComUrl)
                chComResponse = requests.get(chComUrl,headers = headers)
                chComTempJson = json.loads(chComResponse.text)
                for m in range(len(chComTempJson['data'])):
                    chComJson['data'][i][j][k + m] = chComTempJson['data'][m]
                k += limitCount
                countChCom += limitCount


with open('./child_comments.json','w',encoding='utf-8')as f:
    f.write(json.dumps(chComJson,ensure_ascii=False))
'''
