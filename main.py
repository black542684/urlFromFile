# 遍历指定文件夹中所有文件，并获取url
import os
import re
import threading
import time

import requests
from urllib.parse import urlparse

# 需要查找的文件夹
rootFile = r"D:\project"
# 保存文件的路径
saveFile = r'D:\temp'

# 忽略的文件夹
ignorePath = ['.git', 'node_modules', 'miniprogram_npm', 'icon', 'package-lock.json', 'package.json', 'yarn.lock']
# 文件路径
files = []
# url路径
links = []


# 遍历出所有文件
def traverseFile(path):
    file_list = os.listdir(path)
    for file in file_list:
        # 过滤忽略的文件夹
        if ignorePath.count(file) <= 0:
            # 利用os.path.join()方法取得路径全名，并存入cur_path变量，否则每次只能遍历一层目录
            cur_path = os.path.join(path, file)
            # 判断是否是文件夹
            if os.path.isdir(cur_path):
                traverseFile(cur_path)
            else:
                # 保存文件路径
                files.append(cur_path)


# 获取文件中的url
def getFileUrl(files):
    global links
    # 遍历所有文件路径
    for file in files:
        # 打开文件
        with open(file, 'r', encoding='UTF-8') as f:
            urls = f.read()
            # 查找文件中的url
            inner_links = re.findall('[("\']((http)s?://.*?)[\'")]', urls)
            # 遍历所有的url并保存
            for url in inner_links:
                links.append(url[0])


# 解析url并下载
def parseUrl(links):
    for url in links:
        # 1. 获取各主要参数
        path = urlparse(url).path
        # 2. 分割路径和文件名
        result = os.path.split(path)
        # 3. 多线程下载
        t = threading.Thread(target=createDir, args=(saveFile + result[0], result[1], url))
        t.start()


# 下载并保存文件
def createDir(path: str, filename: str, url: str) -> None:
    try:
        # 下载文件
        file = requests.get(url)
        filepath = os.path.join(path, filename)
        # 判断文件夹是否存在
        if os.path.exists(path):
            open(filepath, 'wb').write(file.content)
        else:
            # 创建文件夹
            os.makedirs(path)
            open(filepath, 'wb').write(file.content)
    except BaseException as a:
        print('下载出错', a)
        print('出错链接：', url)


if __name__ == '__main__':
    start_time = time.time()  # 记录程序开始运行时间

    # 获取所有文件路径
    traverseFile(rootFile)
    getFileUrl(files)
    parseUrl(links)

    end_time = time.time()  # 记录程序结束运行时间
    print("下载完成")
    print('耗时 %f 秒' % (end_time - start_time))
