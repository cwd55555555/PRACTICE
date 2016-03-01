# coding=utf-8
#        ┏┓　　　┏┓+ +
# 　　　┏┛┻━━━┛┻┓ + +
# 　　　┃　　　　　　　┃ 　
# 　　　┃　　　━　　　┃ ++ + + +
# 　　 ████━████ ┃+
# 　　　┃　　　　　　　┃ +
# 　　　┃　　　┻　　　┃
# 　　　┃　　　　　　　┃ + +
# 　　　┗━┓　　　┏━┛
# 　　　　　┃　　　┃　　　　　　　　　　　
# 　　　　　┃　　　┃ + + + +
# 　　　　　┃　　　┃　　　　Codes are far away from bugs with the animal protecting　　　
# 　　　　　┃　　　┃ + 　　　　神兽保佑,代码无bug　　
# 　　　　　┃　　　┃
# 　　　　　┃　　　┃　　+　　　　　　　　　
# 　　　　　┃　 　　┗━━━┓ + +
# 　　　　　┃ 　　　　　　　┣┓
# 　　　　　┃ 　　　　　　　┏┛
# 　　　　　┗┓┓┏━┳┓┏┛ + + + +
# 　　　　　　┃┫┫　┃┫┫
# 　　　　　　┗┻┛　┗┻┛+ + + +
"""
Author = Eric_Chan
Create_Time = 2016/02/08
模拟登录邮箱系统,读取邮箱中的收件箱
input:广外邮箱的帐号和密码
return:收件箱中的详细内容
"""

import urllib
import urllib2
import cookielib
import re
from BeautifulSoup import BeautifulSoup


class Email_gdufs:
    header = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6)'
                            ' Gecko/20091201 Firefox/3.5.6'}
    user_accounts = ''  # 记录用户帐号(学号)
    user_name = ''  # 记录用户姓名
    user = ''  # 记录用户帐号
    pwd = ''  # 记录用户密码
    cookie = None
    sid = None
    mailBaseUrl = 'http://gdufs.edu.cn/'

    def __init__(self, user, pwd):
        self.cookie = cookielib.CookieJar()
        cookiePro = urllib2.HTTPCookieProcessor(self.cookie)
        urllib2.install_opener(urllib2.build_opener(cookiePro))
        self.user = user
        self.pwd = pwd

    def login(self):
        """
        登录学校邮箱
        :return:
        """
        user = self.user
        pwd = self.pwd
        header = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6)'
                                ' Gecko/20091201 Firefox/3.5.6'}
        post_data = urllib.urlencode({  # urllib 的 urlencode 方法将字典编码
                                        'user': user,
                                        'password': pwd,
                                        'locale': 'zh_CN',
                                        'face': '',
                                        'action:login': '',
                                        })
        # 注意版本不同，登录URL也不同
        req = urllib2.Request(  # 创建一个Request的实例,用来发出请求
                                url='http://gdufs.edu.cn/coremail/index.jsp',
                                data=post_data,
                                headers=header
                                )
        res = urllib2.urlopen(req)  # response 获得服务器的响应
        res_read = res.read()
        # print 'response \n', res_read, '\n------------------------------------------------------------------'

        pattern_sid = re.compile('.jsp\?sid=([^"]+)')  # 匹配返回结果是否有sid,若有则表明登录成功
        search_result = pattern_sid.search(res_read)  # re.search(pat,string) 等同于 pat.search(string)
        sid = search_result.group(1)

        pattern_user_name = re.compile('<span class="account">(.*)</span> &lt;\d+@gdufs\.edu\.cn&gt')  # 获得用户的姓名
        user_name = re.findall(pattern_user_name, res_read)
        if search_result:
            self.sid = sid
            self.user_name = user_name[0]
            print 'Login Successful.....'
            print "sid:", self.sid, "\nuser_name:", self.user_name
        else:
            print '%s Login failed....' % self.user_name

    def get_in_box(self):
        """
            获取邮箱列表
        """
        print 'Get mail lists.....\n'
        sid = self.sid
        page_no = 1
        page_max_no = None
        mail_list = []  # 保存邮件的url的列表
        while True:
            url = self.mailBaseUrl + '/coremail/XJS/mbox/list.jsp?sid=' + sid + '&fid=1&nav_type=system' + '&page_no=' + str(
                page_no)
            res = urllib2.urlopen(url).read()
            soup = BeautifulSoup(res)
            mail_html = soup.find('div', id='early_mbox').table.tbody.findAll('tr')  # 每条邮件对应的html列表
            if page_max_no is None:
                page_max_no = len(soup.find("div", attrs={'class': 'controls'})  # 收件箱的总页数
                                  .find("div", attrs={'class': 'fRight'}).find('select').findAll('option'))
            pattern_mail_url = re.compile('href="(.*?)"')
            for unit_mail_html in mail_html:
                mail_url = re.findall(pattern_mail_url, str(unit_mail_html))[0]
                mail_url = 'http://gdufs.edu.cn/coremail/XJS' + mail_url[2:]
                mail_url = mail_url.replace('&amp;', '&')
                mail_list.append(mail_url)
            page_no += 1
            if page_no > page_max_no:
                break

        return mail_list

    def get_mail_msg(self, url):
        """
        下载邮件的标题,发件人,时间,内容
        :param url: 邮件对应的url
        """
        return_email = {'time': '', 'title': '', 'from_email': '', 'from_name': '', 'content': '', 'url': url,
                        'mid': ''}
        # print '\n Download.....%s\n' % url
        res = urllib2.urlopen(url).read()
        soup = BeautifulSoup(res)
        # 获取邮件的mid
        pattern_mid_url = re.compile('mid=(.*?)&')
        mid = re.findall(pattern_mid_url, url)[0]
        return_email['mid'] = mid
        # 获取邮件标题
        title = str(soup.find("div", id='body_area').find("div", attrs={'class': 'gRead-info bg-cont'}).h2)
        title = re.sub('<.*?>', '', title)
        return_email['title'] = title
        # 获取邮件发件人的邮箱地址和发件名
        from_mail = str(soup.find("div", id='body_area').find('input', attrs={'name': 'from_mail'}))
        from_mail = re.findall('value="(.*?)"', from_mail)[0]
        return_email['from_email'] = from_mail
        from_name = str(soup.find("div", id='body_area').find('input', attrs={'name': 'from_name'}))
        from_name = re.findall('value="(.*?)"', from_name)[0]
        return_email['from_name'] = from_name
        # 获取邮件的发送时间
        send_time = str(
            soup.find("div", id='body_area').find('div', id='full_details').findAll("table", attrs={'class': 'stlr '})[
                1].tbody.tr.td)
        send_time = re.sub('<.*?>', '', send_time)
        return_email['time'] = send_time
        # 获取邮件内容
        pattern_mail_content_url = re.compile(
            'iframe name="mail_content" id="mail_content"  frameborder="0"  src="(.*)"')
        mail_content_url = 'http://gdufs.edu.cn/coremail/XJS/' + \
                           re.findall(pattern_mail_content_url, res)[0][2:]  # 邮件的内容的url
        res_content = urllib2.urlopen(mail_content_url).read()
        pattern_content = re.compile('<[Pp].*?>(.*?)</[Pp]r?e?>', re.S)  # 点任意匹配模式
        content = re.findall(pattern_content, res_content)
        new_content = ''
        for row in content:
            row = re.sub('<.*?>', '', row)
            row = row.replace('&nbsp;', ' ')
            new_content += row + '\n'
        return_email['content'] = new_content
        return return_email

    def get_emails(self):
        self.login()
        mail_list = self.get_in_box()
        emails = []
        for unit_mail in mail_list:
            emails.append(self.get_mail_msg(unit_mail))
        return emails

# if __name__ == '__main__':
#     emails = Email_gdufs('2014100', '266095').get_emails()
#     for email in emails:
#         print '******************************************************************************************'
#         print '标 题:', email['title']
#         print '发件人:', email['from_email'], email['from_name']
#         print '时 间:', email['time']
#         print '\n', email['content']
#         print '\n原邮件地址:\n', email['url']
#         print email['mid']2516
