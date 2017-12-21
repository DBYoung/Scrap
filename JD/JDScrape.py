import requests
import re
import urllib.parse as up
import time
import sys
import json

def quote(x):
    '''
    转换成URL编码
    '''
    return up.quote(x)
def unquote(x):
    '''
    将URL编码转换成字符串
    '''
    return up.unquote(x)

class JDSpider:
    '''
    JDSpider类是一个爬虫类，首先，你需要为构造函数传递必需的参数以初始化类，然后，你就可以使用类中的方法，生成URL，获取商品详情。
    
    '''
    def __init__(self,kwdlist,psort,pages = 100):
        '''
        kwslist:列表，元素为在京东搜索框输入的关键词。
        psort:整数，代表排序方式。
            1：价格由低到高
            2：价格由高到低
            3：销量由高到低
            4：评论数由高到低
            5：上架时间由近及远
        pages:需要获取的商品列表的页数，默认是获取100页
        '''
        self.kwdlist = kwdlist
        self.psort = psort
        self.pages = pages
        pass
    
    def genURLs(self,**paras):
        '''
        genURLs函数根据给定的关键词列表和排序方式，生成需要获取的具体页面的URL。
        在笔者写这段代码的时候，京东已经把商品列表的页数限制为100页，而在此之前是有超过100页的。
        次函数支持两种数据输出方式：
            1. 将数据输出到本地磁盘，以平面文件的方式存储；
            2. 将数据输出到数据库，以二维表的形式存储。
        除非你需要将数据存储到本地磁盘，否则你需要按顺序提供以下参数：
            
        '''
        
        
        #startUrl中需要改变的是psort,page,s,keyword和wq
        #因此，先将startUrl写成通用模式
        #page和s都是从1开始的，京东的每一页有两个page，第一页的page为1,2，s为1,31，第二页的page为3,4，s为61,91，以此类推
        #因此，先根据关键词列表构造初始的URL
        
        psort = str(self.psort)
        common1Url = "https://search.jd.com/Search?enc=utf-8&qrst=1&rt=1&stop=1&vt=2&click=0" + "&psort=" + psort
        common2Url = "https://search.jd.com/s_new.php?scrolling=y&tpl=1_M&enc=utf-8&qrst=1&rt=1&stop=1&vt=2" + "&psort=" + psort
        kwds = self.kwdlist
        
        '''
        京东商品列表页的源代码只给出了前30个商品的id，往下翻到第七行的时候，才会出现剩下的30个商品的信息，但是这个过程是通过动态请求得到的
        我们需要构造请求的参数，对获取的响应数据进行提取，才能得到剩下的30个商品的id
        上述语句完成了初始URL的生成工作，下面需要利用上面生成的结果，向浏览器发出请求
        下面的语句构造请求头,其中Referer需要在每页进行变动。即每一页的后30个商品id需要通过前30个id进行获取
        '''

        headers = {"Accept":"*/*",
                    "Accept-Encoding":"gzip, deflate, br",
                    "Accept-Language":"zh-CN,zh;q=0.9",
                    "Connection":"keep-alive",
                    "Host":"search.jd.com",
                    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36",
                    "X-Requested-With":"XMLHttpRequest"}
        
        with open("ids.csv","a") as f:
            for kwd in kwds:
                kwd = quote(kwd)
                page = 1
                s = 1
                part1Url = common1Url + "&keyword=" + kwd + "&wq=" + kwd 
                part2Url = common2Url + "&keyword=" + kwd + "&wq=" + kwd 
                
                while page <= self.pages*2:
                    
                    currUrl = part1Url + "&page=" + str(page) + "&s=" + str(s)
                    res =requests.get(url=currUrl)
                    ids = re.findall('li data-sku="([0-9]+)',res.text)
                    headers['Referer'] = currUrl
                    
                    page = page + 1
                    s = s + 30
                    
                    time.sleep(2.0)
                    
                    requestUrl = part2Url + "&page=" + str(page) + "&s=" + str(s) + "&show_items=" + ",".join(ids)
                    
                    res = requests.get(url=requestUrl,headers = headers)
                    ids += re.findall('li data-sku="([0-9]+)',res.text)
                    
                    page = page + 1
                    s = s + 30
                    
                    f.write(",".join(ids)+"\n")
        
    def getComments(self,commentPages = 2000):
        
        '''
        getComments函数爬取商品的评论信息。此处的商品是根据genURLs函数生成的商品id来获取的，根据此id可以构造评论信息的URL。
        京东评论页的URL如下所示:
            https://sclub.jd.com/comment/productPageComments.action?productId=12128543&score=0&sortType=3
            &page=0&pageSize=10&isShadowSku=0&callback=fetchJSON_comment98vv4361
        
        此处需要改变的参数：
            1. sortType，要与我们之前传入的psort一致；
            2. page，评论所在的页数，从0开始，如果评论比较多，比如有20000个，那么page就可能达到2000;
            3. productid即为我们获取到的商品id；
            4. callback的参数可以直接设为fetchJSON_comment，省略后面的内容。
            
        book:爬取的是否是书籍，默认True。
        commentPages:爬取评论的页数，默认2000页。
        '''
        
        url = "https://sclub.jd.com/comment/productPageComments.action?score=0&pageSize=10&isShadowSku=0&callback=fetchJSON_comment" + "&sortType=" + str(self.psort)
        
        with open("comments.csv","a") as f1,open('ids.csv','r') as f2,open("items.csv","a") as f3:
            #f1存放评论数据，f2是getURLs函数获取到的ids，f3存放商品的其他信息
            lines = f2.readlines()
            for line in lines:
                line = re.sub("\n","",line)
                ids = line.split(",")
                for id in ids:
                    #构造商品详情页面的URL
                    itemUrl = "https://item.jd.com/"+ id + ".html"
                    resItem = requests.get(itemUrl)
                    try:
                        item = re.search("《(.*?)》",resItem.text).group(1)
                        
                    except:
                        item = re.search("<title>(.*?)</title>",resItem.text).group(1)
                        
                    f3.write(id + "," + item + "\n")
                    for pageNum in range(2):    
                        currUrl = url + "&productId=" + id + "&page=" + str(pageNum) 
                        try:
                            res = requests.get(currUrl)
                            text = res.text
                            text = text[18:len(text)-2]
                            j = json.loads(text)
                            
                            for i in range(10):
                                f1.write(id+",page"+str(pageNum)+","+re.sub("\n","",j['comments'][i]['content']) + "\n")
                        except:
                            break
                            
                            
a = JDSpider(['机器学习',"大数据","人工智能","深度学习","数据挖掘"],3,10)

a.genURLs()

a.getComments(commentPages=10)
