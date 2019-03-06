import requests
import os
import re
from bs4 import BeautifulSoup
from urllib import parse
import sys

sloginUrl = 'http://sep.ucas.ac.cn/slogin'

randomUrl = 'http://sep.ucas.ac.cn/changePic'

appStoreUrl = 'http://sep.ucas.ac.cn/appStore'

CourseUrl = 'http://sep.ucas.ac.cn/portal/site/16/801'

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip,deflate",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded",
    "Host": "course.ucas.ac.cn",
    "Origin": "http://course.ucas.ac.cn",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"
        }

headerpostdir = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip,deflate",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Content-Length": "388",
    "Content-Type": "application/x-www-form-urlencoded",
    # Cookie: sepuser="bWlkPWFlYjZlNzdhLWYwODUtNDUwYS1hY2YyLTg4YzZmNjNlMjZhOA==  "; JSESSIONID=0c45eb02-a602-4c10-995a-c1381e677a5a.course.ucas.ac.cn; pasystem_timezone_ok=true
    "Host": "course.ucas.ac.cn",
    "Origin": "http://course.ucas.ac.cn",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"
}

loginData = {
    'userName':'',
    'pwd':'',
    'certCode':'',
    'sb':'sb'
}
# 获取院系课程
subDirData = {
    'source':0,
    'collectionId':'/group/155710/White.Geochemstry/',
    'sakai_csrf_token':'',
    'navRoot':'',
    'criteria': 'title',
    'sakai_action': 'doNavigate',
    'rt_action': '',
    'selectedItemId':'',
    'itemHidden': 'false',
    'itemCanRevise': 'false',

}


def downloadPPT(ses, ID, fileName, fileNameNo20):

    urlHead = 'http://course.ucas.ac.cn/access/content/group/' + ID + '/'
    for (oneFile, saveFileName) in zip(fileName, fileNameNo20):
        url = urlHead + oneFile
        print(url)
        file = ses.get(url)
        with open(saveFileName, 'wb') as f:
            f.write(file.content)

def getAllDir(HTML):
    '''
    :type HTML: str
    :param dirName:
    :return:
    '''
    soup = BeautifulSoup(HTML, 'lxml')
    direNamesSoup = soup.find_all(name='a', attrs={'title': '文件夹'})
    # 去掉首个
    direNamesSoup2 = direNamesSoup[1:]
    allDir = []
    reStr = r"collectionId'\).value='(.*?)'"
    for i in range(len(direNamesSoup2)):
        value = re.findall(reStr, direNamesSoup2[i]['onclick'])
        allDir.append(value)
    return allDir


# 获得某文件夹下的所有文件链接
def getSubFileUrl(HTML, ID):
    '''
    :type HTML: str
    :type ID: str
    :param HTML:
    :param ID:
    :return:
    若返回空列表，则该文件夹下为空
    '''
    NewFileUrl = []
    fileRE = 'http://course.ucas.ac.cn/access/content/group/' + ID + '/(.*?)\" target='
    fileNames = re.findall(fileRE, HTML)
    fileNames = list(set(fileNames))
    # 中文解码
    fileNamesNo20 = []
    for name in fileNames:
        temp = parse.unquote(name)
        fileNamesNo20.append(temp)
    for name in fileNames:
        tempStr = 'http://course.ucas.ac.cn/access/content/group/' + ID + '/' + name
        NewFileUrl.append(tempStr)
    return (NewFileUrl, fileNamesNo20)


# 深度优先，栈处理文件夹
def searchAll(ses, PostUrl, dirName, ID):
    '''
    :type dirName: str
    :param dirName:
    :return:
    '''
    stack = []
    fullFileUrl = []
    fullFileName = []
    stack.append(dirName)


    while stack:
        dir = stack.pop()
        subDirData['collectionId'] = dir
        html = ses.post(PostUrl, headers=headerpostdir, data=subDirData)
        htmlText = html.text
        SubDirs = getAllDir(htmlText)

        temTuple = getSubFileUrl(htmlText, ID)
        urlfilelist = temTuple[0]
        namefilelist = temTuple[1]

        if SubDirs:
            for subdir in SubDirs:
                stack.append(subdir)
        if urlfilelist:
            fullFileUrl.extend(urlfilelist)
            fullFileName.extend(namefilelist)
    return (fullFileUrl, fullFileName)

if __name__ == '__main__':

    print('请使用校园网！')
    userName = input('用户名：')
    pwd = input('密码：')

    loginData['userName'] = userName
    loginData['pwd'] = pwd


    ses = requests.session()
    # 登录
    loginHtml = ses.post(sloginUrl, headers=headers, data=loginData)
    if loginHtml.status_code == 200:
        loginHtml = loginHtml.text
        while '用户名或密码错误' in loginHtml or '验证码错误' in loginHtml:
            print('用户名或密码错误')
            userName = input('用户名：')
            pwd = input('密码：')
            loginData['userName'] = userName
            loginData['pwd'] = pwd
            # result = getcode(ses)
            # loginData['certCode'] = result
            loginHtml = ses.post(sloginUrl, headers=headers, data=loginData)
            loginHtml = loginHtml.text

    print('登录成功！')
    print('请勿网页再登录，以免相互挤掉。')

    # 跳转到课程网站
    CourseUrlHtml = ses.get(CourseUrl)
    CourseUrlHtmlText = CourseUrlHtml.text
    CourseUrlChange = re.findall(r'>2秒钟没有响应请点击<a href=\"(.*?)\"><strong>',CourseUrlHtmlText,re.S)[0]
    CourseUrlHtml = ses.get(CourseUrlChange)
    CourseUrlHtmlText = CourseUrlHtml.text
    # print(CourseUrlHtmlText)

    # # 获得资源链接
    # SourceUrl = re.findall(r'<a class=\"Mrphs-toolsNav__menuitem--link \" href=\"(.*?)\" title=\"资源 - 上传', CourseUrlHtmlText, re.S)[0]
    # SourceUrlHtml = ses.get(SourceUrl)
    # SourceUrlHtmlText = SourceUrlHtml.text

    # 获得课程id
    CourseIdList = re.findall(r'data-site-id=\"(\d*?)\" href=\"j', CourseUrlHtmlText, re.S)

    # 课程名称
    CourseNameList = []
    for id in CourseIdList:
        strrr = id + '\" title=\"(.*?)\">'
        name = re.findall(strrr, CourseUrlHtmlText)[0]
        CourseNameList.append(name)
    # print(CourseNameList)

    newCourseNameList = []
    for name in CourseNameList:
        newName = ''
        names = name.split(';')
        for word in names:
            if '&#' in word:
                # print(word)
                newWord = chr(int(word[-5:]))
                newName = word[:-7] + newName + newWord
            else:
                newName = newName + word
        newCourseNameList.append(newName)

    for i in range(len(newCourseNameList)):
        if i % 3 == 0:
            print('')
        print('名称：{0}:序号：{1}。 '.format(newCourseNameList[i], i), end='  ')
    print('')
    print('*********************************************')
    selectedId = input('输入课程序号进行批量下载：')
    while not selectedId.isdigit():
        selectedId = input('输入错误！重新输入课程序号进行批量下载：')
    while not int(selectedId) in range(len(newCourseNameList)):
        selectedId = input('输入错误！重新输入课程序号进行批量下载：')
    temID = CourseIdList[int(selectedId)]
    # print(newCourseNameList)
    # print(CourseIdList)

    # 构造资源链接
    head = 'http://course.ucas.ac.cn/portal/site/'
    courseDetailUrlList = []
    for u in CourseIdList:
        te = head + u
        courseDetailUrlList.append(te)

    CourseContentHtml = ses.get(courseDetailUrlList[0])
    CourseContentHtmlText = CourseContentHtml.text

    # 提取资源url
    PPTUrl = re.findall(r'<a class=\"Mrphs-toolsNav__menuitem--link \" href=\"(.*?)\" title=\"&#36164;&#28304;', CourseContentHtmlText)[0]

    PPTRUrlDetailHtml = ses.get(PPTUrl)
    PPTRUrlDetailHtmlText = PPTRUrlDetailHtml.text
    # 构建soup对象
    PPTsoup = BeautifulSoup(PPTRUrlDetailHtmlText, 'lxml')

    # 获取token
    token = PPTsoup.find_all(name='input', attrs={'name':'sakai_csrf_token'})
    tokens = token[0]['value']
    subDirData['sakai_csrf_token'] = tokens
    iniValue = '/group/' + temID


    fullFileUrl, fullFileName = searchAll(ses, PPTUrl, iniValue, temID)



    newFolder = input('××××××××输入新建下载文件夹：')
    while os.path.isdir(newFolder):
        print('×××××××文件夹已存在！请重新输入：')
        newFolder = input('××××××××输入新建下载文件夹：')

    os.mkdir(newFolder)
    maxDir = '/'
    for saveDirr in fullFileName:
        if '/' in saveDirr:
            dirIndex = saveDirr.rindex('/')
            dirF = saveDirr[:dirIndex+1]
            if maxDir != dirF:
                tempdir = dirF.split('/')
                finaldir = newFolder
                for dirr in tempdir:
                    finaldir = os.path.join(finaldir, dirr)
                maxDir = dirF
                os.makedirs(finaldir)
                # print(finaldir)

    fileNumber = len(fullFileName)
    current = 0
    print('')
    for (oneFile, saveFileName) in zip(fullFileUrl, fullFileName):
        current = current + 1
        progress = '已经完成' + str(int(current*100/fileNumber)) + '%'
        print('\r{}'.format(progress), end='')
        sys.stdout.flush()
        file = ses.get(oneFile)
        # if saveFileName[0] != '/':
        #     saveFileName = '/' + saveFileName
        saveDir = saveFileName.split('/')
        newFolder2 = newFolder
        for dir in saveDir:
            newFolder2 = os.path.join(newFolder2, dir)

        # saveFileName = '/' + newFolder + saveFileName
        with open(newFolder2, 'wb') as f:
            f.write(file.content)
    print('')
    print('下载完成')
