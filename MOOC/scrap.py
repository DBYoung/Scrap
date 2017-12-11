import requests
import urllib.parse as up

#准备进行搜索的关键词
keywords = ['大数据','机器学习','数据挖掘','数据科学','人工智能']

#转换成URL编码
def quote(x):
    return up.quote(x)
#转换编码
keywords = list(map(quote,keywords))

#URL前缀
startUrl = "http://www.icourse163.org/search.htm?search="

#构造URL
urls = []
for kws in keywords:
    urls.append(startUrl+kws)

#post的URL
jsurl = "http://www.icourse163.org/dwr/call/plaincall/MocSearchBean.searchMocCourse.dwr"

#请求头
headers = {
        "Accept":"*/*",
        "Accept-Encoding":"gzip,deflate",
        "Accept-Language":"zh-CN,zh;q=0.9",
        "Connection":"keep-alive",
        "Content-Length":"522",
        "Content-Type":"text/plain",
        "Host":"www.icourse163.org",
        "Origin":"http://www.icourse163.org"
        #Refere是我们查询的时候对应的URL，也需要根据不同的关键词进行调整
        #"Referer":"http://www.icourse163.org/search.htm?search=%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0"
        }
#发送的数据
payload = {
    "callCount":"1",
    "scriptSessionId":"${scriptSessionId}190",
    "httpSessionId":"907805e60a6540c4a268164e9e89ac4c",
    "c0-scriptName":"MocSearchBean",
    "c0-methodName":"searchMocCourse",
    "c0-id":"0",
    #c0-e1的string是我们查询的关键词，需要根据不同的关键词进行更改
    #"c0-e1":"string:%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0",
    #c0-e2的number表示获取的是第几页数据，需要动态变化
    #"c0-e2":"number:1",
    "c0-e3":"boolean:true",
    "c0-e4":"null:null",
    "c0-e5":"number:0",
    "c0-e6":"number:30",
    "c0-e7":"number:20",
    "c0-param0":"Object_Object:{keyword:reference:c0-e1,pageIndex:reference:c0-e2,highlight:reference:c0-e3,categoryId:reference:c0-e4,orderBy:reference:c0-e5,stats:reference:c0-e6,pageSize:reference:c0-e7}",
    "batchId":"1511830181483"
         }

#构造一个空字典，用于存储课程列表中每一门课程的id
courses = {}
#分析response
for i in range(0,len(urls)):
    headers["Referer"] = urls[i]
    string = "string:" + keywords[i]
    payload["c0-e1"] = string
    for j in range(1,20):  #大致查询了一下，课程数量不会超过20页
        page = "number:" + str(j)
        payload["c0-e2"] = page
        #目前为止，上面请求的部分已经做完
        response = requests.post(data=payload,url=jsurl,headers = headers)
        courseid = re.findall(pattern=r'courseId=([0-9]{0,20})',string=response.text)
        if(len(courseid) == 0):
            break;
        else:
            kw = up.unquote(keywords[i])
            if not kw in courses.keys():
                courses[kw] = courseid
            else:
                courses[kw].extend(courseid)
