# -*- coding: utf-8 -*-

'''
@Time    : 2020/4/6 19:48
@Author  : jiangzhiqin 
'''
from threading import Thread,Lock
from queue import Queue
from urllib import request
from lxml import html
import os
#https://bh.sb/post/category/main/page/2/

#爬取数据类

class SpiderCategory(Thread):

    def __init__(self,crawl_name,page_queue):
        """

        :param crawl_name: 线程名
        :param page_queue: 页面链接队列
        """
        super(SpiderCategory,self).__init__()
        self.crawl_name = crawl_name #线程名
        self.page_queue = page_queue

    def run(self):
        print("启动{}线程".format(self.crawl_name))

        self.page_spider()

        print("结束{}线程".format(self.crawl_name))

    def page_spider(self):#请求页面

        while True:
            if self.page_queue.empty(): #队列为空
                break

            else:
                page = self.page_queue.get(False) #页数

                url = "https://bh.sb/post/category/main/page/"+str(page)+"/"
                headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36",
                           "Accept-Language":"zh-CN,zh;q=0.8"}
            timeout = 0

            while timeout<3:#多次尝试失败结束
                timeout +=1
                try:
                    # req = request.Request(url)
                    # html = request.urlopen(req).read()
                    # #将网页数据添加到队列
                    # html = html.decode("utf-8")
                    # req.add_header("User-Agent","Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36")
                    # data_queue.put(html)

                    req = request.Request(url)
                    # print("--------可以url-------",url)
                    html = request.urlopen(req).read()
                    html = html.decode('utf-8')
                    req.add_header('User-Agent',
                                   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36')
                    data_queue.put(html)
                    break
                except Exception as e:
                    print(e)

            if timeout>=3:
                print('爬取网页超时{}'.format(url))


#解析页面数据
class ParsersCategory(Thread):

    def __init__(self,parse_name,data_queue,lock,file_name):
        """

        :param parse_name: 线程名
        :param data_queue: 数据队列
        :param lock: 加锁
        :param file_name: 保存数据文件
        """
        super(ParsersCategory,self).__init__()
        self.parse_name = parse_name
        self.data_queue = data_queue
        self.lock = lock
        self.file_name = file_name

    def run(self):

        print("启动{}线程".format(self.parse_name))

        global exitFlag_parser,total
        while not exitFlag_parser:

            try:
                '''
                    调用队列对象的get()方法从队头删除并返回一个项目。可选参数为block，默认为True。
                    如果队列为空且block为True，get()就使调用线程暂停，直至有项目可用。
                    如果队列为空且block为False，队列将引发Empty异常。
                '''
                item = self.data_queue.get(False)
                print("---------item----------",item)
                if not item:
                    pass
                #调用方法对页面数据进行解析
                self.parser_page(item)
                #每task_done一次就从队列里删掉一个元素，这样在最后join的时候根据长度是否为零来判断队列是否结束，从而执行主进程
                self.data_queue.task_done()

                print("线程%s, %d" % (self.parse_name, total))


            except Exception as e:
                print("parser线程名{0}发生异常{1}".format(self.parse_name,e))

            print("结束{}线程".format(self.parse_name))

    def parser_page(self,item):
        """
        网页数据解析函数
        :param item: 页面返回的数据内容
        :return:
        """
        global total
        try:

            etree = html.etree
            HTMLS = etree.HTML(item)
            Nodes = HTMLS.xpath("//article/header/h2/a/")
            print("-------node-----------",Nodes)
            for node in Nodes:
                node_text = node.text

                #将本地文件写入数据加上互斥锁
                with self.lock:
                    self.file_name.write(node_text+"\n")

        except Exception as e:
            print("数据解析{}线程错误".format(self.parse_name),e)

        with self.lock:
            total +=1

#数据队列
data_queue = Queue()
#是否可以退出线程，默认是False,当所有的线程都处理完之后，把他改为True
exitFlag_parser = False
#线程中的互斥锁
lock = Lock()
total =0


file_name = os.path.join(os.path.dirname(os.path.abspath("__file__")),"c.txt")

print(file_name)
#主函数
def main():
    file_names = open(file_name,'a')

    #创建页码队列
    page_queue = Queue(1)
    start_page = int(input('请输入开始的页码：\n'))
    end_page = int(input('请输入结束的页码：\n'))
    # 把要爬取得页码放入页码队列
    for page in range(start_page,end_page+1):
        page_queue.put(page)

    # 初始化采集线程
    crawl_threads = []

    # 创建线程
    crawl_list = ['crawl-1', 'crawl-2', 'crawl-3', 'crawl-4']
    #启动线程
    for crawl in crawl_list:
        thread = SpiderCategory(crawl,page_queue)
        thread.start()
        crawl_threads.append(thread)

    # 初始化数据处理线程2
    parse_threads = []
    # 创建线程
    parse_list = ['parser-1', 'parser-2', 'parser-3', 'parser-4']
    #启动线程
    for parser in parse_list:
        thread = ParsersCategory(parser,data_queue,lock,file_names)
        thread.start()
        parse_threads.append(thread)

    # 等待所有的子线程完成
    for crawl in crawl_threads:
        crawl.join()

    # 如果以上条件都满足了,那么,就证明队列中已经没有需要处理的了,可以通知线程退出了
    global exitFlag_parser  # 函数中修改全局变量要声明
    exitFlag_parser = True

    # 等待所有的数据处理线程完成
    for each in parse_threads:
        each.join()

    print('主线程结束')

    # 关闭文件
    with lock:
        file_names.close()


if __name__ == '__main__':
    main()










