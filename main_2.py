# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import requests
from lxml import etree
import os
import json
from urllib import parse
import execjs
import hashlib
import time

import Utils


def progress(title_id):
    url = 'https://api.zhihu.com/promus/progress'
    path = '/promus/progress'
    cookie = Utils.read_my_file('my_file/cookie.txt')
    post_data = [{"unit_id": title_id, "type": "paid_column", "progress": 1,
             "client_updated_at": int(round(time.time() * 1000)),
             "is_finished": True}]
    op = SpiderRequest(path, url, cookie)
    data = op.postRequest(post_data)

def pre_convert(path, bookname, author, img_path):
    r = requests.get(img_path)
    with open(path + '/' + bookname + '/' + bookname + ".jpg", 'wb')as jpg:
        jpg.write(r.content)
    book_path = path + f'/{bookname}'
    book_toml = path + f'/{bookname}.toml'
    book_path_convert = book_path.replace('\\', '/')
    content = f'''title="{bookname}"
author="{author}"
file="{book_path_convert}.txt"
cover="{book_path_convert}/{bookname}.jpg"
chapter="^第.*章 .*$"
subchapter="^第 \\\d+ 节 .*$"
compress=false
encoding="UTF8"
lang="zh-CN"'''
    # 暂时用不到
    '''title="example"
    author="zhengxin"
    file="examples/example.txt"
    cover="examples/cover_example.jpg"
    chapter="^第.*卷$"
    subchapter="^第\\d+章 .*$"
    compress=false
    encoding="GB18030"
    lang="zh-CN"'''
    if os.path.exists(book_toml):
        return
    book_file = open(book_toml, "ab+")  # 打开小说文件
    book_file.write(content.encode('UTF-8'))
    book_file.close()  # 关闭小说文件


# # 建立索引
def bookdata(path, data):
    for books in data['data']:
        book_id = books['business_id']
        book_name = books['title']
        book_author = books['author'][0]
        book_img_path = books['tab_artwork']
        bookdir_path = os.path.join(path, book_name)
        if not os.path.exists(bookdir_path):
            os.makedirs(bookdir_path)
        else:
            continue
        pre_convert(path, book_name, book_author, book_img_path)

        url = 'https://api.zhihu.com/remix/well/' + book_id + '/catalog?limit=50&include_after_id=true&offset=0'
        url_path = '/remix/well/' + book_id + '/catalog?limit=50&include_after_id=true&offset=0'
        op = SpiderRequest(url_path, url, cookie)
        title_list = op.getRequest()
        list = getAlltitle(title_list)

        # 循环得到所有列表
        while title_list['paging']['has_next'] is True:
            url = 'https:' + title_list['paging']['next']
            url_path = title_list['paging']['next'][15:]
            op = SpiderRequest(url_path, url, cookie)
            title_list = op.getRequest()
            list = list + getAlltitle(title_list)

        setIndex(path, list, book_name)
        # 获取所有文章，存入txt，转换为html
        for index in range(len(list)):
            next_title = 'index'
            chapter = list[index].get('chapter')
            relative = list[index].get('relative')
            title = list[index].get('title').replace("\n", "").replace(" ", "")
            try:
                next_title = list[index + 1].get('title').replace("\n", "").replace(" ", "")
            except Exception as e:
                print('/')
            req(bookdir_path, book_id, book_name, list[index].get('id'), chapter, relative, title, next_title)


def getAlltitle(title_list):
    list = []
    for data in title_list['data']:
        id = data['id']
        chapter_id = data['chapter']['serial_number_txt']
        chapter = chapter_id + ' ' + data['chapter']['title']
        relative = data['index']['relative']
        title = data['index']['serial_number_txt'] + '  ' + data['title']
        dict = {'id': id, 'chapter': chapter, 'relative': relative, 'title': title}
        list.append(dict)
    print(list)
    return list


def setIndex(path, list, book_name):
    bookdir_path = os.path.join(path, book_name)
    if not os.path.exists(bookdir_path):
        os.makedirs(bookdir_path)
    # 索引
    pathIndex = path + '/3.html'
    fileIndex = open(pathIndex, "ab+")  # 打开小说文件
    text = '<p><a href="' + book_name + '/index.html">' + book_name + '</a></p>'
    fileIndex.write((text).encode('UTF-8'))
    fileIndex.close()
    pathPage = bookdir_path + '/index.html'
    filePage = open(pathPage, "ab+")  # 打开小说文件
    filePage.write('<meta charset="UTF-8">'.encode('UTF-8'))
    for l in list:
        chapter = l.get('chapter')
        relative = l.get('relative')
        title = l.get('title')
        path = '' + l.get('title') + '.html'
        if relative == 1:
            text = '<p>' + chapter + '</p>'
            filePage.write((text + '').encode('UTF-8'))
        text = '<p><a href="' + path + '">' + title + '</a></p>'
        filePage.write((text + '').encode('UTF-8'))
    filePage.close()


def req(bookdir_path, book_id, book_name, id, chapter, relative, title, next_title):
    cookie = Utils.read_my_file('my_file/cookie.txt')
    headers = {
        'referer': 'https://www.zhihu.com/xen/market/remix/paid_column/' + book_id,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
        'Cookie': cookie
    }
    response = requests.get('https://www.zhihu.com/market/paid_column/' + book_id + '/section/' + id,
                            headers=headers)

    response.encoding = 'utf-8'
    print(response)
    # print(response.text)
    html = etree.HTML(response.text)
    # title = ''.join(html.xpath('//*[@id="app"]/div/h1/text()'))
    # print(title)
    textx = html.xpath('//*[@id="manuscript"]')
    text = textx[0].xpath('string(.)').strip()
    print(text)
    timestamp = str(int(round(time.time() * 10000000000)))   #超极长的时间戳用来当文件名，保证每章顺序
    fullpath = bookdir_path + '/' + timestamp + '.txt'
    if not os.path.exists(bookdir_path):
        os.makedirs(bookdir_path)
    file = open(fullpath, "ab+")  # 打开小说文件
    if relative == 1:
        file.write((chapter + '\n').encode('UTF-8'))
    file.write((title + '\n').encode('UTF-8'))
    file.write((text).encode('UTF-8'))
    file.close()  # 关闭小说文件
    toHtml(bookdir_path, timestamp, title, next_title)


def toHtml(path, id, title, next_title):
    pathtext = path + '/' + id + '.txt'
    pathhtml = path + '/' + title + '.html'
    f = open(pathtext, encoding='utf_8_sig')  # 返回一个文件对象
    fhtml = open(pathhtml, "ab+")  # 打开小说文件
    line = f.readline()  # 调用文件的 readline()方法
    fhtml.write('<meta charset="UTF-8">'.encode('UTF-8'))
    while line:
        fhtml.write((line + '<p>').encode('UTF-8'))
        print(line)
        line = f.readline()
    fhtml.write(('<p><a href="' + path + '/' + next_title + '.html' + '">' + next_title + '</a></p>').encode('UTF-8'))

    fhtml.close()
    f.close()


class SpiderRequest():
    def __init__(self, parse_url, url, cookie):
        self.parse_url = parse_url
        self.url = url
        self.cookie = cookie
        self.headers = {}

    def get_headers(self):
        star = 'd_c0='
        end = ';'
        cookie_mes = self.cookie[self.cookie.index(star):].replace(star, '')
        cookie_mes = cookie_mes[:cookie_mes.index(end)]
        f = "+".join(["101_3_2.0", self.parse_url, cookie_mes])
        fmd5 = hashlib.new('md5', f.encode()).hexdigest()
        jsdom_path = Utils.read_my_file('my_file/jsdom_path.txt')
        with open("./g_encrypt.js", 'r', encoding='utf-8') as f:
            ctx1 = execjs.compile(f.read(), cwd=jsdom_path)
        encrypt_str = "2.0_%s" % ctx1.call('b', fmd5)
        print(encrypt_str)
        headers = {
            "x-api-version": "3.0.91",
            'x-app-za': 'OS=Web',
            "x-zse-93": "101_3_2.0",
            "x-zse-96": encrypt_str,
            "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
            "Cookie": self.cookie,
        }
        self.headers = headers

    def getRequest(self):
        self.get_headers()
        response = requests.get(self.url, headers=self.headers)
        response.encoding = 'utf-8'
        print(response)
        print(response.text)
        json_mes = json.loads(response.text)
        print(json_mes)
        return json_mes

    def postRequest(self, data):
        self.get_headers()
        headers = self.headers
        # headers['Content-Type'] = 'application/json'
        print(headers)
        print(int(round(time.time() * 1000)))  # 毫秒级时间戳

        print(data)
        response = requests.post(self.url, json=data, headers=headers)
        response.encoding = 'utf-8'
        print(response)
        print(response.text)
        json_mes = json.loads(response.text)
        print(json_mes)
        return json_mes


if __name__ == '__main__':
    url = 'https://api.zhihu.com/pluton/shelves?limit=50&offset=0&property_type=column'
    url_path = '/pluton/shelves?limit=50&offset=0&property_type=column'
    cookie = Utils.read_my_file('my_file/cookie.txt')
    op = SpiderRequest(url_path, url, cookie)
    data = op.getRequest()
    path = os.path.join(os.getcwd(), "小说")
    bookdata(path, data)
