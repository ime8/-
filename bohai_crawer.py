from bs4 import BeautifulSoup
from urllib import request
import threading
import re
import os
from lxml import html

class SpiderCategory(threading.Thread): #继承父类threading.Thread

    def __init__(self,url,newdir,CrawledURLs):
        super(SpiderCategory,self).__init__()
        self.url = url
        self.newdir = newdir
        self.CrawledURLs = CrawledURLs

    def run(self): #把要执行的代码写到run函数里面，线程在创建后会直接运行run函数
        CrawListPage(self.url, self.newdir, self.CrawledURLs)
#任务管理器
starturl = "https://bh.sb/post/category/main/"
#判断地址是否已经爬取
def __isexit(newurl,CrawledURLs):
    for url in CrawledURLs:
        if newurl == url:
            return True
    return False


#打开页面
def getUrl(url):
    req = request.Request(url)
    html = request.urlopen(req).read()
    html = html.decode('utf-8')
    req.add_header('User-Agent','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36')
    return html

#SpiderCategory().getUrl('https://bh.sb/post/category/main/')

#分析主题下的页面
def CrawListPage(indexurl,filedir,CrawledURLs):
    print('正在解析主题下资源')
    page = getUrl(indexurl)

    if page == 'error':
        return
    CrawledURLs.append(indexurl)

    etree = html.etree
    Html = etree.HTML(page)

    p_title = Html.xpath('//article[@class="article-content"]/p')[:-5]
    p_image = Html.xpath('//article[@class="article-content"]/p/img/@src')
    i=0
    for img_url in p_image:
        img_url_name = '.'+(img_url.split('.')[-1])
        img_file_name = filedir+"/"+str(i)+img_url_name
        print(img_file_name)
        with open(img_file_name,"wb") as f:
            print(img_url)
            req = request.urlopen(img_url)
            print("req",req)
            buf = req.read()
            print(buf)
            f.write(buf)
            i +=1
    # title_len = len(p_title)
    # print(title_len)
    # for i in range(0,title_len):
    #
    #
    #     #print(p_title[i].xpath("img/@src"))
    #     if not p_title[i].xpath("text()"):
    #         img = p_title[i].xpath("img/@src")
    #         source = p_title[i-1].xpath("text()")[0].replace("/", " ") \
    #                                             .replace("\\", " ") \
    #                                             .replace(":", " ") \
    #                                             .replace("*", " ") \
    #                                             .replace("?", " ") \
    #                                             .replace("\"", " ") \
    #                                             .replace("<", " ") \
    #                                             .replace(">", " ") \
    #                                             .replace("|", " ") \
    #                                             .replace("【", " ") \
    #                                             .replace("】", " ")
    #         img_name = source.strip()+img[0]
    #         # print(img_name)
    #
    #         #filedir_img = str(filedir+"//"+img_name+'.jpg').strip()
#解析首页
def CrawIndexPage(starturl):
    print("正在爬取首页")

    page = getUrl(starturl)
    if page =="error":
        return

    soup = BeautifulSoup(page,'lxml')
    Nodes = soup.find_all('article')

    print("首页解析出地址",len(Nodes),"条")
    for node in Nodes:
        CrawledURLs = []
        CrawledURLs.append(starturl)
        a = node.find('a')
        url = a.get('href')

        if __isexit(url,CrawledURLs):
            pass

        else:
            try:
                catalog = a.text

                catalog = re.findall(r'\[(.*?)\]',catalog)[0]
                print("---------------",catalog)
                newdir = "D:/海贝/"+catalog
                if not os.path.exists(newdir):
                    os.makedirs(newdir.encode("utf-8"))
                print("创建分类目录成功----------")

                thread = SpiderCategory(url,newdir,CrawledURLs)
                thread.start()
                #CrawListPage(url,newdir,CrawledURLs)
            except Exception as e:
                print(e)



CrawIndexPage(starturl)





