import os


def getDir(path):
    bookdir_path_list = []
    bookname_list = []
    for name in os.listdir(path):
        file_path = os.path.join(path, name)
        if os.path.isdir(file_path):
            bookdir_path_list.append(file_path)
            bookname_list.append(name)
    return bookname_list

def getFile(path):
    title_list = []
    for name in os.listdir(path):
        file_path = os.path.join(path, name)
        if os.path.splitext(file_path)[1] == '.txt':
            title_list.append(name[0:-4])
    return title_list

def make_book_txt(path, bookname, title_list):
    bookdir_path = path + '/' + bookname
    book_path = bookdir_path + '.txt'
    if os.path.exists(book_path):
        return
    book_file = open(book_path, "ab+")  # 打开小说文件
    for title in title_list:
        print(title)
        title_path = os.path.join(bookdir_path, title+'.txt')
        print(title_path)
        book_title_file = open(title_path, encoding='utf_8_sig')  # 返回一个文件对象
        # book_file.write(('\n# ' + title + '\n').encode('UTF-8'))
        line = book_title_file.readline()  # 调用文件的 readline()方法
        while line:
            book_file.write((line + '\n\n').encode('UTF-8'))
            line = book_title_file.readline()
        book_title_file.close()
    book_file.close()  # 关闭小说文件

#
# def pre_convert(path, bookname):
#     author = ''
#     img = ''
#     bookdir_path = path + '/' + bookname
#     book_path = bookdir_path + '.toml'
#     content = f'''title="{bookname}"
# author="{author}"
# file="{bookdir_path}.txt"
# cover="{img}"
# chapter=""
# subchapter="^第.*章第 \\d+ 节  .*$"
# compress=false
# encoding="UTF-8"
# lang="zh-CN"'''
#     '''title="example"
#     author="zhengxin"
#     file="examples/example.txt"
#     cover="examples/cover_example.jpg"
#     chapter="^第.*卷$"
#     subchapter="^第\\d+章 .*$"
#     compress=false
#     encoding="GB18030"
#     lang="zh-CN"'''
#     if os.path.exists(book_path):
#         return
#     book_file = open(book_path, "ab+")  # 打开小说文件
#     book_file.write(content.encode('UTF-8'))
#     book_file.close()  # 关闭小说文件

def convert(path, bookname):
    os.system('chcp 65001')
    bookdir_path = path + '/' + bookname
    print(bookdir_path)
    cmd = f'{os.getcwd()}//txt2mobi.exe -config "{bookdir_path}.toml" [- o "{bookdir_path}.mobi"] [-p]'
    os.system(cmd)


if __name__ == '__main__':
    path = os.getcwd()+'/小说'
    bookname_list = getDir(path)
    print(bookname_list)
    for bookname in bookname_list:
        title_list = getFile(os.path.join(path, bookname))
        # print(bookname, title_list)
        make_book_txt(path, bookname, title_list)
        convert(path, bookname)
