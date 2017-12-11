#使用无头浏览器phantomjs获取页面信息
browser = webdriver.PhantomJS('C:/phantomjs/bin/phantomjs.exe')
#data用来存储我们获取到的数据
data = None
data = pd.DataFrame({"course_name":"","start_times":"","lasting":"","start_date":"","end_date":"",
                     "rollnum":"","coursehrs":"","outline":"","key_word":""},index=["0"])
#data frame的行索引
index = 0

for k in courses.keys():  #k是键
    for v in courses[k]:  #v是值
        #page是构造的课程详情页URL
        page = "http://www.icourse163.org/course/ABC-" + str(v)
        #get数据
        browser.get(page)
        #每个页面之间停顿3秒，否则有可能还没有渲染成功，获取不到数据
        #这应该是一种隐式等待
        time.sleep(3)
        #info是我们需要的一系列信息，根据id(j-center)返回
        info = browser.find_element_by_id('j-center').text
        info = re.sub(re.compile("\n"),"",info)
        info = re.sub(re.compile(r'[0-9]{2}:[0-9]{2}'),"",string=info)

        #1.课程名称
        course_name = browser.find_element_by_tag_name('h1').text
        #2.第几次开课
        start_times = re.search(pattern="第([0-9])次开课",string=info)
        if not start_times is None:
            start_times = start_times.group(1)
        else:
            start_times = "NA"
        #3.持续时长
        lasting = re.search(pattern="课程已进行至([0-9]{0,2}\/[0-9]{0,2})周",string=info)
        if not lasting is None:
            lasting = lasting.group(1)
        else:
            lasting = "NA"
        #4.开始日期
        start_date = re.search(pattern= r"开课：([0-9]{0,4}[年]{0,1}[0-9]{0,2}月[0-9]{0,2}日)",string=info)
        if not start_date is None:
            start_date = start_date.group(1)
        else:
            start_date = "NA"
        #5.结束日期
        end_date = re.search(pattern = r"结束：([0-9]{0,4}[年]{0,1}[0-9]{0,2}月[0-9]{0,2}日)",string=info)
        if not end_date is None:
            end_date = end_date.group(1)
        else:
            end_date = "NA"
        #6.参与人数
        rollnum = re.search(pattern = r"([0-9]{0,9})人参加",string = info)
        if not rollnum is None:
            rollnum = rollnum.group(1)
        else:
            rollnum = "NA"
        #7.课程时长
        coursehrs = re.search(pattern=r"课程时长(.*?)周",string=info)
        if not coursehrs is None:
            coursehrs = coursehrs.group(1)
        else:
            coursehrs = "NA"
        #8.课程概述
        outline = browser.find_element_by_id('j-rectxt2').text
        if outline is None:
            outline = "NA"

        data.loc[index] = {"course_name":course_name,"start_times":start_times,"lasting":lasting,"start_date":start_date,
                       "end_date":end_date,"rollnum":rollnum,"coursehrs":coursehrs,"outline":outline,"key_word":k}

        index = index + 1

        print("已经获取第%d个课程数据！"%(index))
